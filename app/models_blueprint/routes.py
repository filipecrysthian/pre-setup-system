"""
Blueprint de Modelos de Produto.
CRUD completo para cadastro de modelos (Notebook, Desktop, Tiny).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import ProductModel

models_bp = Blueprint('models_blueprint', __name__, url_prefix='/models')

# Tipos de produto disponíveis
PRODUCT_TYPES = ['Notebook', 'Desktop', 'Tiny']


@models_bp.route('/')
@login_required
def index():
    """Lista todos os modelos cadastrados."""
    models = ProductModel.query.order_by(ProductModel.name).all()
    return render_template('models/index.html', models=models, product_types=PRODUCT_TYPES)


@models_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Cria um novo modelo de produto."""
    name = request.form.get('name', '').strip()
    product_type = request.form.get('product_type', '').strip()

    # Validações
    if not name:
        flash('O nome do modelo é obrigatório.', 'danger')
        return redirect(url_for('models_blueprint.index'))

    if product_type not in PRODUCT_TYPES:
        flash('Tipo de produto inválido.', 'danger')
        return redirect(url_for('models_blueprint.index'))

    # Verificar se já existe
    existing = ProductModel.query.filter_by(name=name).first()
    if existing:
        flash('Já existe um modelo com este nome.', 'warning')
        return redirect(url_for('models_blueprint.index'))

    model = ProductModel(name=name, product_type=product_type)
    db.session.add(model)
    db.session.commit()

    flash(f'Modelo "{name}" criado com sucesso!', 'success')
    return redirect(url_for('models_blueprint.index'))


@models_bp.route('/edit/<int:model_id>', methods=['POST'])
@login_required
def edit(model_id):
    """Edita um modelo existente."""
    model = ProductModel.query.get_or_404(model_id)

    name = request.form.get('name', '').strip()
    product_type = request.form.get('product_type', '').strip()

    if not name:
        flash('O nome do modelo é obrigatório.', 'danger')
        return redirect(url_for('models_blueprint.index'))

    if product_type not in PRODUCT_TYPES:
        flash('Tipo de produto inválido.', 'danger')
        return redirect(url_for('models_blueprint.index'))

    # Verificar duplicidade (excluindo o próprio modelo)
    existing = ProductModel.query.filter(
        ProductModel.name == name,
        ProductModel.id != model_id
    ).first()
    if existing:
        flash('Já existe outro modelo com este nome.', 'warning')
        return redirect(url_for('models_blueprint.index'))

    model.name = name
    model.product_type = product_type
    db.session.commit()

    flash(f'Modelo "{name}" atualizado com sucesso!', 'success')
    return redirect(url_for('models_blueprint.index'))


@models_bp.route('/toggle/<int:model_id>', methods=['POST'])
@login_required
def toggle_status(model_id):
    """Ativa/desativa um modelo."""
    model = ProductModel.query.get_or_404(model_id)
    model.is_active = not model.is_active
    db.session.commit()

    status_text = 'ativado' if model.is_active else 'desativado'
    flash(f'Modelo "{model.name}" {status_text} com sucesso!', 'success')
    return redirect(url_for('models_blueprint.index'))
