from flask import Flask
from flask_login import LoginManager, current_user
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from src.auth.login_manager import login_manager
from src.auth.routes import layout_login, register_callbacks
from src.auth.session import on_user_login
from src.auth.session import get_current_profile
from src.user.dashboard import layout_user_dashboard, register_dashboard_callbacks
from src.telemetry.recorder import record_tick

server = Flask(__name__)
server.secret_key = "CHAVE-SECRETA-DA-NAVE"

login_manager.init_app(server)

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

register_callbacks(app)

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content"),

    # IA e telemetria
    html.Div(id="ia-output"),
    html.Div(id="dummy-output"),
    dcc.Interval(id="intervalo", interval=2000, n_intervals=0)
])

@app.server.before_request
def protect_routes():
    from flask import request, redirect

    protected_paths = ["/cockpit"]

    if request.path in protected_paths and not current_user.is_authenticated:
        return redirect("/login")

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/login" or pathname is None:
        return layout_login()

    if pathname == "/cockpit":
        profile = get_current_profile()
        if not profile:
            # se não tiver sessão, manda pro login
            return layout_login()
        # usa o cockpit “oficial” com IA
        return layout_cockpit()

    # rota padrão
    return layout_login()
    
@app.callback(
    Output("dummy-output", "children"),
    Input("intervalo", "n_intervals")
)
def tick(n):
    record_tick()
    return ""
    
from src.ai.events import on_cockpit_open

def layout_cockpit():
    profile = get_current_profile()
    briefing = on_cockpit_open()

    return html.Div([
        html.H1(f"Cockpit da Nave Planetária — {profile['rank']}"),
        html.P(f"XP: {profile['xp']}"),
        html.P(f"Tema: {profile['theme']}"),
        html.P(f"Último login: {profile['last_login']}"),
        html.H3("Briefing da IA"),
        html.Ul([html.Li(msg) for msg in briefing]),
    ])

from src.ai.core import generate_ai_briefing

@app.callback(
    Output("ia-output", "children"),
    Input("intervalo", "n_intervals")
)
def ia_tick(n):
    msgs = generate_ai_briefing()
    return html.Ul([html.Li(m) for m in msgs])
# --- callbacks, rotas, layouts etc. acima ---

if __name__ == "__main__":
    app.run(
    debug=True,
    host="127.0.0.1",
    port=8050
)

