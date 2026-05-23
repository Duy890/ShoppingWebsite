import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .config import settings


async def send_email(to: str, subject: str, html_body: str) -> None:
    """Send an HTML email via SMTP (async). Raises on failure."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_USER and SMTP_PASSWORD must be set in .env to send emails."
        )

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    message["To"] = to
    message.attach(MIMEText(html_body, "html", "utf-8"))

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        timeout=30,
    )


def build_reset_password_email(reset_url: str, user_name: str = "") -> str:
    """Return the HTML body for the password reset email."""
    name_line = f"<p>Hello {user_name},</p>" if user_name else "<p>Hello,</p>"
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head><meta charset="UTF-8" /></head>
    <body style="margin:0;padding:0;background:#f8fafc;font-family:sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;padding:40px 0;">
        <tr><td align="center">
          <table width="560" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:20px;overflow:hidden;
                        box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg,#f97316,#ea580c);
                         padding:32px 40px;text-align:center;">
                <p style="margin:0;font-size:22px;font-weight:900;color:#ffffff;
                           letter-spacing:-0.5px;">🛒 Electronics Store</p>
              </td>
            </tr>
            <!-- Body -->
            <tr>
              <td style="padding:40px;">
                {name_line}
                <p>We received a request to reset the password for your account.</p>
                <p>Click the button below to set a new password. This link is valid for
                   <strong>1 hour</strong>.</p>
                <div style="text-align:center;margin:32px 0;">
                  <a href="{reset_url}"
                     style="display:inline-block;background:#f97316;color:#ffffff;
                            font-size:16px;font-weight:700;padding:14px 36px;
                            border-radius:999px;text-decoration:none;">
                    Reset Password
                  </a>
                </div>
                <p style="color:#94a3b8;font-size:13px;">
                  If you did not request this, you can safely ignore this email.
                  Your password will not change.
                </p>
                <p style="color:#94a3b8;font-size:13px;">
                  Or copy this link into your browser:<br/>
                  <a href="{reset_url}" style="color:#f97316;word-break:break-all;">{reset_url}</a>
                </p>
              </td>
            </tr>
            <!-- Footer -->
            <tr>
              <td style="padding:24px 40px;background:#f1f5f9;
                         text-align:center;color:#94a3b8;font-size:12px;">
                © Electronics Store · This is an automated message, please do not reply.
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """


def build_verify_email_change_email(verify_url: str, new_email: str, user_name: str = "") -> str:
    """Return the HTML body for the email-change verification email."""
    name_line = f"<p>Hello {user_name},</p>" if user_name else "<p>Hello,</p>"
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head><meta charset="UTF-8" /></head>
    <body style="margin:0;padding:0;background:#f8fafc;font-family:sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;padding:40px 0;">
        <tr><td align="center">
          <table width="560" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:20px;overflow:hidden;
                        box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <tr>
              <td style="background:linear-gradient(135deg,#f97316,#ea580c);
                         padding:32px 40px;text-align:center;">
                <p style="margin:0;font-size:22px;font-weight:900;color:#ffffff;">🛒 Electronics Store</p>
              </td>
            </tr>
            <tr>
              <td style="padding:40px;">
                {name_line}
                <p>We received a request to change your account email to:</p>
                <p style="text-align:center;font-size:18px;font-weight:700;color:#f97316;">
                  {new_email}
                </p>
                <p>Click the button below to confirm. This link is valid for <strong>1 hour</strong>.</p>
                <div style="text-align:center;margin:32px 0;">
                  <a href="{verify_url}"
                     style="display:inline-block;background:#f97316;color:#ffffff;
                            font-size:16px;font-weight:700;padding:14px 36px;
                            border-radius:999px;text-decoration:none;">
                    Confirm New Email
                  </a>
                </div>
                <p style="color:#94a3b8;font-size:13px;">
                  If you did not request this change, please ignore this email.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:24px 40px;background:#f1f5f9;
                         text-align:center;color:#94a3b8;font-size:12px;">
                © Electronics Store · Automated message.
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """
