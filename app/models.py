"""
Modelos do banco de dados - PRÉ SETUP System.
Define todas as tabelas e relacionamentos do sistema.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


# --- Callback do Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário pelo ID para o Flask-Login."""
    return User.query.get(int(user_id))


# --- Modelo de Usuário ---
class User(UserMixin, db.Model):
    """Usuários do sistema."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile = db.Column(db.String(50), nullable=False, default='Engenharia')  # Admin, Engenharia
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relacionamento com pré setups gerados
    setups = db.relationship('PreSetup', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Gera hash da senha."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica a senha contra o hash armazenado."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        """Propriedade necessária pelo Flask-Login."""
        return self.is_active_user

    def __repr__(self):
        return f'<User {self.name}>'


# --- Modelo de Produto ---
class ProductModel(db.Model):
    """Modelos de produtos (Notebook, Desktop, Tiny)."""
    __tablename__ = 'product_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    product_type = db.Column(db.String(50), nullable=False)  # Notebook, Desktop, Tiny
    station = db.Column(db.String(50), nullable=True)  # FCT, SHELL, IO
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relacionamentos
    template_items = db.relationship('TemplateItem', backref='product_model', lazy='dynamic',
                                     cascade='all, delete-orphan')
    items = db.relationship('Item', backref='product_model', lazy='dynamic',
                            cascade='all, delete-orphan')
    setups = db.relationship('PreSetup', backref='product_model', lazy='dynamic')

    def __repr__(self):
        return f'<ProductModel {self.name}>'


# --- Modelo de Item/Material ---
class Item(db.Model):
    """Itens e materiais disponíveis para os templates."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey('product_models.id'), nullable=True) # Temporarily nullable for migration
    name = db.Column(db.String(200), nullable=False)
    internal_code = db.Column(db.String(50), unique=False, nullable=True) # Removing unique constraint for simplicity
    category = db.Column(db.String(50), nullable=False, default='GERAL')
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Item {self.name}>'


# --- Template de Pré Setup ---
class TemplateItem(db.Model):
    """Itens que compõem o template padrão de pré setup de cada modelo."""
    __tablename__ = 'template_items'

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey('product_models.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    group_area = db.Column(db.String(50), nullable=False)  # FCT, IO, SHELL, PERIFÉRICO, OUTROS
    quantity = db.Column(db.Integer, nullable=False, default=1)
    observation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relacionamento com Item
    item = db.relationship('Item', backref='template_items')

    def __repr__(self):
        return f'<TemplateItem Model:{self.product_model_id} Item:{self.item_id}>'


# --- Pré Setup Gerado ---
class PreSetup(db.Model):
    """Registros de pré setups gerados."""
    __tablename__ = 'pre_setups'

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey('product_models.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    num_bays = db.Column(db.Integer, nullable=False, default=1)
    station = db.Column(db.String(50), nullable=False)  # FCT, SHELL, IO
    generated_at = db.Column(db.DateTime, default=datetime.now)
    overall_status = db.Column(db.String(50), nullable=False)  # CONCLUÍDO, COM PENDÊNCIA
    pdf_filename = db.Column(db.String(300), nullable=True)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)

    # Relacionamento com itens preenchidos
    setup_items = db.relationship('PreSetupItem', backref='pre_setup', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PreSetup {self.id} - Model:{self.product_model_id}>'


# --- Itens do Pré Setup Gerado ---
class PreSetupItem(db.Model):
    """Itens individuais preenchidos em cada pré setup gerado."""
    __tablename__ = 'pre_setup_items'

    id = db.Column(db.Integer, primary_key=True)
    pre_setup_id = db.Column(db.Integer, db.ForeignKey('pre_setups.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    group_area = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False)  # OK, PENDENTE, N/A
    observation = db.Column(db.Text, nullable=True)

    # Relacionamento com Item
    item = db.relationship('Item', backref='setup_items')

    def __repr__(self):
        return f'<PreSetupItem Setup:{self.pre_setup_id} Item:{self.item_id} Status:{self.status}>'


# --- Configuração de Email ---
class EmailConfig(db.Model):
    """Configuração de email SMTP e destinatários."""
    __tablename__ = 'email_config'

    id = db.Column(db.Integer, primary_key=True)
    smtp_host = db.Column(db.String(200), nullable=False, default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, nullable=False, default=587)
    username = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(200), nullable=True)
    sender_email = db.Column(db.String(200), nullable=True)
    recipients = db.Column(db.Text, nullable=True)  # Lista de emails separados por ;
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def get_recipients_list(self):
        """Retorna lista de destinatários."""
        if self.recipients:
            return [r.strip() for r in self.recipients.split(';') if r.strip()]
        return []

    def __repr__(self):
        return f'<EmailConfig {self.smtp_host}:{self.smtp_port}>'
