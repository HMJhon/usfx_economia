from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

ROLE_ESTUDIANTE = "estudiante"
ROLE_ADMIN = "administrativo"
ROLE_REY = "el_rey"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_ESTUDIANTE)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin_like(self):
        return self.role in (ROLE_ADMIN, ROLE_REY)

    def is_rey(self):
        return self.role == ROLE_REY


class Publication(db.Model):
    """Publicaciones del Centro de Estudiantes o de la Facultad (noticias, avisos)."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300))
    source = db.Column(db.String(30), nullable=False, default="facultad")  # 'facultad' o 'centro_estudiantes'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Activity(db.Model):
    """Conferencias, talleres y eventos con código QR y puntos."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300))
    cost = db.Column(db.String(100), default="Gratuito")
    benefits = db.Column(db.Text)
    event_date = db.Column(db.String(100))
    place = db.Column(db.String(200))
    points_value = db.Column(db.Integer, default=10)
    share_points_value = db.Column(db.Integer, default=5)
    qr_code_path = db.Column(db.String(300))
    qr_token = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class PointsTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=True)
    points = db.Column(db.Integer, nullable=False)  # positivo = gana, negativo = canje
    kind = db.Column(db.String(30), nullable=False)  # 'escaneo', 'compartir', 'canje'
    note = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AvatarConfig(db.Model):
    """Configuración global del muñeco/avatar 3D, editable solo por 'El Rey'."""
    id = db.Column(db.Integer, primary_key=True)
    color_primary = db.Column(db.String(20), default="#f4c542")
    color_secondary = db.Column(db.String(20), default="#2b6cb0")
    message_scan = db.Column(db.String(300), default="¡Bien hecho! Ganaste puntos por participar 🎉")
    message_share = db.Column(db.String(300), default="¡Gracias por compartir! Sigue sumando puntos 🚀")
