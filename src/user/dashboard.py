import json
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objects as go
import random

from src.api.db import get_connection
from src.auth.session import get_current_profile
from src.api.astronomy import (
    get_all_celestial_objects,
    get_observed_object_ids,
    record_observation,
    reset_user_observations,
    get_celestial_object_by_name
)
from src.api.telemetry import get_last_points
from src.ai.core import generate_ai_briefing
from src.ai.agent import run_gemini_agent
from src.api.ai_memory import add_ai_memory, get_ai_memory
from src.missions.mission_definitions import MISSIONS_CATALOG
from src.missions.mission_engine import list_user_missions, complete_mission, assign_mission
from src.api.logs import get_recent_logs, add_log


# ---------------------------------------------------------
# LAYOUT PRINCIPAL DO DASHBOARD
# ---------------------------------------------------------

def layout_user_dashboard():
    profile = get_current_profile()
    if not profile:
        return html.Div("Nenhum usuário autenticado. Redirecionando...", style={"color": "#f87171"})

    # Layout estruturado em grade SaaS com Top Bar
    return html.Div(
        className="dashboard-container fade-in",
        children=[
            # Top Stats Bar
            html.Div(
                className="top-bar",
                children=[
                    html.Div("SaaS Antigravity Space", className="top-bar-title"),
                    html.Div(
                        className="top-bar-stats",
                        id="dashboard-top-stats"
                    )
                ]
            ),

            # Main Layout Area (Sidebar + Content)
            html.Div(
                className="main-layout",
                children=[
                    # Sidebar de Navegação
                    html.Div(
                        className="sidebar",
                        children=[
                            html.H3("Navegação", style={"fontFamily": "Orbitron", "fontSize": "1.1rem", "color": "#818cf8"}),
                            dcc.Tabs(
                                id="user-dashboard-tabs",
                                value="tab-cockpit",
                                vertical=True,
                                parent_className="custom-tabs-container",
                                className="custom-tabs",
                                children=[
                                    dcc.Tab(label="Cockpit & Co-Pilot", value="tab-cockpit", className="custom-tab", selected_className="custom-tab--selected"),
                                    dcc.Tab(label="Visualizador 3D", value="tab-sky", className="custom-tab", selected_className="custom-tab--selected"),
                                    dcc.Tab(label="Catálogo Estelar", value="tab-catalog", className="custom-tab", selected_className="custom-tab--selected"),
                                    dcc.Tab(label="Missões Acadêmicas", value="tab-missions", className="custom-tab", selected_className="custom-tab--selected"),
                                    dcc.Tab(label="Configurações", value="tab-settings", className="custom-tab", selected_className="custom-tab--selected"),
                                ]
                            )
                        ]
                    ),

                    # Área de Conteúdo Dinâmico
                    html.Div(
                        className="content-area",
                        id="user-dashboard-content"
                    )
                ]
            ),
            dcc.Interval(id="stats-refresh-interval", interval=2500, n_intervals=0)
        ]
    )


# ---------------------------------------------------------
# RENDERIZAÇÃO DAS ABAS
# ---------------------------------------------------------

def _tab_cockpit(profile):
    user_id = profile["user_id"]
    telemetry_points = get_last_points(user_id, limit=30)
    
    # Coordenadas da ISS mais recentes ou fallback
    latest_lat = 0.0
    latest_lon = 0.0
    latest_alt = 408.0
    latest_vel = 27600.0
    
    if telemetry_points:
        latest = telemetry_points[0]
        latest_lat = latest["lat"]
        latest_lon = latest["lon"]
        latest_alt = round(latest["altitude"], 2)
        latest_vel = round(latest["velocity"], 2)

    # Gráfico de Telemetria Orbital 2D (ISS Trajectory)
    trajectory_fig = go.Figure()
    if telemetry_points:
        lats = [pt["lat"] for pt in telemetry_points]
        lons = [pt["lon"] for pt in telemetry_points]
        trajectory_fig.add_trace(go.Scatter(
            x=lons, y=lats,
            mode='lines+markers',
            name='Rastro Orbital',
            line=dict(color='#818cf8', width=2),
            marker=dict(size=6, color='#a78bfa')
        ))
    trajectory_fig.update_layout(
        title="Rastreamento da Rota de Voo (Coordenadas ISS)",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        xaxis=dict(range=[-180, 180], gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(range=[-90, 90], gridcolor="rgba(255,255,255,0.05)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        margin=dict(l=40, r=20, t=40, b=40)
    )

    # AI Briefing
    briefing = generate_ai_briefing()

    return html.Div(
        className="fade-in",
        children=[
            html.H2("Painel do Cockpit & Co-Piloto", style={"fontFamily": "Orbitron", "marginBottom": "24px"}),

            html.Div(
                className="dashboard-grid",
                children=[
                    # Coluna da esquerda: Status e Telemetria
                    html.Div(
                        children=[
                            # Status Grid
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "16px", "marginBottom": "24px"},
                                children=[
                                    html.Div(
                                        className="glass-panel",
                                        children=[
                                            html.H4("Altitude da Nave", style={"color": "#94a3b8", "fontSize": "0.85rem", "marginBottom": "8px"}),
                                            html.Div(f"{latest_alt} km", style={"fontFamily": "Orbitron", "fontSize": "1.6rem", "fontWeight": "700", "color": "#38bdf8"})
                                        ]
                                    ),
                                    html.Div(
                                        className="glass-panel",
                                        children=[
                                            html.H4("Velocidade Relativa", style={"color": "#94a3b8", "fontSize": "0.85rem", "marginBottom": "8px"}),
                                            html.Div(f"{latest_vel} km/h", style={"fontFamily": "Orbitron", "fontSize": "1.6rem", "fontWeight": "700", "color": "#fbbf24"})
                                        ]
                                    ),
                                    html.Div(
                                        className="glass-panel",
                                        children=[
                                            html.H4("Coordenadas ISS", style={"color": "#94a3b8", "fontSize": "0.85rem", "marginBottom": "8px"}),
                                            html.Div(f"{round(latest_lat, 2)}°, {round(latest_lon, 2)}°", style={"fontFamily": "Orbitron", "fontSize": "1.2rem", "fontWeight": "700", "color": "#4ade80"})
                                        ]
                                    )
                                ]
                            ),

                            # Gráfico orbital
                            html.Div(
                                className="glass-panel",
                                children=[
                                    dcc.Graph(figure=trajectory_fig, className="star-map-graph", config={"displayModeBar": False})
                                ]
                            )
                        ]
                    ),

                    # Coluna da direita: Co-Pilot IA & Chat
                    html.Div(
                        className="glass-panel ai-copilot-container",
                        children=[
                            html.H3("IA Co-Piloto Científico", style={"fontFamily": "Orbitron", "color": "#818cf8", "marginBottom": "16px"}),
                            
                            # Real-time briefing list
                            html.Ul(
                                className="ai-message-list",
                                children=[html.Li(msg, className="ai-message-item") for msg in briefing]
                            ),
                            
                            html.Hr(style={"border": "0", "borderTop": "1px solid rgba(255,255,255,0.08)", "margin": "20px 0"}),
                            
                            # Chat com co-piloto
                            html.H4("Consulta Espacial Rápida", style={"fontSize": "0.95rem", "color": "#cbd5e1", "marginBottom": "8px"}),
                            dcc.Input(
                                id="ai-chat-input",
                                placeholder="Pergunte sobre estrelas, planetas ou manobras...",
                                type="text",
                                style={"width": "100%", "marginBottom": "12px"}
                            ),
                            html.Button("Consultar Sistemas", id="ai-chat-submit", style={"width": "100%"}),
                            
                            html.Div(
                                id="ai-chat-response-area",
                                style={"marginTop": "16px", "padding": "12px", "background": "rgba(255,255,255,0.02)", "borderRadius": "8px", "border": "1px solid rgba(255,255,255,0.05)", "fontSize": "0.85rem", "lineHeight": "1.4", "color": "#a78bfa"}
                            )
                        ]
                    )
                ]
            )
        ]
    )


