from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Inicializar o aplicativo Flask
app_flask = Flask(__name__)

# Configurações do banco de dados SQLite
app_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app_flask.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app_flask)

# Modelo de dados para a tabela de usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Rotas do Flask

@app_flask.route('/')
def index():
    return render_template('index.html')

@app_flask.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.password, password):
            return redirect(url_for('pagina_principal'))
    return render_template('login.html')

@app_flask.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        senha_hash = generate_password_hash(password, method='sha256')
        novo_usuario = Usuario(username=username, password=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app_flask.route('/pagina-principal')
def pagina_principal():
    return render_template('pagina_principal.html')

# Inicializar o aplicativo Dash com um tema Bootstrap
app_dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=app_flask)

# Layout do aplicativo Dash
app_dash.layout = html.Div([
    dcc.Graph(id='grafico-barras'),
])

# Callback para gerar gráficos somente se o usuário estiver autenticado
@app_dash.callback(Output('grafico-barras', 'figure'),
              [Input('url', 'pathname')])
def gerar_grafico(pathname):
    if verificar_senha_autenticada():
        # Coloque aqui a lógica para gerar o gráfico
        return {'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Exemplo'}],
                'layout': {'title': 'Exemplo de Gráfico'}}
    else:
        return {'data': [], 'layout': {'title': 'Faça o login para acessar os gráficos'}}

# Função para verificar se o usuário está autenticado
def verificar_senha_autenticada():
    return '/pagina-principal' in dash.callback_context.outputs_list

# Executar o aplicativo Flask
if __name__ == '__main__':
    with app_flask.app_context():
        db.create_all()
        app_flask.run(debug=True)
