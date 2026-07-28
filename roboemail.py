pip install openpyxl

import streamlit as st
import pandas as pd
import smtplib
import tempfile


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(
    page_title="Robô de E-mails",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Robô de Envio de E-mails")

st.write("Faça upload da planilha, da imagem e envie os e-mails em massa.")

# Dados do remetente
sender_email = st.text_input("E-mail do remetente")

sender_password = st.text_input(
    "Senha",
    type="password"
)

subject = st.text_input(
    "Assunto",
    value="Campanha Promocional"
)

body_html = st.text_area(
    "Corpo HTML",
    height=300,
    value="""
<html>
<body>

<h1>Promoção Especial!</h1>

<p>Confira nossa promoção exclusiva.</p>

<img src="cid:image1">

<p>Esperamos você!</p>

</body>
</html>
"""
)

excel_file = st.file_uploader(
    "Planilha Excel",
    type=["xlsx"]
)

image_file = st.file_uploader(
    "Imagem",
    type=["png","jpg","jpeg"]
)

if st.button("Enviar E-mails"):

    if excel_file is None:
        st.error("Selecione uma planilha.")
        st.stop()

    if image_file is None:
        st.error("Selecione uma imagem.")
        st.stop()

    if sender_email == "" or sender_password == "":
        st.error("Informe e-mail e senha.")
        st.stop()

    try:

        df = pd.read_excel(excel_file)

        if "Email" not in df.columns:
            st.error("A planilha precisa possuir uma coluna chamada 'Email'.")
            st.stop()

        recipients = df["Email"].dropna().tolist()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(image_file.read())
            image_path = tmp.name

        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        progress = st.progress(0)
        status = st.empty()

        total = len(recipients)

        enviados = 0

        for i, recipient in enumerate(recipients):

            try:

                msg = MIMEMultipart("related")

                msg["From"] = sender_email
                msg["To"] = recipient
                msg["Subject"] = subject

                body = MIMEMultipart("alternative")
                body.attach(MIMEText(body_html, "html"))

                msg.attach(body)

                with open(image_path, "rb") as f:
                    img = MIMEImage(f.read())

                    img.add_header(
                        "Content-ID",
                        "<image1>"
                    )

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

                enviados += 1

            except Exception as e:
                st.warning(f"Erro ao enviar para {recipient}: {e}")

            progress.progress((i + 1) / total)

            status.write(
                f"Enviados {i+1} de {total}"
            )

        server.quit()

        st.success(f"{enviados} e-mails enviados com sucesso!")

    except Exception as e:
        st.error(str(e))
