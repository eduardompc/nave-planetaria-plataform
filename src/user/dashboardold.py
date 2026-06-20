from dash import html, dcc
from dash.dependencies import Input, Output
from src.auth.session import get_current_profile
from src.missions.mission_engine import list_user_missions
from src.api.telemetry import get_all_telemetry
from src.telemetry.analyzer import compute_stats
from src.ai.events import on_mission_tab_open


def layout_user_dashboard():
    profile = get_current_profile()

    if not profile:
        return html.Div("Nenhum usuário autenticado.")

    return html.Div([
        html.H2(f"Painel do Piloto — {profile['rank']}"),
        html.P(f"XP: {profile['xp']}"),
        html.P(f"Tema preferido: {profile['theme']}"),

        dcc.Tabs(id="user-dashboard-tabs", value="tab-profile", children=[
            dcc.Tab(label="Perfil", value="tab-profile"),
            dcc.Tab(label="Missões", value="tab-missions"),
            dcc.Tab(label="Estatísticas", value="tab-stats"),
            dcc.Tab(label="Configurações", value="tab-settings"),
        ]),
        html.Div(id="user-dashboard-content")
    ])

def register_dashboard_callbacks(app):

    @app.callback(
        Output("user-dashboard-content", "children"),
        Input("user-dashboard-tabs", "value")
    )
    def render_tab(tab):
        profile = get_current_profile()
        if not profile:
            return html.Div("Sessão expirada. Faça login novamente.")

        if tab == "tab-profile":
            return _tab_profile(profile)
        if tab == "tab-missions":
            return _tab_missions(profile)
        if tab == "tab-stats":
            return _tab_stats(profile)
        if tab == "tab-settings":
            return _tab_settings(profile)

        return html.Div("Aba desconhecida.")

def _tab_profile(profile):
    return html.Div([
        html.H3("Perfil do Piloto"),
        html.P(f"Rank: {profile['rank']}"),
        html.P(f"XP: {profile['xp']}"),
        html.P(f"Tema: {profile['theme']}"),
        html.P(f"Último login: {profile['last_login']}")
    ])

def _tab_missions(profile):
    missions = list_user_missions(profile["user_id"])
    if not missions:
        return html.Div("Nenhuma missão ativa no momento.")

    return html.Div([
        html.H3("Missões Ativas"),
        html.Ul([
            html.Li(f"{m['name']} — {m['progress']}% ({m['status']})")
            for m in missions
        ])
    ])

if tab == "tab-missions":
    briefing = on_mission_tab_open()
    return html.Div([
        html.H3("Missões Ativas"),
        html.Ul([html.Li(msg) for msg in briefing]),
        html.Hr(),
        html.Ul([
            html.Li(f"{m['name']} — {m['progress']}% ({m['status']})")
            for m in missions
        ])
    ])

def _tab_stats(profile):
    rows = get_all_telemetry(profile["user_id"])
    stats = compute_stats(rows)

    return html.Div([
        html.H3("Estatísticas de Voo"),
        html.P(f"Pontos de telemetria: {stats['total_points']}"),
        html.P(f"Altitude média: {stats['avg_altitude']} km"),
        html.P(f"Velocidade média: {stats['avg_velocity']} km/h")
    ])

def _tab_settings(profile):
    return html.Div([
        html.H3("Configurações"),
        html.P("Aqui você poderá ajustar tema, idioma e preferências futuras.")
    ])
