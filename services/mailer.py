"""Envío del OTP: APIs HTTPS (por defecto SendGrid, luego Resend, Brevo). SMTP suele fallar en Render.

Render normalmente bloquea conexiones SMTP a Internet (p. ej. smtp.gmail.com:587).
Usar SendGrid (o otro proveedor) por API HTTPS (puerto 443).

Opcional: MAIL_OTP_LOG_ONLY=true imprime el OTP en logs (solo demos / emergencia).
"""

import os
import smtplib
import ssl
from collections.abc import Callable
from email.message import EmailMessage
from email.utils import parseaddr

import httpx

_VERIFICATION_SUBJECT = "Código de verificación TecWeb"


def _verification_body(code: str) -> str:
    return (
        "Tu código de verificación (válido 10 minutos) es:\n\n"
        f"{code}\n\n"
        "Si no solicitaste este registro, ignora este mensaje."
    )


def _parse_sender(raw: str) -> tuple[str, str | None]:
    """Devuelve (email_normalizado, nombre_opcional). Acepta `correo@x.com` o `Nombre <correo@x.com>`."""
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("remitente vacío")
    name, addr = parseaddr(raw)
    addr = (addr or "").strip()
    if not addr:
        raise ValueError(f"No se pudo leer un correo en: {raw!r}")
    addr = addr.lower()
    display = (name or "").strip() or None
    return addr, display


def _send_via_resend(to_email: str, code: str) -> None:
    """POST https://api.resend.com/emails"""
    api_key = (os.getenv("RESEND_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("RESEND_API_KEY está vacío.")

    from_default = "TecWeb <onboarding@resend.dev>"
    from_raw = (os.getenv("RESEND_FROM_EMAIL") or "").strip() or from_default

    try:
        addr, display_name = _parse_sender(from_raw)
    except ValueError:
        addr, display_name = _parse_sender(from_default)

    from_header = f"{display_name} <{addr}>" if display_name else addr

    payload = {
        "from": from_header,
        "to": [to_email],
        "subject": _VERIFICATION_SUBJECT,
        "text": _verification_body(code),
    }

    try:
        with httpx.Client(timeout=25.0) as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"No se pudo contactar a Resend: {exc}") from exc

    if response.status_code >= 400:
        raise RuntimeError(
            "Resend rechazó el envío. Verifica RESEND_API_KEY; si mandás a correos reales, "
            "verifica un dominio en Resend y pon RESEND_FROM_EMAIL con un @ de ese dominio. "
            f"HTTP {response.status_code}: {response.text}"
        )
    print(f"[Resend] Código enviado correctamente a {to_email}")


def _send_via_brevo(to_email: str, code: str) -> None:
    """POST https://api.brevo.com/v3/smtp/email (HTTPS). Remitente debe estar validado en Brevo."""
    api_key = (os.getenv("BREVO_API_KEY") or "").strip()
    from_raw = (os.getenv("BREVO_FROM_EMAIL") or "").strip()
    if not api_key:
        raise RuntimeError("BREVO_API_KEY está vacío.")
    if not from_raw:
        raise RuntimeError(
            "Configura BREVO_FROM_EMAIL con un correo autorizado en Brevo (Senders →)."
        )

    addr, display_name = _parse_sender(from_raw)
    sender: dict[str, str] = {"email": addr}
    if display_name:
        sender["name"] = display_name
    else:
        sender["name"] = "TecWeb"

    payload = {
        "sender": sender,
        "to": [{"email": to_email}],
        "subject": _VERIFICATION_SUBJECT,
        "textContent": _verification_body(code),
    }

    try:
        with httpx.Client(timeout=25.0) as client:
            response = client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"No se pudo contactar a Brevo: {exc}") from exc

    if response.status_code >= 400:
        raise RuntimeError(
            "Brevo rechazó el envío. Revisa la API key y que BREVO_FROM_EMAIL sea un remitente "
            f"validado en el panel de Brevo. HTTP {response.status_code}: {response.text}"
        )
    print(f"[Brevo] Código enviado correctamente a {to_email}")


