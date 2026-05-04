"""
Módulo de envio de email.
Envia PDFs de pré setup por SMTP com anexo.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os


def send_pre_setup_email(email_config, recipients, subject, body, pdf_path):
    """
    Envia email com PDF anexado.

    Args:
        email_config: Objeto EmailConfig com configurações SMTP
        recipients: Lista de emails destinatários
        subject: Assunto do email
        body: Corpo do email (texto)
        pdf_path: Caminho completo do PDF a anexar

    Raises:
        Exception: Se houver erro no envio
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'Arquivo PDF não encontrado: {pdf_path}')

    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = email_config.sender_email
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    # Corpo do email
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Anexar PDF
    with open(pdf_path, 'rb') as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 'attachment',
            filename=os.path.basename(pdf_path)
        )
        msg.attach(pdf_attachment)

    # Enviar via SMTP
    try:
        server = smtplib.SMTP(email_config.smtp_host, email_config.smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_config.username, email_config.password)
        server.sendmail(email_config.sender_email, recipients, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise Exception('Falha na autenticação SMTP. Verifique usuário e senha.')
    except smtplib.SMTPConnectError:
        raise Exception('Não foi possível conectar ao servidor SMTP.')
    except Exception as e:
        raise Exception(f'Erro ao enviar email: {str(e)}')
