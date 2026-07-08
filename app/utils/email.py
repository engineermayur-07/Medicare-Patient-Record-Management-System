import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_otp_email(to_email: str, otp_code: str, user_name: str) -> bool:
    """Send OTP verification email. Returns True on success, False on failure."""
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_APP_PASSWORD']

    if not username or not password:
        current_app.logger.error('SMTP credentials not configured.')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'MediCare — Verify Your Email'
    msg['From'] = f'MediCare Hospital <{username}>'
    msg['To'] = to_email

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f9ff; margin: 0; padding: 0; }}
        .wrapper {{ max-width: 520px; margin: 40px auto; background: #ffffff;
                    border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #1D4ED8, #0F766E);
                   padding: 32px 40px; text-align: center; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 22px; font-weight: 600;
                      letter-spacing: -0.3px; }}
        .header p {{ color: rgba(255,255,255,0.75); margin: 4px 0 0; font-size: 14px; }}
        .body {{ padding: 36px 40px; }}
        .greeting {{ color: #0f172a; font-size: 16px; margin-bottom: 16px; }}
        .otp-box {{ background: #f0f9ff; border: 2px dashed #93c5fd; border-radius: 12px;
                    text-align: center; padding: 24px; margin: 24px 0; }}
        .otp-label {{ color: #64748b; font-size: 13px; text-transform: uppercase;
                      letter-spacing: 1px; margin-bottom: 10px; }}
        .otp-code {{ font-size: 42px; font-weight: 700; color: #1D4ED8;
                     letter-spacing: 10px; }}
        .info {{ color: #64748b; font-size: 14px; line-height: 1.6; }}
        .footer {{ background: #f8fafc; padding: 20px 40px; text-align: center;
                   color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="wrapper">
        <div class="header">
          <h1>✚ MediCare Hospital</h1>
          <p>Email Verification</p>
        </div>
        <div class="body">
          <p class="greeting">Hello <strong>{user_name}</strong>,</p>
          <p class="info">Use the one-time password below to verify your account. It expires in
             <strong>10 minutes</strong>.</p>
          <div class="otp-box">
            <div class="otp-label">Your OTP</div>
            <div class="otp-code">{otp_code}</div>
          </div>
          <p class="info">If you did not create an account with MediCare, please ignore this email.</p>
        </div>
        <div class="footer">
          &copy; MediCare Hospital &nbsp;·&nbsp; This is an automated message, please do not reply.
        </div>
      </div>
    </body>
    </html>
    """

    text_body = (
        f"Hello {user_name},\n\n"
        f"Your MediCare verification OTP is: {otp_code}\n"
        f"It expires in 10 minutes.\n\n"
        f"If you did not register, ignore this email.\n"
    )

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'],
                          current_app.config['MAIL_PORT']) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send OTP email: {e}')
        return False
