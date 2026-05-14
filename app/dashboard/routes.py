"""
Blueprint do Dashboard.
Exibe métricas e resumo geral do sistema.
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from sqlalchemy import func, desc
from datetime import datetime
from app.models import PreSetup, ProductModel, Item, User

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

    # 3. Volumetria por Linha (Bar chart)
    linha_query = db.session.query(PreSetup.linha, func.count(PreSetup.id)).group_by(PreSetup.linha).all()
    linha_labels = [row[0] or 'Desconhecida' for row in linha_query]
    linha_data = [row[1] for row in linha_query]

    # 4. Produtividade por Período (Últimos 14 dias com atividade)
    date_query = db.session.query(func.date(PreSetup.generated_at).label('data'), func.count(PreSetup.id)).group_by('data').order_by('data').limit(14).all()
    
    date_labels = []
    date_data = []
    for row in date_query:
        if row[0]:
            try:
                dt = datetime.strptime(row[0], '%Y-%m-%d')
                date_labels.append(dt.strftime('%d/%m'))
            except ValueError:
                date_labels.append(row[0])
            date_data.append(row[1])

    # 5. Ranking de Produtividade dos Usuários
    user_ranking = db.session.query(
        User.name, 
        func.count(PreSetup.id).label('total')
    ).join(PreSetup).group_by(User.id).order_by(desc('total')).limit(5).all()

    return render_template('dashboard.html',
                           total_setups=total_setups,
                           total_models=total_models,
                           total_items=total_items,
                           recent_setups=recent_setups,
                           linha_labels=linha_labels,
                           linha_data=linha_data,
                           date_labels=date_labels,
                           date_data=date_data,
                           user_ranking=user_ranking)
