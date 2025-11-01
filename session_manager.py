# session_manager.py
import pickle
import os
import tempfile
import random
import requests
import streamlit as st
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# ==============================
# atlas.io Version 1.2.0 - Copyright © White Labs Technologies 2025
# author: jhonattan blanco
# ==============================


load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# Usar un directorio de escritura seguro en entornos PaaS (e.g., Railway)
# /tmp suele estar disponible para escritura; localmente no cambia el comportamiento.
SESSION_FILE = os.path.join(tempfile.gettempdir(), "file.pkl")
SESSION_DURATION_MINUTES = 25

# — Usuarios permitidos (hardcoded). Modifica o amplía aquí
VALID_USERS = {
    "JB": {"password": "jwb123", "email": "jhonattanblanco@gmail.com"},
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
                    # acumulado de tiempo de sesión
                    "total_duration": timedelta(0),
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

    # asegurar claves mínimas para compatibilidad hacia atrás
    changed = False
    if "total_duration" not in data:
        data["total_duration"] = timedelta(0)
        changed = True
    if changed:
        save_session(data)
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

    backend = os.getenv("EMAIL_BACKEND", "smtp").lower()
    if backend in ("console", "ui", "disabled"):
        # Modo demo/console: no intenta SMTP, muestra el código en UI
        st.info("Demo: usa este código de verificación")
        st.code(code)
        return

    if backend == "sendgrid":
        # Envío por API HTTP (443) — funciona en PaaS sin SMTP
        api_key = os.getenv("SENDGRID_API_KEY")
        sender = os.getenv("EMAIL_FROM") or EMAIL_ADDRESS
        if not api_key or not sender:
            st.warning("Configura SENDGRID_API_KEY y EMAIL_FROM/EMAIL_ADDRESS para enviar el código por email.")
            st.code(code)
            return
        try:
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [
                        {"to": [{"email": recipient}]}
                    ],
                    "from": {"email": sender},
                    "subject": "Código de verificación - Acceso Atlas",
                    "content": [
                        {"type": "text/plain", "value": f"Tu código de verificación es: {code}"},
                        {"type": "text/html", "value": html_content},
                    ],
                },
                timeout=15,
            )
            if resp.status_code not in (200, 201, 202):
                raise RuntimeError(f"SendGrid API error {resp.status_code}: {resp.text}")
            return
        except Exception as e:
            st.warning("No se pudo enviar el correo por SendGrid. Mostrando el código aquí para continuar.")
            st.code(code)
            st.caption(f"Email backend error: {e}")
            return

    # SMTP por defecto (Gmail). Intenta TLS 587 y luego SSL 465
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            return
    except Exception:
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                return
        except Exception as e:
            # Fallback si SMTP falla (puertos bloqueados en PaaS, sin red o credenciales)
            st.warning("No se pudo enviar el correo de verificación. Mostrando el código aquí para continuar.")
            st.code(code)
            st.caption(f"Email backend error: {e}")


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

    try:
        backend = os.getenv("EMAIL_BACKEND", "smtp").lower()
        if backend in ("console", "ui", "disabled"):
            return
        if backend == "sendgrid":
            api_key = os.getenv("SENDGRID_API_KEY")
            sender = os.getenv("EMAIL_FROM") or EMAIL_ADDRESS
            if not api_key or not sender:
                return
            requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [
                        {"to": [{"email": recipient}]}
                    ],
                    "from": {"email": sender},
                    "subject": f"Sesión cerrada - {user}",
                    "content": [
                        {"type": "text/plain", "value": f"Usuario: {user}\nInicio: {start_time}\nFin: {end_time}"},
                        {"type": "text/html", "value": html_content},
                    ],
                },
                timeout=15,
            )
            return

        # SMTP por defecto
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception:
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
        except Exception:
            # Silencioso: no debe impedir el cierre de sesión
            pass


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
            # Acumula duración de la sesión previa con valor por defecto seguro
            elapsed = now - session["start_time"]
            session["total_duration"] = session.get("total_duration", timedelta(0)) + elapsed

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

                # ✅ Resetear archivo .pkl para permitir nuevo login
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

                st.warning(
                    "⚠️ Your session has expired. Please refresh your browser window"
                )
                st.stop()
