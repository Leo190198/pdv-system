from app import db
from datetime import datetime
import json

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_details = db.Column(db.Text, nullable=True)  # JSON com detalhes do pagamento
    status = db.Column(db.String(20), default='concluída')  # 'concluída', 'cancelada', 'pendente'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, sale_number, user_id, payment_method, payment_details=None, status='concluída'):
        self.sale_number = sale_number
        self.user_id = user_id
        self.payment_method = payment_method
        self.payment_details = payment_details
        self.status = status
    
    def add_item(self, product_id, quantity, unit_price):
        """Adiciona um item à venda"""
        item = SaleItem(
            sale_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        db.session.add(item)
        self.update_total()
        
        # Atualiza o estoque do produto
        from app.models.product import Product
        product = Product.query.get(product_id)
        if product:
            product.update_stock(-quantity)
    
    def update_total(self):
        """Atualiza o valor total da venda"""
        self.total_amount = sum(item.subtotal for item in self.items)
    
    def cancel(self):
        """Cancela a venda e devolve os produtos ao estoque"""
        if self.status != 'cancelada':
            self.status = 'cancelada'
            
            # Devolve os produtos ao estoque
            from app.models.product import Product
            for item in self.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.update_stock(item.quantity)
    
    def get_payment_details_dict(self):
        """Retorna os detalhes de pagamento como dicionário"""
        if self.payment_details:
            try:
                return json.loads(self.payment_details)
            except:
                return {}
        return {}
    
    def __repr__(self):
        return f'<Sale {self.sale_number}>'


class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    @property
    def subtotal(self):
        """Calcula o subtotal do item"""
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<SaleItem {self.id} of Sale {self.sale_id}>'