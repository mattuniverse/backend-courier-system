import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

MAIL_FROM = os.getenv("MAIL_FROM", "noreply@courierpro.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "CourierPro")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _booking_html(tracking_no: str, receiver_name: str, booking_date: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <tr><td style="background:#c0272d;padding:24px 32px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <span style="color:#fff;font-size:20px;font-weight:700;">CourierPro</span><br/>
                <span style="color:rgba(255,255,255,0.7);font-size:12px;">Courier &amp; Parcel Management</span>
              </td>
              <td align="right">
                <span style="background:#fff;color:#c0272d;font-size:11px;font-weight:600;padding:4px 12px;border-radius:999px;">Booked</span>
              </td>
            </tr>
          </table>
        </td></tr>

        <tr><td style="padding:28px 32px;">
          <p style="margin:0 0 4px;font-size:14px;color:#64748b;">Hello,</p>
          <p style="margin:0 0 20px;font-size:22px;font-weight:700;color:#0d0d0d;">{receiver_name}</p>
          <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.6;">
            Your parcel has been <strong>successfully booked</strong>. Below are your booking details.
          </p>

          <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:24px;">
            <tr><td style="padding:20px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Tracking No.</td>
                  <td style="font-size:13px;font-weight:700;color:#c0272d;font-family:monospace;">{tracking_no}</td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Receiver</td>
                  <td style="font-size:13px;font-weight:600;color:#0d0d0d;">{receiver_name}</td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Booking Date</td>
                  <td style="font-size:13px;font-weight:600;color:#0d0d0d;">{booking_date}</td>
                </tr>
              </table>
            </td></tr>
          </table>

          <p style="margin:0 0 0;font-size:14px;color:#475569;line-height:1.6;">
            You can track your parcel anytime using your tracking number.
          </p>
        </td></tr>

        <tr><td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:16px 32px;text-align:center;">
          <p style="margin:0;font-size:11px;color:#94a3b8;">CourierPro &middot; Automated Message</p>
          <p style="margin:4px 0 0;font-size:11px;color:#94a3b8;">This is an automated message. Do not reply to this email.</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def _status_html(tracking_no: str, status: str, location: str) -> str:
    status_display = status.replace("_", " ").title()
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <tr><td style="background:#c0272d;padding:24px 32px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <span style="color:#fff;font-size:20px;font-weight:700;">CourierPro</span><br/>
                <span style="color:rgba(255,255,255,0.7);font-size:12px;">Courier &amp; Parcel Management</span>
              </td>
              <td align="right">
                <span style="background:#fff;color:#c0272d;font-size:11px;font-weight:600;padding:4px 12px;border-radius:999px;">{status_display}</span>
              </td>
            </tr>
          </table>
        </td></tr>

        <tr><td style="padding:28px 32px;">
          <p style="margin:0 0 4px;font-size:14px;color:#64748b;">Hello,</p>
          <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.6;">
            Your parcel status has been updated.
          </p>

          <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:24px;">
            <tr><td style="padding:20px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Tracking No.</td>
                  <td style="font-size:13px;font-weight:700;color:#c0272d;font-family:monospace;">{tracking_no}</td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Status</td>
                  <td style="font-size:13px;font-weight:600;color:#0d0d0d;">{status_display}</td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="font-size:12px;color:#94a3b8;width:120px;">Location</td>
                  <td style="font-size:13px;font-weight:600;color:#0d0d0d;">{location or "N/A"}</td>
                </tr>
              </table>
            </td></tr>
          </table>

          <p style="margin:0 0 0;font-size:14px;color:#475569;line-height:1.6;">
            Thank you for using CourierPro.
          </p>
        </td></tr>

        <tr><td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:16px 32px;text-align:center;">
          <p style="margin:0;font-size:11px;color:#94a3b8;">CourierPro &middot; Automated Message</p>
          <p style="margin:4px 0 0;font-size:11px;color:#94a3b8;">This is an automated message. Do not reply to this email.</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_booking_confirmation(to_email: str, tracking_no: str, receiver_name: str, booking_date: str) -> bool:
    if not to_email:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Booking Confirmed — {tracking_no} | CourierPro"
        msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
        msg["To"] = to_email
        msg.attach(MIMEText(_booking_html(tracking_no, receiver_name, booking_date), "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(MAIL_FROM, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False


def send_status_update(to_email: str, tracking_no: str, status: str, location: str) -> bool:
    if not to_email:
        return False
    try:
        msg = MIMEMultipart("alternative")
        status_display = status.replace("_", " ").title()
        msg["Subject"] = f"Status Update — {status_display} | {tracking_no} | CourierPro"
        msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
        msg["To"] = to_email
        msg.attach(MIMEText(_status_html(tracking_no, status, location or ""), "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(MAIL_FROM, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False
