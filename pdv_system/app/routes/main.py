from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.sale import Sale
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Estatísticas para o dashboard
    total_products = Product.query.count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= 5).count()
    
    # Vendas do dia
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_sales = Sale.query.filter(
        Sale.created_at.between(today_start, today_end),
        Sale.status == 'concluída'
    ).count()
    
    today_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.created_at.between(today_start, today_end),
        Sale.status == 'concluída'
    ).scalar() or 0
    
    # Vendas da semana
    week_start = today - timedelta(days=today.weekday())
    week_start = datetime.combine(week_start, datetime.min.time())
    
    week_sales = Sale.query.filter(
        Sale.created_at >= week_start,
        Sale.status == 'concluída'
    ).count()
    
    week_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.created_at >= week_start,
        Sale.status == 'concluída'
    ).scalar() or 0
    
    # Produtos com estoque baixo
    low_stock_items = Product.query.filter(Product.stock_quantity <= 5).all()
    
    # Últimas vendas
    recent_sales = Sale.query.filter_by(status='concluída').order_by(Sale.created_at.desc()).limit(5).all()
    
    return render_template('main/index.html',
                          total_products=total_products,
                          low_stock_products=low_stock_products,
                          today_sales=today_sales,
                          today_revenue=today_revenue,
                          week_sales=week_sales,
                          week_revenue=week_revenue,
                          low_stock_items=low_stock_items,
                          recent_sales=recent_sales)

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@main.route('/about')
def about():
    return render_template('main/about.html')