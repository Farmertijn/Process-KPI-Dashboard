import subprocess
import sys

# Lijst met benodigde libraries
required_libraries = [
    "dash",
    "dash_bootstrap_components",
    "mariadb",
    "pandas",
    "pytz",
    "seaborn",
    "matplotlib",
    "sqlalchemy",
    "flask_sqlalchemy",
    "flask_bcrypt"
]

# Controleer en installeer ontbrekende libraries
for library in required_libraries:
    try:
        __import__(library)
    except ImportError:
        print(f"{library} wordt geïnstalleerd...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

from flask import Flask, session, redirect, request, render_template, flash
from dash import Dash, dcc, html, Input, Output, callback_context, no_update
from models import db, bcrypt, User
import home
import InOut
import harvester

# Configuratie van de Flask-server
server = Flask(__name__)
server.secret_key = 'your_secret_key'  # Sleutel voor sessiebeheer
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite-database
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(server)
bcrypt.init_app(server)

# Initialiseer database en voeg een standaard admin-gebruiker toe
with server.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin/admin123")
    if not User.query.filter_by(username='test').first():
        hashed_password = bcrypt.generate_password_hash('test123').decode('utf-8')
        admin_user = User(username='test', password=hashed_password, is_admin=False)
        db.session.add(admin_user)
        db.session.commit()
        print("Test user created: test/test123")

# Configuratie van de Dash-applicatie
app = Dash(server=server, url_base_pathname='/dashboard/', suppress_callback_exceptions=True)
app.title = 'Process KPI Dashboard'

# Redirect rootroute naar de loginpagina
@server.route('/')
def root():
    return redirect('/login')

# Loginroute met validatie
@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = user.username
            session['is_admin'] = user.is_admin
            return redirect('/dashboard/')
        flash("Invalid credentials. Please try again.")
    return render_template('login.html')

# Registratieroute voor nieuwe gebruikers
@server.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different username.")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html')

# Uitlogroute wist sessiegegevens
@server.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('is_admin', None)
    flash("You have been logged out.")
    return redirect('/login')

# Admin-dashboard voor beheer van gebruikers
@server.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    current_user = User.query.filter_by(username=session.get('user')).first()
    if not current_user or not current_user.is_admin:
        return "Unauthorized access. Only admins can view this page.", 403

    if request.method == 'POST':
        if 'delete_user' in request.form:
            user_id = request.form['delete_user']
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash(f"User {user.username} deleted.", "success")
        elif 'make_admin' in request.form:
            user_id = request.form['make_admin']
            user = User.query.get(user_id)
            if user and not user.is_admin:
                user.is_admin = True
                db.session.commit()
                flash(f"User {user.username} is now an admin.", "success")
        elif 'remove_admin' in request.form:
            user_id = request.form['remove_admin']
            user = User.query.get(user_id)
            if user and user.is_admin:
                user.is_admin = False
                db.session.commit()
                flash(f"User {user.username} is no longer an admin.", "success")
        return redirect('/admin')

    users = User.query.all()
    return render_template('admin.html', users=users)

# Dash layout configureren
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Houd de URL bij
    dcc.Store(id='selected-period', data='today'),  # Opslag voor geselecteerde periode
    dcc.Store(id='is-admin', data=False),  # Adminstatus
    html.Div(className='button-container', children=[
        # Navigatieknoppen
        html.Button('Today', id='btn-today', className='tab-button', n_clicks=0),
        html.Button('Yesterday', id='btn-yesterday', className='tab-button', n_clicks=0),
        html.Button('Last Week', id='btn-week', className='tab-button', n_clicks=0),
        html.A("Logout", href="/logout", className='tab-button logout-button'),
        html.A("Admin Dashboard", href="/admin", className='tab-button admin-dashboard'),
    ]),
    html.Div(id='page-content')  # Dynamische inhoud
])

# Admin-knop updaten afhankelijk van admin-status
@app.callback(
    Output('admin-dashboard-button', 'children'),
    [Input('is-admin', 'data')]
)
def update_admin_button(is_admin):
    if is_admin:
        return html.A("Admin Dashboard", href="/admin", className='tab-button admin-button')
    return no_update

# Controleer admin-status bij het laden van een pagina
@app.callback(
    Output('is-admin', 'data'),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def check_admin_status(pathname):
    user = session.get('user')
    if user:
        current_user = User.query.filter_by(username=user).first()
        return current_user.is_admin if current_user else False
    return False

# Toewijzing van inhoud op basis van URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'), Input('selected-period', 'data')]
)
def display_page(pathname, period):
    if 'user' not in session:
        return html.Div([html.H1("Unauthorized"), html.P("Please login to access this page.")])

    if pathname == '/dashboard/' or pathname == '/dashboard/home':
        return home.generate_kpi_cards(period)
    elif pathname == '/dashboard/InOut':
        return InOut.generate_inout_kpi_cards(period)
    elif pathname == '/dashboard/harvester':
        return harvester.generate_harvester_kpi_cards(period)
    else:
        return html.Div('404 - Page Not Found')

# Instellen van periode via knoppen
@app.callback(
    [Output('selected-period', 'data'),
     Output('btn-today', 'className'),
     Output('btn-yesterday', 'className'),
     Output('btn-week', 'className')],
    [Input('btn-today', 'n_clicks'),
     Input('btn-yesterday', 'n_clicks'),
     Input('btn-week', 'n_clicks')]
)
def update_button_styles(n_clicks_today, n_clicks_yesterday, n_clicks_week):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-today'

    period_map = {
        'btn-today': 'today',
        'btn-yesterday': 'yesterday',
        'btn-week': 'week'
    }
    period = period_map.get(button_id, 'today')

    return (
        period,
        'tab-button active' if button_id == 'btn-today' else 'tab-button',
        'tab-button active' if button_id == 'btn-yesterday' else 'tab-button',
        'tab-button active' if button_id == 'btn-week' else 'tab-button'
    )

# Start de Flask-server
if __name__ == '__main__':
    server.run(debug=True)
