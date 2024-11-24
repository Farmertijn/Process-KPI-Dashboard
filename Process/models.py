from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialiseer database-objecten
db = SQLAlchemy()
bcrypt = Bcrypt()

# Model voor gebruikersbeheer
class User(db.Model):
    # Databasekolommen
    id = db.Column(db.Integer, primary_key=True)  # Unieke ID voor elke gebruiker
    username = db.Column(db.String(80), unique=True, nullable=False)  # Gebruikersnaam, uniek en verplicht
    password = db.Column(db.String(200), nullable=False)  # Versleuteld wachtwoord, verplicht
    is_admin = db.Column(db.Boolean, default=False)  # Bool om aan te geven of de gebruiker adminrechten heeft

    # Representatie van een User-object
    def __repr__(self):
        return f'<User {self.username}>'
