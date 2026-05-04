"""
Blueprint de Itens/Materiais.
CRUD completo para cadastro de itens e materiais usados nos templates de pré setup.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Item

items_bp = Blueprint('items', __name__, url_prefix='/items')

# Categorias disponíveis
CATEGORIES = ['CABO', 'PCI', 'PERIFÉRICO', 'FERRAMENTA', 'CONSUMÍVEL', 'JIG', 'COMPONENTE', 'OUTRO']


@items_bp.route('/')
@login_required
def index():
    """Lista todos os itens cadastrados."""
    items = Item.query.order_by(Item.category, Item.name).all()
    return render_template('items/index.html', items=items, categories=CATEGORIES)


@items_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Cria um novo item/material."""
    name = request.form.get('name', '').strip()
    internal_code = request.form.get('internal_code', '').strip() or None
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip() or None

    # Validações
    if not name:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('items.index'))

    if category not in CATEGORIES:
        flash('Categoria inválida.', 'danger')
        return redirect(url_for('items.index'))

    # Verificar código interno duplicado
    if internal_code:
        existing = Item.query.filter_by(internal_code=internal_code).first()
        if existing:
            flash('Já existe um item com este código interno.', 'warning')
            return redirect(url_for('items.index'))

    item = Item(name=name, internal_code=internal_code, category=category, description=description)
    db.session.add(item)
    db.session.commit()

    flash(f'Item "{name}" criado com sucesso!', 'success')
    return redirect(url_for('items.index'))


@items_bp.route('/edit/<int:item_id>', methods=['POST'])
@login_required
def edit(item_id):
    """Edita um item existente."""
    item = Item.query.get_or_404(item_id)

    name = request.form.get('name', '').strip()
    internal_code = request.form.get('internal_code', '').strip() or None
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip() or None

    if not name:
        flash('O nome do item é obrigatório.', 'danger')
        return redirect(url_for('items.index'))

    if category not in CATEGORIES:
        flash('Categoria inválida.', 'danger')
        return redirect(url_for('items.index'))

    # Verificar duplicidade de código (excluindo o próprio)
    if internal_code:
        existing = Item.query.filter(
            Item.internal_code == internal_code,
            Item.id != item_id
        ).first()
        if existing:
            flash('Já existe outro item com este código interno.', 'warning')
            return redirect(url_for('items.index'))

    item.name = name
    item.internal_code = internal_code
    item.category = category
    item.description = description
    db.session.commit()

    flash(f'Item "{name}" atualizado com sucesso!', 'success')
    return redirect(url_for('items.index'))


@items_bp.route('/toggle/<int:item_id>', methods=['POST'])
@login_required
def toggle_status(item_id):
    """Ativa/desativa um item."""
    item = Item.query.get_or_404(item_id)
    item.is_active = not item.is_active
    db.session.commit()

    status_text = 'ativado' if item.is_active else 'desativado'
    flash(f'Item "{item.name}" {status_text} com sucesso!', 'success')
    return redirect(url_for('items.index'))
