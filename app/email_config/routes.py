"""
Blueprint de Configuração de Email.
Gerencia configurações SMTP e lista de destinatários.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import EmailConfig

email_bp = Blueprint('email_config', __name__, url_prefix='/email')


@email_bp.route('/')
@login_required
def index():
    """Tela de configuração de email."""
    config = EmailConfig.query.first()
    return render_template('email/index.html', config=config)


@email_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Salva as configurações de email."""
    smtp_host = request.form.get('smtp_host', '').strip()
    smtp_port = request.form.get('smtp_port', 587, type=int)
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    sender_email = request.form.get('sender_email', '').strip()
    recipients = request.form.get('recipients', '').strip()

    if not smtp_host:
        flash('O host SMTP é obrigatório.', 'danger')
        return redirect(url_for('email_config.index'))

    config = EmailConfig.query.first()
    if config:
        config.smtp_host = smtp_host
        config.smtp_port = smtp_port
        config.username = username
        # Só atualiza a senha se uma nova foi fornecida
        if password:
            config.password = password
        config.sender_email = sender_email
        config.recipients = recipients
    else:
        config = EmailConfig(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            username=username,
            password=password,
            sender_email=sender_email,
            recipients=recipients
        )
        db.session.add(config)

    db.session.commit()
    flash('Configurações de email salvas com sucesso!', 'success')
    return redirect(url_for('email_config.index'))
