from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.sale import Sale, SaleItem
import json
from datetime import datetime
import uuid

sales = Blueprint('sales', __name__)

@sales.route('/sales')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Sale.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    # Filtro por data
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date = datetime.combine(start_date, datetime.min.time())
        query = query.filter(Sale.created_at >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Sale.created_at <= end_date)
    
    sales_list = query.order_by(Sale.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('sales/index.html', 
                          sales=sales_list,
                          status=status,
                          start_date=request.args.get('start_date', ''),
                          end_date=request.args.get('end_date', ''))

@sales.route('/sales/new')
@login_required
def new():
    # Gera um número único para a venda
    sale_number = f"V{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Passa a data atual para o template
    current_datetime = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    return render_template('sales/new.html', sale_number=sale_number, current_datetime=current_datetime)

@sales.route('/sales', methods=['POST'])
@login_required
def create():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
    
    sale_number = data.get('sale_number')
    items = data.get('items', [])
    payment_method = data.get('payment_method')
    payment_details = data.get('payment_details', {})
    
    # Validações
    if not sale_number or not items or not payment_method:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    
    # Verifica se o número da venda já existe
    if Sale.query.filter_by(sale_number=sale_number).first():
        return jsonify({'success': False, 'message': 'Número de venda já existe'}), 400
    
    # Cria a venda
    sale = Sale(
        sale_number=sale_number,
        user_id=current_user.id,
        payment_method=payment_method,
        payment_details=json.dumps(payment_details) if payment_details else None
    )
    
    db.session.add(sale)
    db.session.flush()  # Para obter o ID da venda
    
    total_amount = 0
    
    # Adiciona os itens à venda
    for item_data in items:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        product = Product.query.get(product_id)
        if not product:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Produto ID {product_id} não encontrado'}), 400
        
        # Verifica se há estoque suficiente
        if product.stock_quantity < quantity:
            db.session.rollback()
            return jsonify({
                'success': False, 
                'message': f'Estoque insuficiente para o produto {product.name}. Disponível: {product.stock_quantity}'
            }), 400
        
        # Cria o item da venda
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price
        )
        
        db.session.add(sale_item)
        
        # Atualiza o estoque
        product.stock_quantity -= quantity
        
        # Soma ao total
        total_amount += (product.price * quantity)
    
    # Atualiza o total da venda
    sale.total_amount = total_amount
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Venda realizada com sucesso!',
        'sale_id': sale.id,
        'sale_number': sale.sale_number
    })

@sales.route('/sales/<int:sale_id>')
@login_required
def show(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/show.html', sale=sale)

@sales.route('/sales/<int:sale_id>/receipt')
@login_required
def receipt(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/receipt.html', sale=sale)

@sales.route('/sales/<int:sale_id>/cancel', methods=['POST'])
@login_required
def cancel(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    if sale.status == 'cancelada':
        flash('Esta venda já está cancelada.', 'warning')
        return redirect(url_for('sales.show', sale_id=sale.id))
    
    # Cancela a venda (isso devolverá os produtos ao estoque)
    sale.cancel()
    db.session.commit()
    
    flash('Venda cancelada com sucesso!', 'success')
    return redirect(url_for('sales.show', sale_id=sale.id))