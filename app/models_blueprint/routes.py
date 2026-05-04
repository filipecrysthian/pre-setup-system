"""
Blueprint de Modelos de Produto.
CRUD completo para cadastro de modelos (Notebook, Desktop, Tiny).
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import ProductModel, Item

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
    station = request.form.get('station', '').strip()

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

    model = ProductModel(name=name, product_type=product_type, station=station)
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
    station = request.form.get('station', '').strip()

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
    model.station = station
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


# --- Materiais por Modelo ---

@models_bp.route('/<int:model_id>/materials')
@login_required
def materials(model_id):
    """Lista todos os materiais vinculados a um modelo específico."""
    model = ProductModel.query.get_or_404(model_id)
    materials = Item.query.filter_by(product_model_id=model_id).order_by(Item.name).all()
    return render_template('models/materials.html', model=model, materials=materials)


@models_bp.route('/<int:model_id>/materials/create', methods=['POST'])
@login_required
def create_material(model_id):
    """Cadastra um novo material para o modelo."""
    model = ProductModel.query.get_or_404(model_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip() or None
    
    if not name:
        flash('O nome do material é obrigatório.', 'danger')
        return redirect(url_for('models_blueprint.materials', model_id=model_id))

    # Processar Upload de Foto
    image_filename = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename:
            filename = secure_filename(f"{model_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

    material = Item(
        name=name,
        description=description,
        product_model_id=model_id,
        category='GERAL',
        image_filename=image_filename,
        quantity=int(request.form.get('quantity', 1))
    )
    db.session.add(material)
    db.session.commit()

    flash(f'Material "{name}" adicionado ao modelo {model.name}!', 'success')
    return redirect(url_for('models_blueprint.materials', model_id=model_id))


@models_bp.route('/<int:model_id>/materials/edit/<int:item_id>', methods=['POST'])
@login_required
def edit_material(model_id, item_id):
    """Edita um material de um modelo."""
    material = Item.query.get_or_404(item_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip() or None

    if not name:
        flash('O nome do material é obrigatório.', 'danger')
        return redirect(url_for('models_blueprint.materials', model_id=model_id))

    # Processar nova foto se enviada
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename:
            # Remover antiga se existir
            if material.image_filename:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.image_filename)
                if os.path.exists(old_path):
                    try: os.remove(old_path)
                    except: pass
            
            filename = secure_filename(f"{model_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            material.image_filename = filename

    material.name = name
    material.description = description
    material.quantity = int(request.form.get('quantity', 1))
    db.session.commit()

    flash(f'Material "{name}" atualizado!', 'success')
    return redirect(url_for('models_blueprint.materials', model_id=model_id))


@models_bp.route('/<int:model_id>/materials/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_material(model_id, item_id):
    """Exclui um material de um modelo."""
    material = Item.query.get_or_404(item_id)
    name = material.name
    
    # Remover arquivo de imagem se existir
    if material.image_filename:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.image_filename)
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

    db.session.delete(material)
    db.session.commit()

    flash(f'Material "{name}" excluído com sucesso!', 'success')
    return redirect(url_for('models_blueprint.materials', model_id=model_id))
