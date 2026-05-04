"""
Blueprint de Geração de Pré Setup e Histórico.
Gerencia o fluxo de geração, PDF e histórico de pré setups.
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, \
    send_file, current_app, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ProductModel, TemplateItem, PreSetup, PreSetupItem, Item, EmailConfig
from app.setup_requests.pdf_generator import generate_pre_setup_pdf
from app.setup_requests.email_sender import send_pre_setup_email

setup_bp = Blueprint('setup_requests', __name__, url_prefix='/setup')


@setup_bp.route('/generate')
@login_required
def generate_select():
    """Tela para selecionar o modelo e iniciar a geração do pré setup."""
    models = ProductModel.query.filter_by(is_active=True).order_by(ProductModel.name).all()
    return render_template('setup/generate_select.html', models=models)

@setup_bp.route('/generate/redirect')
@login_required
def generate_form_redirect():
    """Redireciona para o formulário com os parâmetros do modal."""
    model_id = request.args.get('model_id')
    num_bays = request.args.get('num_bays', 1)
    station = request.args.get('station', 'FCT')
    
    if not model_id:
        flash('Modelo é obrigatório.', 'danger')
        return redirect(url_for('setup_requests.generate_select'))
        
    return redirect(url_for('setup_requests.generate_form', 
                            model_id=model_id, 
                            num_bays=num_bays, 
                            station=station))


@setup_bp.route('/generate/<int:model_id>')
@login_required
def generate_form(model_id):
    """Carrega o formulário de preenchimento com os itens do template."""
    model = ProductModel.query.get_or_404(model_id)
    template_items = TemplateItem.query.filter_by(product_model_id=model_id).all()
    materials = Item.query.filter_by(product_model_id=model_id, is_active=True).order_by(Item.name).all()

    num_bays = request.args.get('num_bays', 1)
    station = request.args.get('station', model.station or 'FCT')

    return render_template('setup/generate_form.html',
                           model=model,
                           template_items=template_items,
                           materials=materials,
                           num_bays=num_bays,
                           station=station)


@setup_bp.route('/generate/<int:model_id>/submit', methods=['POST'])
@login_required
def generate_submit(model_id):
    """Processa o formulário e gera o pré setup com PDF."""
    model = ProductModel.query.get_or_404(model_id)
    materials = Item.query.filter_by(product_model_id=model_id, is_active=True).order_by(Item.name).all()

    # Coletar dados do formulário
    setup_items_data = []
    has_pending = False
    all_filled = True

    for material in materials:
        status = request.form.get(f'status_{material.id}', '').strip()
        observation = request.form.get(f'observation_{material.id}', '').strip()

        # Validar que todos os itens têm status
        if not status:
            all_filled = False
            break

        # Validar observação obrigatória para PENDENTE
        if status == 'PENDENTE' and not observation:
            flash(f'O item "{material.name}" com status PENDENTE requer uma observação.', 'danger')
            return redirect(url_for('setup_requests.generate_form', model_id=model_id))

        if status == 'PENDENTE':
            has_pending = True

        setup_items_data.append({
            'material': material,
            'status': status,
            'observation': observation
        })

    if not all_filled and materials:
        flash('Todos os itens devem ter um status preenchido.', 'danger')
        return redirect(url_for('setup_requests.generate_form', model_id=model_id))

    # Determinar status geral
    overall_status = 'COM PENDÊNCIA' if has_pending else 'CONCLUÍDO'

    # Criar registro do pré setup
    pre_setup = PreSetup(
        product_model_id=model_id,
        user_id=current_user.id,
        num_bays=int(request.form.get('num_bays', 1)),
        station=request.form.get('station', 'FCT'),
        overall_status=overall_status
    )
    db.session.add(pre_setup)
    db.session.flush()  # Obter o ID antes do commit

    # Criar itens do pré setup
    for data in setup_items_data:
        mat = data['material']
        setup_item = PreSetupItem(
            pre_setup_id=pre_setup.id,
            item_id=mat.id,
            group_area=mat.category or 'GERAL',
            quantity=mat.quantity,
            status=data['status'],
            observation=data['observation'] or None
        )
        db.session.add(setup_item)

    # Gerar PDF
    pdf_filename = f"pre_setup_{model.name.replace(' ', '_')}_{pre_setup.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(current_app.config['GENERATED_PDFS_DIR'], pdf_filename)

    try:
        generate_pre_setup_pdf(pre_setup, model, setup_items_data, current_user, pdf_path)
        pre_setup.pdf_filename = pdf_filename
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        db.session.rollback()
        return redirect(url_for('setup_requests.generate_form', model_id=model_id))

    db.session.commit()
    flash(f'Pré Setup gerado com sucesso! Status: {overall_status}', 'success')
    return redirect(url_for('setup_requests.detail', setup_id=pre_setup.id))


@setup_bp.route('/history')
@login_required
def history():
    """Histórico de todos os pré setups gerados."""
    setups = PreSetup.query.order_by(PreSetup.generated_at.desc()).all()
    return render_template('setup/history.html', setups=setups)


@setup_bp.route('/detail/<int:setup_id>')
@login_required
def detail(setup_id):
    """Detalhes de um pré setup gerado."""
    setup = PreSetup.query.get_or_404(setup_id)
    setup_items = PreSetupItem.query.filter_by(pre_setup_id=setup_id).all()

    # Contadores para resumo
    total_items = len(setup_items)
    total_ok = sum(1 for i in setup_items if i.status == 'OK')
    total_pending = sum(1 for i in setup_items if i.status == 'PENDENTE')
    total_na = sum(1 for i in setup_items if i.status == 'N/A')

    return render_template('setup/detail.html',
                           setup=setup,
                           setup_items=setup_items,
                           total_items=total_items,
                           total_ok=total_ok,
                           total_pending=total_pending,
                           total_na=total_na)


@setup_bp.route('/download/<int:setup_id>')
@login_required
def download_pdf(setup_id):
    """Download do PDF de um pré setup."""
    setup = PreSetup.query.get_or_404(setup_id)

    if not setup.pdf_filename:
        flash('PDF não encontrado para este pré setup.', 'danger')
        return redirect(url_for('setup_requests.history'))

    pdf_path = os.path.join(current_app.config['GENERATED_PDFS_DIR'], setup.pdf_filename)

    if not os.path.exists(pdf_path):
        flash('Arquivo PDF não encontrado no servidor.', 'danger')
        return redirect(url_for('setup_requests.history'))

    return send_file(pdf_path, as_attachment=True, download_name=setup.pdf_filename)


@setup_bp.route('/send-email/<int:setup_id>', methods=['POST'])
@login_required
def send_email(setup_id):
    """Envia o PDF por email para os destinatários configurados."""
    setup = PreSetup.query.get_or_404(setup_id)

    if not setup.pdf_filename:
        flash('PDF não encontrado. Gere o PDF antes de enviar por email.', 'danger')
        return redirect(url_for('setup_requests.detail', setup_id=setup_id))

    pdf_path = os.path.join(current_app.config['GENERATED_PDFS_DIR'], setup.pdf_filename)

    if not os.path.exists(pdf_path):
        flash('Arquivo PDF não encontrado no servidor.', 'danger')
        return redirect(url_for('setup_requests.detail', setup_id=setup_id))

    # Obter configuração de email
    email_config = EmailConfig.query.first()
    if not email_config:
        flash('Configuração de email não encontrada. Configure o email primeiro.', 'warning')
        return redirect(url_for('email_config.index'))

    recipients = email_config.get_recipients_list()
    if not recipients:
        flash('Nenhum destinatário configurado. Configure os destinatários primeiro.', 'warning')
        return redirect(url_for('email_config.index'))

    # Enviar email
    model = ProductModel.query.get(setup.product_model_id)
    subject = f'PRÉ SETUP - {model.name}'
    body = (
        'Segue em anexo o documento de pré setup gerado automaticamente.\n\n'
        'Este é um email automático, favor não responder.'
    )

    try:
        send_pre_setup_email(email_config, recipients, subject, body, pdf_path)
        setup.email_sent = True
        setup.email_sent_at = datetime.now()
        db.session.commit()
        flash('Email enviado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar email: {str(e)}', 'danger')

    return redirect(url_for('setup_requests.detail', setup_id=setup_id))
