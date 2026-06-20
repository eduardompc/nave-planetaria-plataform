import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_login import LoginManager, current_user
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from src.auth.login_manager import login_manager
from src.auth.routes import layout_login, register_callbacks
from src.auth.session import get_current_profile
from src.user.dashboard import layout_user_dashboard, register_dashboard_callbacks
from src.telemetry.recorder import record_tick
from src.ai.events import on_cockpit_open
from src.ai.core import generate_ai_briefing

# ---------------------------------------------------------
# FLASK SERVER + LOGIN
# ---------------------------------------------------------

server = Flask(__name__)
server.secret_key = os.environ.get("FLASK_SECRET_KEY", "CHAVE-SECRETA-DA-NAVE")
server.config["SESSION_COOKIE_SECURE"] = False
server.config["SESSION_COOKIE_SAMESITE"] = "Lax"
server.config["SESSION_COOKIE_HTTPONLY"] = True

login_manager.init_app(server)

# ---------------------------------------------------------
# DASH APP
# ---------------------------------------------------------

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

register_callbacks(app)
register_dashboard_callbacks(app)

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (DINÂMICO)
# ---------------------------------------------------------

def serve_layout():
    return html.Div([
        dcc.Location(id="url"),
        html.Div(id="page-content", children=layout_login()),
        html.Div(id="ia-output", style={"display": "none"}),
        html.Div(id="dummy-output", style={"display": "none"}),
        dcc.Interval(id="intervalo", interval=2000, n_intervals=0)
    ])

app.layout = serve_layout

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
        return layout_user_dashboard()

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
    debug_mode = os.environ.get("DEBUG", "True").lower() == "true"
    port_val = int(os.environ.get("PORT", 8050))
    app.run(
        debug=debug_mode,
        host="127.0.0.1",
        port=port_val
    )