def _tab_sky(profile):
    objects = get_all_celestial_objects()
    observed_ids = get_observed_object_ids(profile["user_id"])

    # Listas para guardar coordenadas de estrelas e planetas
    p_x, p_y, p_z, p_names, p_text = [], [], [], [], []
    s_x, s_y, s_z, s_names, s_text = [], [], [], [], []

    for obj in objects:
        coords = json.loads(obj["coordinates_json"])
        x, y, z = coords["x"], coords["y"], coords["z"]
        
        status = "Observado ✓" if obj["id"] in observed_ids else "Não observado 👁"
        desc = f"<b>{obj['name']}</b> ({obj['type']})<br>Constelação: {obj['constellation']}<br>Distância: {obj['distance_ly']} AL<br>Brilho (Mag): {obj['magnitude']}<br>{status}"

        if obj["type"] == "planet":
            p_x.append(x)
            p_y.append(y)
            p_z.append(z)
            p_names.append(obj["name"])
            p_text.append(desc)
        else:
            s_x.append(x)
            s_y.append(y)
            s_z.append(z)
            s_names.append(obj["name"])
            s_text.append(desc)

    # Cria gráfico 3D
    fig = go.Figure()

    # Planetas (tamanho maior, cores vibrantes)
    fig.add_trace(go.Scatter3d(
        x=p_x, y=p_y, z=p_z,
        mode='markers+text',
        name='Sistema Solar',
        text=p_names,
        textposition="top center",
        hovertext=p_text,
        hoverinfo='text',
        customdata=p_names,
        marker=dict(
            size=10,
            color='#6366f1',
            opacity=0.9,
            line=dict(color='rgba(255,255,255,0.5)', width=1)
        )
    ))

    # Estrelas (tamanho menor, cor brilhante)
    fig.add_trace(go.Scatter3d(
        x=s_x, y=s_y, z=s_z,
        mode='markers',
        name='Estrelas',
        hovertext=s_text,
        hoverinfo='text',
        customdata=s_names,
        marker=dict(
            size=5,
            color='#ffffff',
            opacity=0.8,
            symbol='circle'
        )
    ))

    # Layout do espaço 3D (ocultando eixos)
    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="", backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="", backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="", backgroundcolor="rgba(0,0,0,0)"),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=1)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        legend=dict(x=0.05, y=0.95, bgcolor="rgba(10,10,30,0.6)"),
        clickmode="event+select"
    )

    return html.Div(
        className="fade-in",
        children=[
            html.H2("Visualizador Celeste 3D", style={"fontFamily": "Orbitron", "marginBottom": "8px"}),
            html.P("Use o mouse para rotacionar, aproximar e selecionar astros no mapa espacial interativo.", style={"color": "#94a3b8", "marginBottom": "24px"}),

            html.Div(
                className="dashboard-grid",
                children=[
                    # Gráfico 3D
                    html.Div(
                        className="glass-panel",
                        children=[
                            dcc.Graph(
                                id="sky-graph",
                                figure=fig,
                                className="star-map-graph",
                                style={"height": "550px"},
                                config={"scrollZoom": True, "displayModeBar": False}
                            )
                        ]
                    ),

                    # Card de Detalhes
                    html.Div(
                        className="glass-panel detail-panel",
                        id="sky-detail-container",
                        children=[
                            html.H3("Análise Espectroscópica", style={"fontFamily": "Orbitron", "color": "#818cf8"}),
                            html.P("Clique em qualquer astro no mapa espacial 3D para obter sua leitura científica, distância e magnitude.", style={"color": "#94a3b8", "fontSize": "0.95rem"})
                        ]
                    )
                ]
            )
        ]
    )


def _tab_catalog(profile, search_query="", category_filter="all"):
    objects = get_all_celestial_objects()
    observed_ids = get_observed_object_ids(profile["user_id"])

    # Filtros
    filtered = []
    for obj in objects:
        # Busca
        if search_query and search_query.lower() not in obj["name"].lower() and search_query.lower() not in obj["constellation"].lower():
            continue
        # Categoria
        if category_filter == "stars" and obj["type"] != "star":
            continue
        if category_filter == "planets" and obj["type"] != "planet":
            continue
        filtered.append(obj)

    # Constrói cards
    cards = []
    for obj in filtered:
        is_observed = obj["id"] in observed_ids
        
        obs_element = html.Div(
            className="badge-observed",
            children=[
                html.Span("✓"),
                html.Span("Observado")
            ]
        ) if is_observed else html.Button(
            "Marcar Observado (+50 XP)",
            id={"type": "btn-observe-catalog", "index": obj["id"]},
            style={"padding": "8px 16px", "fontSize": "0.85rem", "width": "100%"}
        )

        badge_type = html.Span(
            "Planeta" if obj["type"] == "planet" else "Estrela",
            className="detail-type",
            style={"marginLeft": "10px", "fontSize": "0.7rem"}
        )

        cards.append(
            html.Div(
                className="catalog-card glass-panel",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                className="catalog-card-header",
                                children=[
                                    html.Span(obj["name"], className="catalog-card-title"),
                                    badge_type
                                ]
                            ),
                            html.Div(
                                className="catalog-card-meta",
                                children=[
                                    html.P(f"Constelação: {obj['constellation']}"),
                                    html.P(f"Distância: {obj['distance_ly']} AL"),
                                    html.P(f"Magnitude: {obj['magnitude']}")
                                ]
                            ),
                            html.P(obj["description"], className="catalog-card-desc"),
                        ]
                    ),
                    html.Div(
                        children=[obs_element],
                        style={"marginTop": "15px"}
                    )
                ]
            )
        )

    # Elemento de filtro
    filter_controls = html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "24px", "gap": "16px", "flexWrap": "wrap"},
        children=[
            # Barra de busca
            dcc.Input(
                id={"type": "catalog-search", "index": "global"},
                placeholder="Pesquise por nome ou constelação...",
                type="text",
                value=search_query,
                style={"flex": "1", "minWidth": "250px"}
            ),
            
            # Filtro por tipo
            dcc.RadioItems(
                id={"type": "catalog-filter", "index": "global"},
                options=[
                    {"label": "Todos", "value": "all"},
                    {"label": "Estrelas", "value": "stars"},
                    {"label": "Planetas", "value": "planets"},
                ],
                value=category_filter,
                inline=True,
                style={"display": "flex", "gap": "12px", "color": "#94a3b8", "fontSize": "0.95rem"},
                labelStyle={"cursor": "pointer", "display": "flex", "alignItems": "center", "gap": "6px"}
            )
        ]
    )

    return html.Div(
        className="fade-in",
        children=[
            html.H2("Catálogo Científico de Astros", style={"fontFamily": "Orbitron", "marginBottom": "8px"}),
            html.P("Consulte informações detalhadas sobre planetas e estrelas. Registre observações para evoluir sua patente militar.", style={"color": "#94a3b8", "marginBottom": "24px"}),
            filter_controls,
            html.Div(
                className="catalog-grid",
                children=cards if cards else [html.Div("Nenhum astro correspondente encontrado.", style={"color": "#94a3b8", "gridColumn": "1/-1", "textAlign": "center", "padding": "40px"})]
            )
        ]
    )


def _tab_missions(profile):
    user_id = profile["user_id"]
    active_missions = list_user_missions(user_id)

    # Divide catálogo em disponíveis e ativas
    active_codes = [m["name"] for m in active_missions]
    
    # Renderiza missões disponíveis para aceitar
    available_cards = []
    for m in MISSIONS_CATALOG:
        is_active = any(m["name"] in ac for ac in active_codes)
        
        action_button = html.Button(
            "Missão em Progresso",
            disabled=True,
            style={"background": "rgba(255,255,255,0.05)", "color": "#64748b", "boxShadow": "none", "cursor": "default"}
        ) if is_active else html.Button(
            "Iniciar Missão",
            id={"type": "btn-assign-mission", "index": m["code"]},
            style={"width": "100%"}
        )

        available_cards.append(
            html.Div(
                className="glass-panel",
                style={"display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                children=[
                    html.Div([
                        html.H4(m["name"], style={"fontFamily": "Orbitron", "color": "#f1f5f9", "marginBottom": "8px"}),
                        html.P(m["description"], style={"color": "#94a3b8", "fontSize": "0.85rem", "marginBottom": "16px"}),
                        html.P(f"Recompensa: +{m['xp_reward']} XP", style={"color": "#38bdf8", "fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "16px"}),
                    ]),
                    action_button
                ]
            )
        )

    # Renderiza missões em progresso
    progress_cards = []
    for m in active_missions:
        m_code = ""
        for item in MISSIONS_CATALOG:
            if item["name"] == m["name"]:
                m_code = item["code"]
                break

        progress_cards.append(
            html.Div(
                className="glass-panel",
                style={"borderLeft": "3px solid #fbbf24", "marginBottom": "12px", "display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                children=[
                    html.Div([
                        html.H4(m["name"], style={"fontFamily": "Orbitron", "color": "#fbbf24", "marginBottom": "4px"}),
                        html.P(f"Progresso orbital: {m['progress']}%", style={"color": "#94a3b8", "fontSize": "0.85rem"})
                    ]),
                    html.Button(
                        "Simular Telemetria & Concluir",
                        id={"type": "btn-complete-mission", "index": f"{m['id']}|{m_code}"},
                        style={"background": "linear-gradient(135deg, #fbbf24 0%, #d97706 100%)", "boxShadow": "0 4px 15px rgba(217, 119, 6, 0.3)"}
                    )
                ]
            )
        )

    return html.Div(
        className="fade-in",
        children=[
            html.H2("Centro de Treinamento e Missões", style={"fontFamily": "Orbitron", "marginBottom": "8px"}),
            html.P("Inicie simulações e complete missões de exploração orbital para receber patentes mais elevadas.", style={"color": "#94a3b8", "marginBottom": "24px"}),

            html.H3("Missões Ativas no Setor", style={"fontFamily": "Orbitron", "color": "#fbbf24", "fontSize": "1.2rem", "marginBottom": "16px"}),
            html.Div(
                children=progress_cards if progress_cards else [html.Div("Nenhuma missão ativa. Selecione uma missão de treinamento abaixo.", style={"color": "#94a3b8", "padding": "24px", "background": "rgba(255,255,255,0.01)", "borderRadius": "8px"})],
                style={"marginBottom": "36px"}
            ),

            html.H3("Catálogo de Missões Disponíveis", style={"fontFamily": "Orbitron", "color": "#818cf8", "fontSize": "1.2rem", "marginBottom": "16px"}),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))", "gap": "20px"},
                children=available_cards
            )
        ]
    )


