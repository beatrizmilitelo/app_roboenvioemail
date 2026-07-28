import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_bulk_email_with_embedded_image(
    sender_email,
    sender_password,
    df,
    subject,
    body_html,
    image_path
):

    recipients = df["Email"].dropna().tolist()

    # SMTP do Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    for recipient in recipients:

        msg = MIMEMultipart("related")
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = subject

        body = MIMEMultipart("alternative")
        body.attach(MIMEText(body_html, "html", "utf-8"))
        msg.attach(body)

        with open(image_path, "rb") as f:

            img = MIMEImage(f.read())

            img.add_header("Content-ID", "<image1>")
            img.add_header(
                "Content-Disposition",
                "inline",
                filename="imagem.jpg"
            )

            msg.attach(img)

        server.sendmail(
            sender_email,
            recipient,
            msg.as_string()
        )

        print(f"E-mail enviado para {recipient}")

    server.quit()
