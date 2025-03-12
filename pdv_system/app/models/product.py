from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)  # Estoque mínimo
    category = db.Column(db.String(50), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    sale_items = db.relationship('SaleItem', backref='product', lazy='dynamic')
    stock_movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    
    def __init__(self, name, code, price, stock_quantity=0, min_stock=5, description=None, category=None):
        self.name = name
        self.code = code
        self.price = price
        self.stock_quantity = stock_quantity
        self.min_stock = min_stock
        self.description = description
        self.category = category
    
    def update_stock(self, quantity):
        """Atualiza o estoque do produto (positivo para entrada, negativo para saída)"""
        self.stock_quantity += quantity
        
        # Registra o movimento de estoque
        from app import db
        movement = StockMovement(
            product_id=self.id,
            quantity=quantity,
            movement_type='entrada' if quantity > 0 else 'saída'
        )
        db.session.add(movement)
        db.session.flush()  # Garante que o movimento seja criado com um ID
    
    def is_low_stock(self):
        """Verifica se o produto está com estoque baixo"""
        return self.stock_quantity <= self.min_stock
    
    def __repr__(self):
        return f'<Product {self.name}>'


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saída'
    reference = db.Column(db.String(50), nullable=True)  # Referência (ex: número da venda, ajuste manual)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} of Product {self.product_id}>'