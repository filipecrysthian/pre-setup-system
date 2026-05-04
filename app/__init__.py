"""
Factory do aplicativo Flask - PRÉ SETUP System.
Sistema de monitoramento e geração de documentos de PRÉ SETUP
para o time de Engenharia de Teste.
"""
import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """Cria e configura a instância do Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Garantir que diretórios necessários existam
    os.makedirs(app.config['GENERATED_PDFS_DIR'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar o sistema.'
    login_manager.login_message_category = 'warning'

    # Registrar blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.models_blueprint.routes import models_bp
    app.register_blueprint(models_bp)

    from app.items.routes import items_bp
    app.register_blueprint(items_bp)

    from app.templates_setup.routes import templates_bp
    app.register_blueprint(templates_bp)

    from app.setup_requests.routes import setup_bp
    app.register_blueprint(setup_bp)

    from app.email_config.routes import email_bp
    app.register_blueprint(email_bp)

    from app.users.routes import users_bp
    app.register_blueprint(users_bp)

    # Criar tabelas e usuário admin inicial
    with app.app_context():
        from app.models import User
        db.create_all()
        _create_admin_user()

    return app


def _create_admin_user():
    """Cria o usuário administrador inicial se não existir."""
    from app.models import User
    admin = User.query.filter_by(email='admin@presetup.com').first()
    if not admin:
        admin = User(
            name='Administrador',
            email='admin@presetup.com',
            profile='Admin',
            is_active_user=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
