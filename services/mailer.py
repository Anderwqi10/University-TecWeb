"""Envío de correo SMTP con el código OTP de verificación."""

import os
import smtplib
import ssl
from email.message import EmailMessage


def send_verification_email(to_email: str, code: str) -> None:
    """Variables: SMTP_HOST, SMTP_PORT (587 o 465), SMTP_USER, SMTP_PASS o SMTP_PASSWORD, SMTP_FROM."""
    host = (os.getenv("SMTP_HOST") or "").strip()
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD") or "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    from_email = (os.getenv("SMTP_FROM") or user or "").strip()

    if not host or not user or not password or not from_email:
        print(
            "\n[SMTP] Modo desarrollo: faltan variables o están vacías.\n"
            "       Configura en .env: SMTP_HOST, SMTP_USER, SMTP_PASS, SMTP_FROM (y SMTP_PORT).\n"
            "       El código solo aparece aquí abajo, no se envía por correo.\n"
        )
        print(f"[DEV] Código OTP para {to_email}: {code}\n")
        return

    msg = EmailMessage()
    msg["Subject"] = "Código de verificación TecWeb"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(
        "Tu código de verificación (válido 10 minutos) es:\n\n"
        f"{code}\n\n"
        "Si no solicitaste este registro, ignora este mensaje."
    )

    try:
        if port == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=25, context=ctx) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=25) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                smtp.login(user, password)
                smtp.send_message(msg)
        print(f"[SMTP] Código enviado correctamente a {to_email}")
    except (smtplib.SMTPException, OSError, TimeoutError, ssl.SSLError) as exc:
        raise RuntimeError(
            "No se pudo enviar el correo. Revisa SMTP en .env (Gmail: usa contraseña de aplicación, "
            f"puerto 587 con STARTTLS o 465 con SSL). Detalle: {exc}"
        ) from exc
