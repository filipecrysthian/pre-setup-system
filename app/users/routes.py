"""
Blueprint de Gestão de Usuários.
CRUD de usuários com perfis Admin e Engenharia.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User

users_bp = Blueprint('users', __name__, url_prefix='/users')

PROFILES = ['Admin', 'Engenharia']


@users_bp.route('/')
@login_required
def index():
    """Lista todos os usuários."""
    users = User.query.order_by(User.name).all()
    return render_template('users/index.html', users=users, profiles=PROFILES)


@users_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Cria um novo usuário."""
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    profile = request.form.get('profile', 'Engenharia')

    if not name or not username or not password:
        flash('Nome, username e senha são obrigatórios.', 'danger')
        return redirect(url_for('users.index'))

    if profile not in PROFILES:
        flash('Perfil inválido.', 'danger')
        return redirect(url_for('users.index'))

    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        flash('Já existe um usuário com este username.', 'warning')
        return redirect(url_for('users.index'))

    if email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Já existe um usuário com este email.', 'warning')
            return redirect(url_for('users.index'))

    user = User(name=name, username=username, email=email or None, profile=profile)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'Usuário "{name}" criado com sucesso!', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/edit/<int:user_id>', methods=['POST'])
@login_required
def edit(user_id):
    """Edita um usuário existente."""
    user = User.query.get_or_404(user_id)
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    profile = request.form.get('profile', 'Engenharia')

    if not name or not username:
        flash('Nome e username são obrigatórios.', 'danger')
        return redirect(url_for('users.index'))

    existing_username = User.query.filter(User.username == username, User.id != user_id).first()
    if existing_username:
        flash('Já existe outro usuário com este username.', 'warning')
        return redirect(url_for('users.index'))

    if email:
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('Já existe outro usuário com este email.', 'warning')
            return redirect(url_for('users.index'))

    user.name = name
    user.username = username
    user.email = email or None
    user.profile = profile
    if password:
        user.set_password(password)
    db.session.commit()

    flash(f'Usuário "{name}" atualizado com sucesso!', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_status(user_id):
    """Ativa/desativa um usuário."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
        return redirect(url_for('users.index'))
    user.is_active_user = not user.is_active_user
    db.session.commit()
    status_text = 'ativado' if user.is_active_user else 'desativado'
    flash(f'Usuário "{user.name}" {status_text} com sucesso!', 'success')
    return redirect(url_for('users.index'))