def _tab_settings(profile):
    return html.Div(
        className="glass-panel fade-in",
        style={"maxWidth": "600px", "margin": "auto"},
        children=[
            html.H2("Configurações do SaaS", style={"fontFamily": "Orbitron", "marginBottom": "20px", "textAlign": "center"}),
            
            html.Div(
                className="info-list",
                style={"marginBottom": "24px"},
                children=[
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Patente Atual", className="info-item-label"),
                            html.Span(profile["rank"], className="info-item-value")
                        ]
                    ),
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Pontuação Total (XP)", className="info-item-label"),
                            html.Span(f"{profile['xp']} XP", className="info-item-value")
                        ]
                    ),
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Preferencia de Tema", className="info-item-label"),
                            html.Span(profile["theme"].upper(), className="info-item-value")
                        ]
                    ),
                ]
            ),
            
            html.Hr(style={"border": "0", "borderTop": "1px solid rgba(255,255,255,0.08)", "marginBottom": "24px"}),

            html.H4("Área de Risco", style={"color": "#f87171", "marginBottom": "8px"}),
            html.P("Esta ação irá deletar todas as observações registradas no seu histórico e resetar seu XP de piloto ao valor inicial de segurança.", style={"color": "#94a3b8", "fontSize": "0.85rem", "marginBottom": "16px"}),
            html.Button(
                "Resetar Histórico de Observações",
                id={"type": "btn-reset-obs", "index": "global"},
                style={"background": "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)", "boxShadow": "0 4px 15px rgba(239, 68, 68, 0.3)", "width": "100%"}
            ),
            html.Div(id="reset-feedback-msg", style={"marginTop": "12px", "textAlign": "center", "fontSize": "0.9rem", "color": "#4ade80"})
        ]
    )


# ---------------------------------------------------------
# REGISTRO DE CALLBACKS DO DASHBOARD (CONSOLIDADO E ROBUSTO)
# ---------------------------------------------------------

