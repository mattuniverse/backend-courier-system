import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

PRIMARY = colors.HexColor("#c0272d")
DARK = colors.HexColor("#0d0d0d")


def generate_booking_receipt(
    tracking_no: str,
    sender_name: str,
    sender_phone: str,
    receiver_name: str,
    receiver_phone: str,
    receiver_address: str,
    parcel_type: str,
    weight_kg: float,
    cost: float,
    booking_date: str,
    pickup_branch: str = "",
    delivery_branch: str = "",
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 30 * mm

    c.setFillColor(PRIMARY)
    c.rect(0, h - 35 * mm, w, 35 * mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin, h - 20 * mm, "CourierPro")
    c.setFont("Helvetica", 9)
    c.drawString(margin, h - 27 * mm, "Courier & Parcel Management")

    c.setFont("Helvetica", 9)
    c.drawRightString(w - margin, h - 20 * mm, "BOOKING RECEIPT")
    c.drawRightString(w - margin, h - 27 * mm, booking_date)

    y = h - 50 * mm

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Tracking Number")
    y -= 8 * mm
    c.setFont("Courier-Bold", 16)
    c.setFillColor(PRIMARY)
    c.drawString(margin, y, tracking_no)
    y -= 4 * mm

    barcode = code128.Code128(tracking_no, barWidth=0.5 * mm, barHeight=12 * mm)
    barcode.drawOn(c, margin, y - 12 * mm)
    y -= 18 * mm

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(0.5)
    c.line(margin, y, w - margin, y)
    y -= 10 * mm

    def _draw_section(title, fields):
        nonlocal y
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, title)
        y -= 7 * mm
        for label, value in fields:
            c.setFillColor(colors.HexColor("#64748b"))
            c.setFont("Helvetica", 9)
            c.drawString(margin + 5 * mm, y, label)
            c.setFillColor(DARK)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(margin + 40 * mm, y, str(value or "N/A"))
            y -= 5.5 * mm
        y -= 3 * mm

    _draw_section("SENDER INFORMATION", [
        ("Name", sender_name),
        ("Phone", sender_phone),
    ])

    _draw_section("RECEIVER INFORMATION", [
        ("Name", receiver_name),
        ("Phone", receiver_phone),
        ("Address", receiver_address),
    ])

    _draw_section("SHIPMENT DETAILS", [
        ("Type", parcel_type.title()),
        ("Weight", f"{weight_kg} kg"),
        ("Pickup", pickup_branch or "N/A"),
        ("Delivery", delivery_branch or "N/A"),
    ])

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(margin, y, w - margin, y)
    y -= 10 * mm

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "COST BREAKDOWN")
    y -= 7 * mm

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 9)
    c.drawString(margin + 5 * mm, y, "Total Cost")
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 40 * mm, y, f"PHP {cost:,.2f}")
    y -= 12 * mm

    c.setStrokeColor(PRIMARY)
    c.setLineWidth(1)
    c.line(margin, y, w - margin, y)
    y -= 10 * mm

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(w / 2, y, "This is a computer-generated receipt. No signature required.")
    y -= 5 * mm
    c.drawCentredString(w / 2, y, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.save()
    return buf.getvalue()
