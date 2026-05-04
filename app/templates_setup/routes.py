"""
Blueprint de Templates de Pré Setup.
Gerencia os templates padrão de itens por modelo de produto.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import ProductModel, Item, TemplateItem

templates_bp = Blueprint('templates_setup', __name__, url_prefix='/templates')

# Grupos/Áreas disponíveis
GROUP_AREAS = ['FCT', 'IO', 'SHELL', 'PERIFÉRICO', 'OUTROS']


@templates_bp.route('/')
@login_required
def index():
    """Lista todos os modelos que possuem templates."""
    models = ProductModel.query.filter_by(is_active=True).order_by(ProductModel.name).all()
    return render_template('templates/index.html', models=models)


@templates_bp.route('/manage/<int:model_id>')
@login_required
def manage(model_id):
    """Gerencia o template de um modelo específico."""
    model = ProductModel.query.get_or_404(model_id)
    template_items = TemplateItem.query.filter_by(product_model_id=model_id).all()
    available_items = Item.query.filter_by(is_active=True).order_by(Item.category, Item.name).all()

    return render_template('templates/manage.html',
                           model=model,
                           template_items=template_items,
                           available_items=available_items,
                           group_areas=GROUP_AREAS)


@templates_bp.route('/add-item/<int:model_id>', methods=['POST'])
@login_required
def add_item(model_id):
    """Adiciona um item ao template do modelo."""
    model = ProductModel.query.get_or_404(model_id)

    item_id = request.form.get('item_id', type=int)
    group_area = request.form.get('group_area', '').strip()
    quantity = request.form.get('quantity', 1, type=int)
    observation = request.form.get('observation', '').strip() or None

    # Validações
    if not item_id:
        flash('Selecione um item.', 'danger')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    if group_area not in GROUP_AREAS:
        flash('Grupo/Área inválido.', 'danger')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    if quantity < 1:
        flash('Quantidade deve ser no mínimo 1.', 'danger')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    # Verificar se item já existe no template
    existing = TemplateItem.query.filter_by(
        product_model_id=model_id,
        item_id=item_id,
        group_area=group_area
    ).first()
    if existing:
        flash('Este item já existe neste grupo do template.', 'warning')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    template_item = TemplateItem(
        product_model_id=model_id,
        item_id=item_id,
        group_area=group_area,
        quantity=quantity,
        observation=observation
    )
    db.session.add(template_item)
    db.session.commit()

    flash('Item adicionado ao template com sucesso!', 'success')
    return redirect(url_for('templates_setup.manage', model_id=model_id))


@templates_bp.route('/remove-item/<int:template_item_id>', methods=['POST'])
@login_required
def remove_item(template_item_id):
    """Remove um item do template."""
    template_item = TemplateItem.query.get_or_404(template_item_id)
    model_id = template_item.product_model_id

    db.session.delete(template_item)
    db.session.commit()

    flash('Item removido do template com sucesso!', 'success')
    return redirect(url_for('templates_setup.manage', model_id=model_id))


@templates_bp.route('/edit-item/<int:template_item_id>', methods=['POST'])
@login_required
def edit_item(template_item_id):
    """Edita um item do template."""
    template_item = TemplateItem.query.get_or_404(template_item_id)
    model_id = template_item.product_model_id

    group_area = request.form.get('group_area', '').strip()
    quantity = request.form.get('quantity', 1, type=int)
    observation = request.form.get('observation', '').strip() or None

    if group_area not in GROUP_AREAS:
        flash('Grupo/Área inválido.', 'danger')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    if quantity < 1:
        flash('Quantidade deve ser no mínimo 1.', 'danger')
        return redirect(url_for('templates_setup.manage', model_id=model_id))

    template_item.group_area = group_area
    template_item.quantity = quantity
    template_item.observation = observation
    db.session.commit()

    flash('Item do template atualizado com sucesso!', 'success')
    return redirect(url_for('templates_setup.manage', model_id=model_id))
