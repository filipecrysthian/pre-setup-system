"""
Blueprint do Dashboard.
Exibe métricas e resumo geral do sistema.
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.models import PreSetup, ProductModel, Item

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Página principal - Dashboard com métricas do sistema."""
    total_setups = PreSetup.query.count()
    total_models = ProductModel.query.filter_by(is_active=True).count()
    total_items = Item.query.filter_by(is_active=True).count()

    # Últimos 10 pré setups gerados
    recent_setups = PreSetup.query.order_by(PreSetup.generated_at.desc()).limit(10).all()

    return render_template('dashboard.html',
                           total_setups=total_setups,
                           total_models=total_models,
                           total_items=total_items,
                           recent_setups=recent_setups)
