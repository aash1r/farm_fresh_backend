import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL_ADDRESS = "rizwanfarmfresh@gmail.com"
APP_PASSWORD = "vuouzdkhtoipvluv"
# EMAIL_ADDRESS = "asheressani@gmail.com"
# APP_PASSWORD = "pkhn nfdv urgx gwkd"


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
    items: list[dict],
    csv_attachment_path: str = None
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

📎 Please find the detailed orders report attached as a CSV file.
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach CSV if provided
    if csv_attachment_path and os.path.exists(csv_attachment_path):
        try:
            with open(csv_attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            
            # Get filename from path
            filename = os.path.basename(csv_attachment_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            print(f"CSV attachment added: {filename}")
        except Exception as e:
            print(f"Failed to attach CSV: {e}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.send_message(msg)

