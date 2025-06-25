# session_manager.py
import pickle
import os
import random
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS") or os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD")

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError(
        "❌ No se encontraron las variables de entorno EMAIL_ADDRESS o EMAIL_PASSWORD"
    )


SESSION_FILE = "file.pkl"
SESSION_DURATION_MINUTES = 5

# — Usuarios permitidos (hardcoded). Modifica o amplía aquí
VALID_USERS = {
    "Jhonattan": {"password": "@Ut0M@tI0n", "email": "jhonattan.blanco@orchest.net"},
    "JB": {"password": "jwb123", "email": "jhonattanblanco@gmail.com"},
    "Irvin": {"password": "@Ut0M@tI0n", "email": "irvin.garciadececa@orchest.net"},
    "Erwind": {"password": "@Ut0M@tI0n", "email": "erwind.martinez@orchest.net"},
    "Jorge": {"password": "@Ut0M@tI0n", "email": "jorge.arrechea@orchest.net"},
    "Nicolas": {"password": "@Ut0M@tI0n", "email": "nicolas.cramer@orchest.net"},
    "Frank": {"password": "@Ut0M@tI0n", "email": "jhonattanblanco@gmail.com"},
    "Daniela": {"password": "@Ut0M@tI0n", "email": "daniela.blanco@orchest.net"},
    "Zimri": {"password": "@Ut0M@tI0n", "email": "zimri.gorrin@orchest.net"},
    "Jaime": {"password": "@Ut0M@tI0n", "email": "yuri.penaforte@orchest.net"},
}


# ==============================
# Inicializa el archivo de sesión
# ==============================
def init_session():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "wb") as file:
            pickle.dump(
                {
                    "authenticated": False,
                    "verified": False,
                    "start_time": None,
                    "username": "",
                    "user_email": "",
                    "code": "",
                    "session_start_time": None,
                },
                file,
            )


# ==============================
# Carga el estado de sesión desde el archivo
# ==============================
def load_session():
    with open(SESSION_FILE, "rb") as file:
        data = pickle.load(file)
        if not isinstance(data, dict):
            raise ValueError(
                "❗ El archivo de sesión no contiene un diccionario válido."
            )
        return data


# ==============================
# Guarda el estado de sesión en el archivo
# ==============================
def save_session(session):
    with open(SESSION_FILE, "wb") as file:
        pickle.dump(session, file)


# ==============================
# Envía un código de verificación por correo
# ==============================
def send_email(recipient, code):
    msg = EmailMessage()
    msg["Subject"] = "Código de verificación - Acceso Atlas"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

    html_content = f"""
    <html>
        <body style="font-family: Tahoma, sans-serif;">
            <div style="
                width: 330px;
                height: 75px;
                font-weight: bold;
                font-size: 32px;
                text-transform: lowercase;
                text-align: left;
                display: flex;
                align-items: center;
                padding-left: 10px;
                border-bottom: 2px solid #ccc;
                margin-bottom: 20px;">
                atlas.io&nbsp;🌐
            </div>
            <p>Tu código de verificación es:</p>
            <h2 style="color: #004aad;">{code}</h2>
        </body>
    </html>
    """

    msg.set_content(f"Tu código de verificación es: {code}")  # fallback texto plano
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# ==============================
# Envía correo al cerrar sesión
# ==============================
def send_session_end_email(user, start_time, end_time, recipient):
    duration = end_time - start_time
    msg = EmailMessage()
    msg["Subject"] = f"Sesión cerrada - {user}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    html_content = f"""
    <html>
        <body style="font-family: Tahoma, sans-serif;">
            <div style="
                width: 330px;
                height: 75px;
                font-weight: bold;
                font-size: 32px;
                text-transform: lowercase;
                text-align: left;
                display: flex;
                align-items: center;
                padding-left: 10px;
                border-bottom: 2px solid #ccc;
                margin-bottom: 20px;">
                atlas.io&nbsp;🌐
            </div>
            <p><strong>Usuario:</strong> {user}</p>
            <p><strong>Inicio:</strong> {start_time}</p>
            <p><strong>Fin:</strong> {end_time}</p>
            <p><strong>Duración total:</strong> {duration}</p>
        </body>
    </html>
    """

    msg.set_content(
        f"Usuario: {user}\nInicio: {start_time}\nFin: {end_time}\nDuración total: {duration}"
    )
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# ==============================
# Verifica si hay una sesión activa
# ==============================
def is_session_active():
    session = load_session()
    if not session.get("authenticated") or not session.get("verified"):
        return False
    start = session.get("start_time")
    if not start:
        return False
    elapsed = datetime.now() - start
    return elapsed <= timedelta(minutes=SESSION_DURATION_MINUTES)


# ==============================
# Inicia el flujo de autenticación
# ==============================
def start_auth_flow(username, password):
    if username in VALID_USERS and password == VALID_USERS[username]["password"]:
        email = VALID_USERS[username]["email"]
        code = str(random.randint(100000, 999999))
        session = load_session()
        now = datetime.now()
        session.update(
            {
                "authenticated": True,
                "verified": False,
                "username": username,
                "user_email": email,
                "code": code,
                "start_time": now,
                "session_start_time": now,
            }
        )
        save_session(session)
        send_email(email, code)
        return code
    else:
        logout()
        return None


# ==============================
# Verifica el código ingresado por el usuario
# ==============================
def verify_code(input_code):
    session = load_session()
    if session.get("code") == input_code:
        now = datetime.now()
        if session.get("start_time"):
            # Acumula duración de la sesión previa
            elapsed = now - session["start_time"]
            session["total_duration"] += elapsed

        # Establece nuevo inicio
        session["verified"] = True
        session["start_time"] = now
        save_session(session)
        return True
    return False


# ==============================
# Finaliza la sesión actual
# ==============================
def logout():
    session = load_session()
    now = datetime.now()
    if session.get("authenticated") and session.get("session_start_time"):
        send_session_end_email(
            session["username"],
            session["session_start_time"],
            now,
            session["user_email"],
        )
    session.update(
        {
            "authenticated": False,
            "verified": False,
            "start_time": None,
            "username": "",
            "user_email": "",
            "code": "",
            "session_start_time": None,
        }
    )
    save_session(session)


# ==============================
# Funcion para el logout automatico
# ==============================


def stop_if_session_expired():
    session = load_session()
    now = datetime.now()

    if session.get("authenticated") and session.get("verified"):
        start = session.get("start_time")
        session_start = session.get("session_start_time")
        if start and session_start:
            elapsed = now - start
            if elapsed > timedelta(minutes=SESSION_DURATION_MINUTES):
                send_session_end_email(
                    session["username"], session_start, now, session["user_email"]
                )
                st.warning(
                    "⚠️ Tu sesión ha expirado. Se ha enviado un correo con el resumen."
                )
                st.stop()
