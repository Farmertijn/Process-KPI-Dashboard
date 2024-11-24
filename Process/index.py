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

# Flask server configureren
server = Flask(__name__)
server.secret_key = 'your_secret_key'
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(server)
bcrypt.init_app(server)

# Maak database als die nog niet bestaat
with server.app_context():
    db.create_all()
    # Voeg een standaard admin-gebruiker toe als deze nog niet bestaat
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin/admin123")

# Dash-app configureren
app = Dash(server=server, url_base_pathname='/dashboard/', suppress_callback_exceptions=True)
app.title = 'Process KPI Dashboard'

# Rootroute voor redirect naar login
@server.route('/')
def root():
    return redirect('/login')

# Loginroute
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

# Registratieroute
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

# Uitlogroute
@server.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('is_admin', None)
    flash("You have been logged out.")
    return redirect('/login')

# Admin-dashboard route
@server.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    # Check if the logged-in user is an admin
    current_user = User.query.filter_by(username=session.get('user')).first()
    if not current_user or not current_user.is_admin:
        return "Unauthorized access. Only admins can view this page.", 403

    # Handle form submissions for user actions
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

    # Fetch all users for display
    users = User.query.all()
    return render_template('admin.html', users=users)

# Dash Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-period', data='today'),
    dcc.Store(id='is-admin', data=False),  # Store voor admin-status
    # Knoppenbalk bovenaan
    html.Div(className='button-container', children=[
        html.Button('Today', id='btn-today', className='tab-button', n_clicks=0),
        html.Button('Yesterday', id='btn-yesterday', className='tab-button', n_clicks=0),
        html.Button('Last Week', id='btn-week', className='tab-button', n_clicks=0),
        html.A("Logout", href="/logout", className='tab-button logout-button'),
        html.A("Admin Dashboard", href="/admin", className='tab-button admin-dashboard'),
    ]),
    html.Div(id='page-content')
])

# Callback voor admin-knop
@app.callback(
    Output('admin-dashboard-button', 'children'),
    [Input('is-admin', 'data')]
)
def update_admin_button(is_admin):
    if is_admin:
        return html.A("Admin Dashboard", href="/admin", className='tab-button admin-button')
    return no_update

# Preload admin-status bij het laden van de pagina
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

# Callback voor navigatie naar de juiste pagina
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'), Input('selected-period', 'data')]
)
def display_page(pathname, period):
    # Controleer of de gebruiker is ingelogd
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

# Callback voor het instellen van de periode met knoppen
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


if __name__ == '__main__':
    server.run(debug=True)