def _send_via_sendgrid(to_email: str, code: str) -> None:
    """SendGrid v3 REST."""
    api_key = (os.getenv("SENDGRID_API_KEY") or "").strip()
    from_raw = (os.getenv("SENDGRID_FROM_EMAIL") or "").strip()
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY está vacío.")
    if not from_raw:
        raise RuntimeError(
            "Configura SENDGRID_FROM_EMAIL con el correo verificado en SendGrid "
            "(Sender Authentication → Single Sender)."
        )

    try:
        addr, display_name = _parse_sender(from_raw)
    except ValueError as exc:
        raise RuntimeError(f"SENDGRID_FROM_EMAIL no es válido: {exc}") from exc

    from_obj: dict = {"email": addr}
    if display_name:
        from_obj["name"] = display_name

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": from_obj,
        "subject": _VERIFICATION_SUBJECT,
        "content": [{"type": "text/plain", "value": _verification_body(code)}],
    }

    try:
        with httpx.Client(timeout=25.0) as client:
            response = client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"No se pudo contactar a SendGrid: {exc}") from exc

    if response.status_code >= 400:
        hint = ""
        if response.status_code == 403 and "Sender Identity" in response.text:
            hint = (
                " Usa el mismo correo que en SendGrid → Sender Authentication; puedes "
                "`TecWeb <tu@gmail.com>` en SENDGRID_FROM_EMAIL."
            )
        raise RuntimeError(
            "SendGrid rechazó el envío. Revisa API key y remitente verificado." + hint + f" HTTP {response.status_code}: {response.text}"
        )
    print(f"[SendGrid] Código enviado correctamente a {to_email}")


def _send_via_smtp(to_email: str, code: str) -> None:
    host = (os.getenv("SMTP_HOST") or "").strip()
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD") or "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    from_email = (os.getenv("SMTP_FROM") or user or "").strip()

    if not host or not user or not password or not from_email:
        print(
            "\n[mail] Sin proveedor API completo ni SMTP completo.\n"
            "       En Render el SMTP a Gmail casi siempre falla; usa SendGrid (o Resend/Brevo) por API HTTPS.\n"
            "       El código solo aparece abajo.\n"
        )
        print(f"[DEV] Código OTP para {to_email}: {code}\n")
        return

    msg = EmailMessage()
    msg["Subject"] = _VERIFICATION_SUBJECT
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(_verification_body(code))

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
            "SMTP falló (en Render es habitual: bloqueo de puertos). Usa SendGrid u otro proveedor por API HTTPS. "
            "Opcional: algunos relays permiten puerto 2525 (SMTP_RELAY_* no implementado aquí). "
            f"Detalle: {exc}"
        ) from exc


def _otp_log_only(to_email: str, code: str) -> None:
    print(
        f"\n[MAIL_OTP_LOG_ONLY] OTP para {to_email}: {code}\n"
        "                (desactiva MAIL_OTP_LOG_ONLY para enviar correo real)\n"
    )


def send_verification_email(to_email: str, code: str) -> None:
    """Intenta proveedores en orden hasta que uno funcione.

    Orden: SendGrid → Resend → Brevo → SMTP → consola.

    SendGrid: SENDGRID_API_KEY + SENDGRID_FROM_EMAIL (remitente verificado en Sender Authentication).
    MAIL_OTP_LOG_ONLY=true: solo imprime el OTP en logs (útil si ningún proveedor te deja enviar aún).
    """
    log_only = (os.getenv("MAIL_OTP_LOG_ONLY") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if log_only:
        _otp_log_only(to_email, code)
        return

    providers: list[tuple[str, Callable[[str, str], None]]] = []

    if (os.getenv("SENDGRID_API_KEY") or "").strip():
        providers.append(("SendGrid", _send_via_sendgrid))
    if (os.getenv("RESEND_API_KEY") or "").strip():
        providers.append(("Resend", _send_via_resend))
    if (os.getenv("BREVO_API_KEY") or "").strip():
        providers.append(("Brevo", _send_via_brevo))

    errors: list[str] = []
    for name, fn in providers:
        try:
            fn(to_email, code)
            return
        except RuntimeError as exc:
            errors.append(f"{name}: {exc}")

    if errors:
        joined = "\n---\n".join(errors)
        raise RuntimeError(
            "Ningún proveedor por API pudo enviar el correo (Render bloquea SMTP; las APIs usan HTTPS).\n"
            "Prueba: otra API key, remitente verificado, o dominio verificado en el panel del proveedor.\n\n"
            f"{joined}"
        )

    _send_via_smtp(to_email, code)
