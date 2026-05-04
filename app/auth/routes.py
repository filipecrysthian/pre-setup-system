"""
Blueprint de Autenticação.
Gerencia login, logout e segurança do sistema.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Tela de login do sistema."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Sua conta está desativada. Contate o administrador.', 'danger')
                return render_template('login.html')

            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Email ou senha inválidos.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Realiza logout do sistema."""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
