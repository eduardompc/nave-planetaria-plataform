from flask import Flask
from flask_login import LoginManager, current_user
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from src.auth.login_manager import login_manager
from src.auth.routes import layout_login, register_callbacks
from src.auth.session import get_current_profile
from src.user.dashboard import register_dashboard_callbacks
from src.telemetry.recorder import record_tick
from src.ai.events import on_cockpit_open

# ---------------------------------------------------------
# FLASK SERVER + LOGIN
# ---------------------------------------------------------

server = Flask(__name__)
server.secret_key = "CHAVE-SECRETA-DA-NAVE"

login_manager.init_app(server)

# ---------------------------------------------------------
# DASH APP
# ---------------------------------------------------------

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=False
)

register_callbacks(app)
#register_dashboard_callbacks(app)

# ---------------------------------------------------------
# LAYOUT PRINCIPAL
# ---------------------------------------------------------

app.layout = html.Div([
    dcc.Location(id="url"),

    # Conteúdo da página
    html.Div(id="page-content"),

    # IA e telemetria
    html.Div(id="ia-output"),
    html.Div(id="dummy-output"),

    # Intervalo global
    dcc.Interval(id="intervalo", interval=2000, n_intervals=0)
])

# ---------------------------------------------------------
# PROTEÇÃO DE ROTAS FLASK
# ---------------------------------------------------------

@app.server.before_request
def protect_routes():
    from flask import request, redirect

    protected_paths = ["/cockpit"]

    if request.path in protected_paths and not current_user.is_authenticated:
        return redirect("/login")

# ---------------------------------------------------------
# COCKPIT COM IA
# ---------------------------------------------------------

def layout_cockpit():
    profile = get_current_profile() or {}

    rank = profile.get("rank", "Comandante")
    xp = profile.get("xp", 0)
    theme = profile.get("theme", "auto")
    last_login = profile.get("last_login", "Primeiro acesso")

    briefing = on_cockpit_open()

    return html.Div([
        html.H1(f"Cockpit — {rank}"),
        html.P(f"XP: {xp}"),
        html.P(f"Tema: {theme}"),
        html.P(f"Último login: {last_login}"),

        html.H3("Briefing da IA"),
        html.Ul([html.Li(msg) for msg in briefing])
    ])

# ---------------------------------------------------------
# CALLBACK PRINCIPAL DE NAVEGAÇÃO
# ---------------------------------------------------------

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):

    if pathname is None:
        return layout_login()

    if pathname == "/login":
        return layout_login()

    if pathname == "/cockpit":
        profile = get_current_profile()
        if not profile:
            return layout_login()
        return layout_cockpit()

    # Rota padrão
    return layout_login()

# ---------------------------------------------------------
# CALLBACK DE TELEMETRIA
# ---------------------------------------------------------

@app.callback(
    Output("dummy-output", "children"),
    Input("intervalo", "n_intervals")
)
def tick(n):
    record_tick()
    return ""

# ---------------------------------------------------------
# CALLBACK DA IA EM TEMPO REAL
# ---------------------------------------------------------

from src.ai.core import generate_ai_briefing

@app.callback(
    Output("ia-output", "children"),
    Input("intervalo", "n_intervals")
)
def ia_tick(n):
    msgs = generate_ai_briefing()
    return html.Ul([html.Li(m) for m in msgs])

# ---------------------------------------------------------
# EXECUÇÃO DO SERVIDOR
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050
    )
