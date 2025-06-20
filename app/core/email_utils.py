import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "rizwanfarmfresh@gmail.com"
APP_PASSWORD = "vuouzdkhtoipvluv"

def send_otp_email(recipient_email: str, otp: str):
    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}\nIt is valid for 10 minute."

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.send_message(msg)

def send_order_email(
    recipient_email: str,
    order_number: str,
    total_amount: float,
    first_name: str,
    last_name: str,
    email_address: str,
    phone: str,
    delivery_type: str,
    shipping_address: str,
    shipping_state: str,
    shipping_zip: str,
    airport_name: str,
    items: list[dict]
):
    subject = f"🧾 New Order Placed - {order_number}"

    item_lines = "\n".join(
        f"- {item.get('quantity', 1)} x {item.get('type') or item.get('variation_name') or 'Item'} @ ${item.get('unit_price', 0):.2f}"
        for item in items
    )

    address_block = (
        f"{shipping_address}, {shipping_state} {shipping_zip}"
        if delivery_type == "doorstep" else f"Pickup from: {airport_name}"
    )

    body = f"""
A new order has been successfully placed.

👤 Customer:
- Name: {first_name} {last_name}
- Email: {email_address}
- Phone: {phone}

🚚 Delivery Type: {delivery_type.capitalize()}
📍 Address: {address_block}

🛒 Items:
{item_lines}

💰 Total Amount: ${total_amount:.2f}

📦 Order Number: {order_number}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.send_message(msg)

