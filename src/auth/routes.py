from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State
from flask_login import login_user
from src.api.users import authenticate, create_user, get_user_by_username
from src.auth.login_manager import User
from src.api.profiles import create_profile_if_missing


def layout_login():
    return html.Div(
        className="login-container fade-in",
        children=[
            dcc.Store(id="login-mode-store", data="login"),
            html.Div(
                className="login-card glass-panel",
                children=[
                    # Título Dinâmico
                    html.Div("ANTIGRAVITY SPACE", id="auth-title", className="login-logo"),
                    # Subtítulo Dinâmico
                    html.Div("SaaS de Reconhecimento Planetário & Estelar", id="auth-subtitle", className="login-subtitle"),

                    # Input de Usuário (Sempre visível)
                    dcc.Input(
                        id="auth-username",
                        placeholder="Nome de Usuário",
                        type="text",
                        style={"width": "100%", "marginBottom": "16px"}
                    ),

                    # Input de Senha (Sempre visível)
                    dcc.Input(
                        id="auth-password",
                        placeholder="Senha de Acesso",
                        type="password",
                        style={"width": "100%", "marginBottom": "24px"}
                    ),

                    # Container do Confirmar Senha (Oculto por padrão no Login)
                    html.Div(
                        id="auth-confirm-container",
                        style={"display": "none", "width": "100%", "marginBottom": "24px"},
                        children=[
                            dcc.Input(
                                id="auth-confirm-password",
                                placeholder="Confirmar Senha",
                                type="password",
                                style={"width": "100%"}
                            )
                        ]
                    ),

                    # Botão de Envio (Rótulo e Estilo dinâmicos)
                    html.Button(
                        "Autenticar Sistemas",
                        id="auth-submit-button",
                        className="btn-action",
                        style={"width": "100%"}
                    ),

                    # Mensagem de Feedback (Sempre visível)
                    html.Div(id="auth-feedback", style={"marginTop": "20px", "color": "#f87171", "fontWeight": "500"}),

                    # Link de Alternância (Sempre visível)
                    html.Div(
                        style={"marginTop": "24px"},
                        children=[
                            html.A(
                                "Ainda não tem conta? Cadastre-se", 
                                id="toggle-login-mode", 
                                style={"color": "#818cf8", "textDecoration": "none", "cursor": "pointer", "fontSize": "0.9rem", "fontWeight": "500"}
                            )
                        ]
                    )
                ]
            )
        ]
    )


def register_callbacks(app):

    # Alterna entre telas de Login e Registro
    @app.callback(
        Output("login-mode-store", "data"),
        Input("toggle-login-mode", "n_clicks"),
        State("login-mode-store", "data"),
        prevent_initial_call=True
    )
    def toggle_mode(n_clicks, current_mode):
        if not n_clicks:
            return current_mode
        return "register" if current_mode == "login" else "login"

    # Atualiza o layout do card de autenticação
    @app.callback(
        [
            Output("auth-title", "children"),
            Output("auth-title", "style"),
            Output("auth-subtitle", "children"),
            Output("auth-confirm-container", "style"),
            Output("auth-password", "style"),
            Output("auth-submit-button", "children"),
            Output("auth-submit-button", "style"),
            Output("toggle-login-mode", "children")
        ],
        Input("login-mode-store", "data")
    )
    def update_ui(mode):
        if mode == "register":
            return (
                "CADASTRAR PILOTO",
                {"fontSize": "1.8rem"},
                "Crie uma nova conta e comece sua jornada",
                {"display": "block", "width": "100%", "marginBottom": "24px"},
                {"width": "100%", "marginBottom": "16px"},
                "Registrar Novo Piloto",
                {"width": "100%", "background": "linear-gradient(135deg, #10b981 0%, #059669 100%)", "boxShadow": "0 4px 15px rgba(16, 185, 129, 0.3)"},
                "Já possui uma conta? Entrar"
            )
        
        # Mode == "login"
        return (
            "ANTIGRAVITY SPACE",
            None,
            "SaaS de Reconhecimento Planetário & Estelar",
            {"display": "none", "width": "100%", "marginBottom": "24px"},
            {"width": "100%", "marginBottom": "24px"},
            "Autenticar Sistemas",
            {"width": "100%"},
            "Ainda não tem conta? Cadastre-se"
        )

    # Processamento do formulário (Login ou Registro)
    @app.callback(
        Output("auth-feedback", "children"),
        Input("auth-submit-button", "n_clicks"),
        [
            State("login-mode-store", "data"),
            State("auth-username", "value"),
            State("auth-password", "value"),
            State("auth-confirm-password", "value")
        ],
        prevent_initial_call=True
    )
    def handle_submit(n_clicks, mode, username, password, confirm_password):
        if not n_clicks:
            return ""

        if not username or not password:
            return "Por favor, preencha todos os campos."

        username = username.strip()

        if mode == "register":
            if not confirm_password:
                return "Por favor, confirme sua senha."
            
            if password != confirm_password:
                return "As senhas não coincidem."

            if len(password) < 4:
                return "A senha deve conter pelo menos 4 caracteres."

            # Verifica se o usuário já existe
            existing_user = get_user_by_username(username)
            if existing_user:
                return "Nome de usuário já cadastrado."

            # Cria o usuário
            user = create_user(username, password)
            if not user:
                return "Erro interno ao cadastrar usuário."

            # Garante a criação do perfil
            create_profile_if_missing(user["id"])

            # Login automático do novo usuário
            login_user(User(user["id"], user["username"]))

            # Redireciona para o cockpit
            return dcc.Location(href="/cockpit", id="redirect-register")

        else:
            # Mode == "login"
            user = authenticate(username, password)
            if not user:
                return "Credenciais inválidas."

            # Autentica o usuário
            login_user(User(user["id"], user["username"]))

            # Garante que o perfil existe
            create_profile_if_missing(user["id"])

            # Redireciona para o cockpit
            return dcc.Location(href="/cockpit", id="redirect-login")
