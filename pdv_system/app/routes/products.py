from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, StockMovement
import os
from werkzeug.utils import secure_filename
from datetime import datetime

products = Blueprint('products', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@products.route('/products')
@login_required
def index():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.code.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    products_list = query.order_by(Product.name).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('products/index.html', 
                          products=products_list, 
                          search=search,
                          category=category,
                          categories=categories)

@products.route('/products/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity', 0)
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Validações
        if not name or not code or not price:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return render_template('products/create.html')
        
        # Verifica se o código já existe
        if Product.query.filter_by(code=code).first():
            flash('Este código de produto já está em uso.', 'danger')
            return render_template('products/create.html')
        
        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
        except ValueError:
            flash('Preço e quantidade devem ser valores numéricos.', 'danger')
            return render_template('products/create.html')
        
        # Criação do produto
        product = Product(
            name=name,
            code=code,
            price=price,
            stock_quantity=stock_quantity,
            description=description,
            category=category
        )
        
        # Upload de imagem
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Adiciona timestamp para evitar nomes duplicados
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Garante que o diretório existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                product.image_path = f"uploads/{filename}"
        
        db.session.add(product)
        
        # Registra o movimento de estoque inicial
        if stock_quantity > 0:
            movement = StockMovement(
                product_id=product.id,
                quantity=stock_quantity,
                movement_type='entrada',
                reference='Estoque inicial',
                notes='Cadastro inicial do produto'
            )
            db.session.add(movement)
        
        db.session.commit()
        
        flash(f'Produto {name} criado com sucesso!', 'success')
        return redirect(url_for('products.index'))
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('products/create.html', categories=categories)

@products.route('/products/<int:product_id>')
@login_required
def show(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Busca os movimentos de estoque do produto
    stock_movements = StockMovement.query.filter_by(product_id=product_id).order_by(StockMovement.created_at.desc()).all()
    
    return render_template('products/show.html', product=product, stock_movements=stock_movements)

@products.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        
        # Verifica se o código foi alterado
        new_code = request.form.get('code')
        if new_code != product.code:
            # Verifica se o novo código já existe
            if Product.query.filter_by(code=new_code).first():
                flash('Este código de produto já está em uso.', 'danger')
                return render_template('products/edit.html', product=product)
            product.code = new_code
        
        try:
            product.price = float(request.form.get('price'))
        except ValueError:
            flash('Preço deve ser um valor numérico.', 'danger')
            return render_template('products/edit.html', product=product)
        
        # Upload de imagem
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Adiciona timestamp para evitar nomes duplicados
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Garante que o diretório existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                
                # Remove a imagem antiga se existir
                if product.image_path:
                    old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_path.replace('uploads/', ''))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                product.image_path = f"uploads/{filename}"
        
        db.session.commit()
        flash(f'Produto {product.name} atualizado com sucesso!', 'success')
        return redirect(url_for('products.show', product_id=product.id))
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('products/edit.html', product=product, categories=categories)

@products.route('/products/<int:product_id>/stock', methods=['GET', 'POST'])
@login_required
def update_stock(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity'))
        except ValueError:
            flash('Quantidade deve ser um valor numérico.', 'danger')
            return redirect(url_for('products.show', product_id=product.id))
        
        movement_type = request.form.get('movement_type')
        reference = request.form.get('reference')
        notes = request.form.get('notes')
        
        # Ajusta a quantidade com base no tipo de movimento
        if movement_type == 'saída':
            quantity = -abs(quantity)  # Garante que seja negativo
            
            # Verifica se há estoque suficiente
            if (product.stock_quantity + quantity) < 0:
                flash('Estoque insuficiente para esta operação.', 'danger')
                return redirect(url_for('products.show', product_id=product.id))
        else:
            quantity = abs(quantity)  # Garante que seja positivo
        
        # Atualiza o estoque
        product.stock_quantity += quantity
        
        # Registra o movimento
        movement = StockMovement(
            product_id=product.id,
            quantity=quantity,
            movement_type=movement_type,
            reference=reference,
            notes=notes
        )
        
        db.session.add(movement)
        db.session.commit()
        
        flash(f'Estoque atualizado com sucesso! Novo estoque: {product.stock_quantity}', 'success')
        return redirect(url_for('products.show', product_id=product.id))
    
    return render_template('products/update_stock.html', product=product)

@products.route('/products/<int:product_id>/toggle', methods=['POST'])
@login_required
def toggle(product_id):
    product = Product.query.get_or_404(product_id)
    product.active = not product.active
    db.session.commit()
    
    status = 'ativado' if product.active else 'desativado'
    flash(f'Produto {product.name} {status} com sucesso!', 'success')
    return redirect(url_for('products.index'))

@products.route('/api/products/search')
@login_required
def search_api():
    term = request.args.get('term', '')
    
    if not term:
        return jsonify([])
    
    products_list = Product.query.filter(
        (Product.name.ilike(f'%{term}%')) | 
        (Product.code.ilike(f'%{term}%')),
        Product.active == True
    ).limit(10).all()
    
    results = []
    for product in products_list:
        results.append({
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'price': product.price,
            'stock': product.stock_quantity,
            'image': product.image_path
        })
    
    return jsonify(results)