def register_dashboard_callbacks(app):

    # CALLBACK CENTRAL: Renderiza a aba atual e processa todas as ações e filtros em uma única via estrutural
    @app.callback(
        Output("user-dashboard-content", "children"),
        [
            Input("user-dashboard-tabs", "value"),
            Input({"type": "btn-observe-catalog", "index": ALL}, "n_clicks"),
            Input({"type": "btn-observe-sky", "index": ALL}, "n_clicks"),
            Input({"type": "btn-assign-mission", "index": ALL}, "n_clicks"),
            Input({"type": "btn-complete-mission", "index": ALL}, "n_clicks"),
            Input({"type": "btn-reset-obs", "index": ALL}, "n_clicks"),
            Input({"type": "catalog-search", "index": ALL}, "value"),
            Input({"type": "catalog-filter", "index": ALL}, "value")
        ]
    )
    def render_tab_and_process_actions(tab, n_obs_cat, n_obs_sky, n_assign, n_complete, n_reset, search_vals, filter_vals):
        profile = get_current_profile()
        if not profile:
            return html.Div("Sessão expirada. Faça login novamente.", style={"color": "#f87171"})

        # Extrai busca e categoria (pattern matching)
        search_query = search_vals[0] if search_vals else ""
        category_filter = filter_vals[0] if filter_vals else "all"

        ctx = callback_context
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"]
            
            # 1. Observar via Catálogo
            if "btn-observe-catalog" in trigger_id and "index" in trigger_id:
                try:
                    cleaned_prop = trigger_id.split(".n_clicks")[0]
                    trigger_data = json.loads(cleaned_prop)
                    obj_id = trigger_data["index"]
                    # Verifica se o click ocorreu de fato (evita disparos nulos no carregamento)
                    clicks_list = [c for c in n_obs_cat if c is not None]
                    if clicks_list and any(c > 0 for c in clicks_list):
                        record_observation(profile["user_id"], obj_id)
                except Exception as e:
                    print("Erro no callback central (observe catalog):", e)
                    
            # 2. Observar via Sky Map 3D
            elif "btn-observe-sky" in trigger_id and "index" in trigger_id:
                try:
                    cleaned_prop = trigger_id.split(".n_clicks")[0]
                    trigger_data = json.loads(cleaned_prop)
                    obj_id = trigger_data["index"]
                    clicks_list = [c for c in n_obs_sky if c is not None]
                    if clicks_list and any(c > 0 for c in clicks_list):
                        record_observation(profile["user_id"], obj_id)
                except Exception as e:
                    print("Erro no callback central (observe sky):", e)
                    
            # 3. Aceitar Missão
            elif "btn-assign-mission" in trigger_id and "index" in trigger_id:
                try:
                    cleaned_prop = trigger_id.split(".n_clicks")[0]
                    trigger_data = json.loads(cleaned_prop)
                    m_code = trigger_data["index"]
                    clicks_list = [c for c in n_assign if c is not None]
                    if clicks_list and any(c > 0 for c in clicks_list):
                        assign_mission(profile["user_id"], m_code)
                        add_log(profile["user_id"], f"Missão de treino '{m_code}' aceita.", "info")
                except Exception as e:
                    print("Erro no callback central (assign mission):", e)
                    
            # 4. Concluir Missão
            elif "btn-complete-mission" in trigger_id and "index" in trigger_id:
                try:
                    cleaned_prop = trigger_id.split(".n_clicks")[0]
                    trigger_data = json.loads(cleaned_prop)
                    index_val = trigger_data["index"]
                    m_id_str, m_code = index_val.split("|")
                    clicks_list = [c for c in n_complete if c is not None]
                    if clicks_list and any(c > 0 for c in clicks_list):
                        complete_mission(profile["user_id"], int(m_id_str), m_code)
                        add_log(profile["user_id"], f"Missão '{m_code}' concluída.", "info")
                except Exception as e:
                    print("Erro no callback central (complete mission):", e)
                    
            # 5. Resetar Histórico
            elif "btn-reset-obs" in trigger_id:
                try:
                    clicks_list = [c for c in n_reset if c is not None]
                    if clicks_list and any(c > 0 for c in clicks_list):
                        reset_user_observations(profile["user_id"])
                except Exception as e:
                    print("Erro no callback central (reset):", e)

        # Retorna o layout correspondente com dados atualizados do banco
        if tab == "tab-cockpit":
            return _tab_cockpit(profile)
        elif tab == "tab-sky":
            return _tab_sky(profile)
        elif tab == "tab-catalog":
            return _tab_catalog(profile, search_query=search_query, category_filter=category_filter)
        elif tab == "tab-missions":
            return _tab_missions(profile)
        elif tab == "tab-settings":
            return _tab_settings(profile)

        return html.Div("Aba desconhecida.", style={"color": "#f87171"})

    # 2) Callback para atualizar o Top Stats Bar em tempo real
    @app.callback(
        Output("dashboard-top-stats", "children"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_top_stats(n):
        profile = get_current_profile()
        if not profile:
            return []

        observed_count = len(get_observed_object_ids(profile["user_id"]))

        return [
            html.Div([
                html.Span("PILOTO: ", style={"color": "#94a3b8"}),
                html.Span(profile["rank"], style={"color": "#818cf8", "fontWeight": "700"})
            ], className="stat-pill stat-pill-highlight"),
            html.Div([
                html.Span("EXPERIÊNCIA: ", style={"color": "#94a3b8"}),
                html.Span(f"{profile['xp']} XP", style={"color": "#fbbf24", "fontWeight": "700"})
            ], className="stat-pill"),
            html.Div([
                html.Span("OBSERVAÇÕES: ", style={"color": "#94a3b8"}),
                html.Span(f"{observed_count} astros", style={"color": "#4ade80", "fontWeight": "700"})
            ], className="stat-pill"),
            html.Button(
                "Sair", 
                id="btn-logout",
                style={"padding": "6px 14px", "fontSize": "0.85rem", "background": "rgba(255,255,255,0.05)", "color": "#cbd5e1", "boxShadow": "none", "border": "1px solid rgba(255,255,255,0.1)"}
            )
        ]

    # 3) Callback para clique no Sky Map (Exibir Detalhes do Astro)
    @app.callback(
        Output("sky-detail-container", "children"),
        Input("sky-graph", "clickData")
    )
    def display_sky_details(clickData):
        if not clickData or "points" not in clickData:
            return [
                html.H3("Análise Espectroscópica", style={"fontFamily": "Orbitron", "color": "#818cf8"}),
                html.P("Clique em qualquer astro no mapa espacial 3D para obter sua leitura científica, distância e magnitude.", style={"color": "#94a3b8", "fontSize": "0.95rem"})
            ]

        profile = get_current_profile()
        if not profile:
            return html.Div("Faça login para realizar análises.", style={"color": "#f87171"})

        # Busca o nome do astro clicado através do customdata
        obj_name = clickData["points"][0].get("customdata", "")
        if not obj_name:
            return html.Div("Astro desconhecido.")

        obj = get_celestial_object_by_name(obj_name)
        if not obj:
            return html.Div(f"Astro '{obj_name}' não encontrado no catálogo.")

        observed_ids = get_observed_object_ids(profile["user_id"])
        is_observed = obj["id"] in observed_ids

        # Botão de observação
        obs_btn = html.Div(
            className="badge-observed",
            children=[html.Span("✓"), html.Span("Observado no Diário de Bordo")],
            style={"marginTop": "16px"}
        ) if is_observed else html.Button(
            "Registrar no Diário de Bordo (+50 XP)",
            id={"type": "btn-observe-sky", "index": obj["id"]},
            style={"marginTop": "16px", "width": "100%"}
        )

        return [
            html.Div(
                className="detail-header",
                children=[
                    html.Span(obj["name"], className="detail-title"),
                    html.Span("Planeta" if obj["type"] == "planet" else "Estrela", className="detail-type")
                ]
            ),
            html.Div(
                className="info-list",
                style={"marginTop": "12px", "marginBottom": "12px"},
                children=[
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Constelação", className="info-item-label"),
                            html.Span(obj["constellation"], className="info-item-value")
                        ]
                    ),
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Distância", className="info-item-label"),
                            html.Span(f"{obj['distance_ly']} Anos-luz", className="info-item-value")
                        ]
                    ),
                    html.Div(
                        className="info-item",
                        children=[
                            html.Span("Magnitude Aparente", className="info-item-label"),
                            html.Span(f"{obj['magnitude']}", className="info-item-value")
                        ]
                    )
                ]
            ),
            html.P(obj["description"], className="detail-desc"),
            obs_btn
        ]

    # 4) Callback do chat do co-piloto científico
    @app.callback(
        Output("ai-chat-response-area", "children"),
        Input("ai-chat-submit", "n_clicks"),
        State("ai-chat-input", "value"),
        prevent_initial_call=True
    )
    def process_ai_chat(n_clicks, user_message):
        profile = get_current_profile()
        if not profile or not user_message:
            return ""

        add_ai_memory(profile["user_id"], f"Usuário: {user_message}")

        # Executa o agente Gemini inteligente integrado com Function Calling
        response = run_gemini_agent(user_message, profile["user_id"])

        add_ai_memory(profile["user_id"], f"IA: {response}")
        return response

    # 5) Callback para deslogar do painel
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("btn-logout", "n_clicks"),
        prevent_initial_call=True
    )
    def logout_process(n_clicks):
        if not n_clicks:
            from dash import no_update
            return no_update

        from flask_login import logout_user
        logout_user()
        return "/login"
