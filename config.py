"""
Configurações do sistema PRÉ SETUP.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuração base do sistema."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pre-setup-secret-key-2024'
    
    # SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Diretório para PDFs gerados
    GENERATED_PDFS_DIR = os.path.join(basedir, 'generated_pdfs')
    
    # Diretório para uploads de imagens
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
    
    # Configurações padrão de email (podem ser sobrescritas pelo banco)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')
