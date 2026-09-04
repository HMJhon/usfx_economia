import os
import secrets
from functools import wraps

from urllib.parse import urlparse

import qrcode
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename

from models import (
    db, User, Publication, Activity, PointsTransaction, AvatarConfig,
    ROLE_ESTUDIANTE, ROLE_ADMIN, ROLE_REY
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
QR_FOLDER = os.path.join(BASE_DIR, "static", "qrcodes")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esta-clave-por-una-segura-en-produccion")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "usfx_economia.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor inicia sesión para continuar."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- Utilidades ----------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_storage, subfolder=""):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash("Formato de imagen no permitido.", "danger")
        return None
    filename = secure_filename(file_storage.filename)
    unique_name = f"{secrets.token_hex(6)}_{filename}"
    folder = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, unique_name)
    file_storage.save(path)
    rel_path = os.path.join("uploads", subfolder, unique_name).replace("\\", "/")
    return rel_path


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin_like():
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


def rey_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_rey():
            flash("Solo 'El Rey' puede acceder a esta sección.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


def get_avatar_config():
    config = AvatarConfig.query.first()
    if not config:
        config = AvatarConfig()
        db.session.add(config)
        db.session.commit()
    return config


# ---------- Rutas públicas ----------

@app.route("/")
def index():
    publicaciones = Publication.query.order_by(Publication.created_at.desc()).limit(6).all()
    actividades = Activity.query.order_by(Activity.created_at.desc()).limit(6).all()
    return render_template("index.html", publicaciones=publicaciones, actividades=actividades)


@app.route("/registro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("register"))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("El usuario o correo ya está registrado.", "danger")
            return redirect(url_for("register"))

        is_first_user = User.query.count() == 0
        user = User(
            username=username,
            email=email,
            role=ROLE_REY if is_first_user else ROLE_ESTUDIANTE,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if is_first_user:
            flash("¡Registro exitoso! Eres el primer usuario del sistema: rol 'El Rey' asignado.", "success")
        else:
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


def is_safe_next_url(target):
    """Evita redirecciones abiertas: solo permite rutas internas del propio sitio."""
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(target)
    return test.scheme in ("", "http", "https") and ref.netloc == test.netloc


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenido, {user.username}.", "success")
            next_url = request.form.get("next") or request.args.get("next")
            if next_url and is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos.", "danger")
    next_url = request.args.get("next", "")
    return render_template("login.html", next_url=next_url)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("index"))


# ---------- Publicaciones ----------

@app.route("/publicaciones")
def publicaciones():
    fuente = request.args.get("fuente")
    query = Publication.query.order_by(Publication.created_at.desc())
    if fuente in ("facultad", "centro_estudiantes"):
        query = query.filter_by(source=fuente)
    return render_template("publicaciones.html", publicaciones=query.all(), fuente=fuente)


@app.route("/publicaciones/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def nueva_publicacion():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        source = request.form.get("source", "facultad")
        image = request.files.get("image")

        if not title or not content:
            flash("Título y contenido son obligatorios.", "danger")
            return redirect(url_for("nueva_publicacion"))

        image_path = save_image(image, subfolder="publicaciones")
        pub = Publication(
            title=title, content=content, source=source,
            image_path=image_path, author_id=current_user.id
        )
        db.session.add(pub)
        db.session.commit()
        flash("Publicación creada correctamente.", "success")
        return redirect(url_for("publicaciones"))

    return render_template("publicacion_form.html")


@app.route("/publicaciones/<int:pub_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_publicacion(pub_id):
    pub = Publication.query.get_or_404(pub_id)
    db.session.delete(pub)
    db.session.commit()
    flash("Publicación eliminada.", "info")
    return redirect(url_for("publicaciones"))


# ---------- Actividades / eventos con QR ----------

@app.route("/actividades")
def actividades():
    lista = Activity.query.order_by(Activity.created_at.desc()).all()
    return render_template("actividades.html", actividades=lista)


@app.route("/actividades/<int:activity_id>")
def detalle_actividad(activity_id):
    actividad = Activity.query.get_or_404(activity_id)
    ya_escaneado = False
    if current_user.is_authenticated:
        ya_escaneado = PointsTransaction.query.filter_by(
            user_id=current_user.id, activity_id=actividad.id, kind="escaneo"
        ).first() is not None
    return render_template("actividad_detalle.html", actividad=actividad, ya_escaneado=ya_escaneado)


@app.route("/actividades/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def nueva_actividad():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        cost = request.form.get("cost", "Gratuito").strip()
        benefits = request.form.get("benefits", "").strip()
        event_date = request.form.get("event_date", "").strip()
        place = request.form.get("place", "").strip()
        points_value = request.form.get("points_value", 10)
        image = request.files.get("image")

        if not title or not description:
            flash("Título y descripción son obligatorios.", "danger")
            return redirect(url_for("nueva_actividad"))

        image_path = save_image(image, subfolder="actividades")
        token = secrets.token_urlsafe(16)

        actividad = Activity(
            title=title, description=description, cost=cost, benefits=benefits,
            event_date=event_date, place=place, points_value=int(points_value or 10),
            image_path=image_path, qr_token=token, author_id=current_user.id
        )
        db.session.add(actividad)
        db.session.commit()

        # Generar QR apuntando a la ruta de escaneo con el token único
        scan_url = url_for("escanear", activity_id=actividad.id, token=token, _external=True)
        img = qrcode.make(scan_url)
        os.makedirs(QR_FOLDER, exist_ok=True)
        qr_filename = f"qr_actividad_{actividad.id}.png"
        img.save(os.path.join(QR_FOLDER, qr_filename))
        actividad.qr_code_path = f"qrcodes/{qr_filename}"
        db.session.commit()

        flash("Actividad creada y código QR generado.", "success")
        return redirect(url_for("detalle_actividad", activity_id=actividad.id))

    return render_template("actividad_form.html")


@app.route("/actividades/<int:activity_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_actividad(activity_id):
    actividad = Activity.query.get_or_404(activity_id)
    db.session.delete(actividad)
    db.session.commit()
    flash("Actividad eliminada.", "info")
    return redirect(url_for("actividades"))


@app.route("/escanear/<int:activity_id>")
def escanear(activity_id):
    """Ruta a la que apunta el código QR. Si el usuario no está logueado, se le pide iniciar sesión."""
    actividad = Activity.query.get_or_404(activity_id)
    token = request.args.get("token")
    if token != actividad.qr_token:
        flash("Código QR inválido.", "danger")
        return redirect(url_for("index"))

    if not current_user.is_authenticated:
        flash("Inicia sesión para registrar tus puntos por esta actividad.", "info")
        return redirect(url_for("login", next=request.url))

    ya = PointsTransaction.query.filter_by(
        user_id=current_user.id, activity_id=actividad.id, kind="escaneo"
    ).first()

    avatar = get_avatar_config()
    if ya:
        return render_template(
            "escaneo_resultado.html", actividad=actividad, ganado=False,
            avatar=avatar, mensaje="Ya habías escaneado este código antes. ¡Gracias por tu participación!"
        )

    tx = PointsTransaction(
        user_id=current_user.id, activity_id=actividad.id,
        points=actividad.points_value, kind="escaneo",
        note=f"Escaneo QR: {actividad.title}"
    )
    current_user.points += actividad.points_value
    db.session.add(tx)
    db.session.commit()

    return render_template(
        "escaneo_resultado.html", actividad=actividad, ganado=True,
        avatar=avatar, mensaje=avatar.message_scan, puntos=actividad.points_value
    )


@app.route("/compartir/<int:activity_id>", methods=["POST"])
@login_required
def compartir(activity_id):
    actividad = Activity.query.get_or_404(activity_id)
    ya = PointsTransaction.query.filter_by(
        user_id=current_user.id, activity_id=actividad.id, kind="compartir"
    ).first()
    if ya:
        return jsonify({"ok": False, "message": "Ya sumaste puntos por compartir esta actividad."})

    tx = PointsTransaction(
        user_id=current_user.id, activity_id=actividad.id,
        points=actividad.share_points_value, kind="compartir",
        note=f"Compartido en redes: {actividad.title}"
    )
    current_user.points += actividad.share_points_value
    db.session.add(tx)
    db.session.commit()

    avatar = get_avatar_config()
    return jsonify({
        "ok": True,
        "points": actividad.share_points_value,
        "total": current_user.points,
        "message": avatar.message_share,
        "color_primary": avatar.color_primary,
        "color_secondary": avatar.color_secondary,
    })


# ---------- Perfil de usuario ----------

@app.route("/perfil")
@login_required
def perfil():
    historial = PointsTransaction.query.filter_by(user_id=current_user.id).order_by(
        PointsTransaction.created_at.desc()
    ).all()
    return render_template("perfil.html", historial=historial)


# ---------- Panel administrativo ----------

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    usuarios = User.query.order_by(User.points.desc()).all()
    total_actividades = Activity.query.count()
    total_publicaciones = Publication.query.count()
    return render_template(
        "admin_dashboard.html", usuarios=usuarios,
        total_actividades=total_actividades, total_publicaciones=total_publicaciones
    )


@app.route("/admin/canjear", methods=["GET", "POST"])
@login_required
@admin_required
def canjear_puntos():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        puntos = request.form.get("puntos", "0")
        motivo = request.form.get("motivo", "Canje de puntos").strip()

        try:
            puntos = int(puntos)
        except ValueError:
            flash("La cantidad de puntos debe ser un número.", "danger")
            return redirect(url_for("canjear_puntos"))

        estudiante = User.query.filter_by(username=username).first()
        if not estudiante:
            flash("Estudiante no encontrado.", "danger")
            return redirect(url_for("canjear_puntos"))
        if puntos <= 0:
            flash("Ingresa una cantidad de puntos válida.", "danger")
            return redirect(url_for("canjear_puntos"))
        if estudiante.points < puntos:
            flash(f"{estudiante.username} no tiene suficientes puntos ({estudiante.points} disponibles).", "danger")
            return redirect(url_for("canjear_puntos"))

        estudiante.points -= puntos
        tx = PointsTransaction(
            user_id=estudiante.id, points=-puntos, kind="canje",
            note=f"{motivo} (validado por {current_user.username})"
        )
        db.session.add(tx)
        db.session.commit()
        flash(f"Se canjearon {puntos} puntos de {estudiante.username}. Saldo restante: {estudiante.points}.", "success")
        return redirect(url_for("canjear_puntos"))

    return render_template("canjear.html")


@app.route("/admin/avatar", methods=["GET", "POST"])
@login_required
@rey_required
def editar_avatar():
    config = get_avatar_config()
    if request.method == "POST":
        config.color_primary = request.form.get("color_primary", config.color_primary)
        config.color_secondary = request.form.get("color_secondary", config.color_secondary)
        config.message_scan = request.form.get("message_scan", config.message_scan)
        config.message_share = request.form.get("message_share", config.message_share)
        db.session.commit()
        flash("Avatar 3D actualizado correctamente.", "success")
        return redirect(url_for("editar_avatar"))
    return render_template("avatar_editor.html", avatar=config)


@app.route("/admin/usuarios/<int:user_id>/rol", methods=["POST"])
@login_required
@rey_required
def cambiar_rol(user_id):
    usuario = User.query.get_or_404(user_id)
    nuevo_rol = request.form.get("role")
    if nuevo_rol not in (ROLE_ESTUDIANTE, ROLE_ADMIN, ROLE_REY):
        flash("Rol inválido.", "danger")
        return redirect(url_for("admin_dashboard"))
    if usuario.role == ROLE_REY and nuevo_rol != ROLE_REY:
        # Evitar quedarse sin ningún 'El Rey' en el sistema por accidente
        otros_reyes = User.query.filter(User.role == ROLE_REY, User.id != usuario.id).count()
        if otros_reyes == 0:
            flash("Debe existir al menos un usuario con rol 'El Rey'.", "danger")
            return redirect(url_for("admin_dashboard"))
    usuario.role = nuevo_rol
    db.session.commit()
    flash(f"Rol de {usuario.username} actualizado a {nuevo_rol}.", "success")
    return redirect(url_for("admin_dashboard"))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)