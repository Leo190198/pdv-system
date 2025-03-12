from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import csv
import io
import json
from sqlalchemy import func, desc, asc
from ..models.product import Product
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from ..extensions import db

reports = Blueprint('reports', __name__, url_prefix='/reports')

@reports.route('/')
@login_required
def index():
    return render_template('reports/index.html')

@reports.route('/sales')
@login_required
def sales_report():
    # Obter parâmetros de filtro
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'))
    group_by = request.args.get('group_by', 'day')
    
    # Converter strings para objetos datetime
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
    
    # Consulta base para vendas no período
    sales_query = Sale.query.filter(
        Sale.created_at.between(start_date_obj, end_date_obj),
        Sale.status == 'concluída'
    )
    
    # Total de vendas e receita
    total_sales = sales_query.count()
    total_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.created_at.between(start_date_obj, end_date_obj),
        Sale.status == 'concluída'
    ).scalar() or 0
    
    # Dados agrupados por período
    sales_data = []
    
    if group_by == 'day':
        # Agrupar por dia
        results = db.session.query(
            func.date(Sale.created_at).label('date'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            Sale.created_at.between(start_date_obj, end_date_obj),
            Sale.status == 'concluída'
        ).group_by(func.date(Sale.created_at)).order_by(func.date(Sale.created_at)).all()
        
        for result in results:
            # Verificar se result.date é um objeto datetime ou string
            if hasattr(result.date, 'strftime'):
                date_str = result.date.strftime('%d/%m/%Y')
            else:
                # Se for string, converter para datetime primeiro
                try:
                    date_obj = datetime.strptime(str(result.date), '%Y-%m-%d')
                    date_str = date_obj.strftime('%d/%m/%Y')
                except:
                    # Fallback se não conseguir converter
                    date_str = str(result.date)
            
            sales_data.append({
                'date': date_str,
                'count': result.count,
                'total': float(result.total) if result.total else 0
            })
    
    elif group_by == 'week':
        # Agrupar por semana
        results = db.session.query(
            func.strftime('%Y-%W', Sale.created_at).label('week'),
            func.min(func.date(Sale.created_at)).label('start_date'),
            func.max(func.date(Sale.created_at)).label('end_date'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            Sale.created_at.between(start_date_obj, end_date_obj),
            Sale.status == 'concluída'
        ).group_by(func.strftime('%Y-%W', Sale.created_at)).order_by(func.strftime('%Y-%W', Sale.created_at)).all()
        
        for result in results:
            # Verificar se start_date e end_date são objetos datetime ou strings
            if hasattr(result.start_date, 'strftime') and hasattr(result.end_date, 'strftime'):
                start_date_str = result.start_date.strftime('%d/%m')
                end_date_str = result.end_date.strftime('%d/%m/%Y')
            else:
                # Se forem strings, converter para datetime primeiro
                try:
                    start_date_obj = datetime.strptime(str(result.start_date), '%Y-%m-%d')
                    end_date_obj = datetime.strptime(str(result.end_date), '%Y-%m-%d')
                    start_date_str = start_date_obj.strftime('%d/%m')
                    end_date_str = end_date_obj.strftime('%d/%m/%Y')
                except:
                    # Fallback se não conseguir converter
                    start_date_str = str(result.start_date)
                    end_date_str = str(result.end_date)
            
            sales_data.append({
                'date': f"{start_date_str} - {end_date_str}",
                'count': result.count,
                'total': float(result.total) if result.total else 0
            })
    
    elif group_by == 'month':
        # Agrupar por mês
        results = db.session.query(
            func.strftime('%Y-%m', Sale.created_at).label('month'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            Sale.created_at.between(start_date_obj, end_date_obj),
            Sale.status == 'concluída'
        ).group_by(func.strftime('%Y-%m', Sale.created_at)).order_by(func.strftime('%Y-%m', Sale.created_at)).all()
        
        for result in results:
            try:
                # Tentar converter a string para datetime
                month_year = datetime.strptime(str(result.month), '%Y-%m')
                date_str = month_year.strftime('%B/%Y')
            except:
                # Fallback se não conseguir converter
                date_str = str(result.month)
            
            sales_data.append({
                'date': date_str,
                'count': result.count,
                'total': float(result.total) if result.total else 0
            })
    
    # Dados de métodos de pagamento
    payment_results = db.session.query(
        Sale.payment_method,
        func.count(Sale.id).label('count'),
        func.sum(Sale.total_amount).label('total')
    ).filter(
        Sale.created_at.between(start_date_obj, end_date_obj),
        Sale.status == 'concluída'
    ).group_by(Sale.payment_method).all()
    
    payment_data = []
    for result in payment_results:
        method_name = {
            'dinheiro': 'Dinheiro',
            'cartao_credito': 'Cartão de Crédito',
            'cartao_debito': 'Cartão de Débito',
            'pix': 'PIX'
        }.get(result.payment_method, result.payment_method)
        
        payment_data.append({
            'method': method_name,
            'count': result.count,
            'total': float(result.total) if result.total else 0
        })
    
    return render_template(
        'reports/sales.html',
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
        sales_data=sales_data,
        payment_data=payment_data,
        total_sales=total_sales,
        total_revenue=total_revenue
    )

@reports.route('/products')
@login_required
def products_report():
    # Obter parâmetros de filtro
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'))
    limit = int(request.args.get('limit', 10))
    
    # Converter strings para objetos datetime
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
    
    # Produtos mais vendidos (por quantidade)
    top_products = db.session.query(
        Product,
        func.sum(SaleItem.quantity).label('quantity_sold'),
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_revenue')
    ).join(
        SaleItem, SaleItem.product_id == Product.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.created_at.between(start_date_obj, end_date_obj),
        Sale.status == 'concluída'
    ).group_by(
        Product.id
    ).order_by(
        desc('quantity_sold')
    ).limit(limit).all()
    
    # Formatar dados para o template
    products_data = []
    for product, quantity_sold, total_revenue in top_products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'quantity_sold': int(quantity_sold),
            'total_revenue': float(total_revenue)
        })
    
    # Produtos com estoque baixo
    low_stock_products = Product.query.filter(
        Product.active == True,
        Product.stock_quantity <= Product.min_stock
    ).order_by(
        asc(Product.stock_quantity)
    ).all()
    
    return render_template(
        'reports/products.html',
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        products_data=products_data,
        low_stock_products=low_stock_products
    )

@reports.route('/stock')
@login_required
def stock_report():
    # Obter parâmetros de filtro
    selected_category = request.args.get('category', '')
    order_by = request.args.get('order_by', 'name')
    order_dir = request.args.get('order_dir', 'asc')
    
    # Consulta base
    query = Product.query
    
    # Filtrar por categoria se especificado
    if selected_category:
        query = query.filter(Product.category == selected_category)
    
    # Ordenar resultados
    if order_by == 'name':
        query = query.order_by(asc(Product.name) if order_dir == 'asc' else desc(Product.name))
    elif order_by == 'stock':
        query = query.order_by(asc(Product.stock_quantity) if order_dir == 'asc' else desc(Product.stock_quantity))
    elif order_by == 'price':
        query = query.order_by(asc(Product.price) if order_dir == 'asc' else desc(Product.price))
    
    # Executar consulta
    products = query.all()
    
    # Calcular estatísticas
    total_products = len(products)
    total_stock_value = sum(product.price * product.stock_quantity for product in products)
    avg_price = sum(product.price for product in products) / total_products if total_products > 0 else 0
    
    # Obter todas as categorias distintas
    categories = db.session.query(Product.category).filter(Product.category != None).distinct().order_by(Product.category).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template(
        'reports/stock.html',
        products=products,
        total_products=total_products,
        total_stock_value=total_stock_value,
        avg_price=avg_price,
        categories=categories,
        selected_category=selected_category,
        order_by=order_by,
        order_dir=order_dir
    )

@reports.route('/export/sales/<format>')
@login_required
def export_sales(format):
    if format not in ['csv']:
        flash('Formato de exportação não suportado.', 'danger')
        return redirect(url_for('reports.sales_report'))
    
    # Obter parâmetros de filtro
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    # Converter strings para objetos datetime
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
    
    # Consulta para vendas no período
    sales = Sale.query.filter(
        Sale.created_at.between(start_date_obj, end_date_obj)
    ).order_by(Sale.created_at).all()
    
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['ID', 'Número da Venda', 'Data', 'Vendedor', 'Método de Pagamento', 'Total', 'Status'])
        
        # Dados
        for sale in sales:
            writer.writerow([
                sale.id,
                sale.sale_number,
                sale.created_at.strftime('%d/%m/%Y %H:%M'),
                sale.seller.username if sale.seller else 'N/A',
                {
                    'dinheiro': 'Dinheiro',
                    'cartao_credito': 'Cartão de Crédito',
                    'cartao_debito': 'Cartão de Débito',
                    'pix': 'PIX'
                }.get(sale.payment_method, sale.payment_method),
                f"{sale.total_amount:.2f}",
                sale.status.capitalize()
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'vendas_{start_date}_a_{end_date}.csv'
        )

@reports.route('/export/products/<format>')
@login_required
def export_products(format):
    if format not in ['csv']:
        flash('Formato de exportação não suportado.', 'danger')
        return redirect(url_for('reports.products_report'))
    
    # Consulta para todos os produtos
    products = Product.query.order_by(Product.name).all()
    
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['ID', 'Código', 'Nome', 'Categoria', 'Preço', 'Estoque', 'Estoque Mínimo', 'Valor Total', 'Status'])
        
        # Dados
        for product in products:
            writer.writerow([
                product.id,
                product.code,
                product.name,
                product.category or 'N/A',
                f"{product.price:.2f}",
                product.stock_quantity,
                product.min_stock,
                f"{product.price * product.stock_quantity:.2f}",
                'Ativo' if product.active else 'Inativo'
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'produtos_{datetime.now().strftime("%Y%m%d")}.csv'
        )