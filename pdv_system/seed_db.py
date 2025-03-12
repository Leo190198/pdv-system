"""
Script para popular o banco de dados com dados iniciais
"""
from app import create_app, db
from app.models.user import User
from app.models.product import Product, StockMovement
from app.models.sale import Sale, SaleItem
from datetime import datetime, timedelta
import random
import json

app = create_app()

def seed_users():
    """Cria usuários iniciais"""
    print("Criando usuários...")
    
    # Administrador
    admin = User(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin"
    )
    
    # Vendedor
    vendedor = User(
        username="vendedor",
        email="vendedor@example.com",
        password="vendedor123",
        role="vendedor"
    )
    
    db.session.add(admin)
    db.session.add(vendedor)
    db.session.commit()
    
    print(f"Criados {User.query.count()} usuários")

def seed_products():
    """Cria produtos iniciais"""
    print("Criando produtos...")
    
    products_data = [
        {
            "name": "Notebook Dell Inspiron",
            "code": "DELL001",
            "description": "Notebook Dell Inspiron 15 polegadas, 8GB RAM, 256GB SSD",
            "price": 3499.99,
            "stock_quantity": 10,
            "category": "Informática"
        },
        {
            "name": "Monitor LG 24 polegadas",
            "code": "LG001",
            "description": "Monitor LG 24 polegadas Full HD IPS",
            "price": 899.99,
            "stock_quantity": 15,
            "category": "Informática"
        },
        {
            "name": "Teclado Mecânico Redragon",
            "code": "RD001",
            "description": "Teclado mecânico Redragon RGB",
            "price": 299.99,
            "stock_quantity": 20,
            "category": "Periféricos"
        },
        {
            "name": "Mouse Logitech G203",
            "code": "LOG001",
            "description": "Mouse gamer Logitech G203 RGB",
            "price": 149.99,
            "stock_quantity": 25,
            "category": "Periféricos"
        },
        {
            "name": "Headset Hyperx Cloud II",
            "code": "HYP001",
            "description": "Headset gamer Hyperx Cloud II 7.1",
            "price": 599.99,
            "stock_quantity": 8,
            "category": "Periféricos"
        },
        {
            "name": "Smartphone Samsung Galaxy S21",
            "code": "SAM001",
            "description": "Smartphone Samsung Galaxy S21 128GB",
            "price": 3999.99,
            "stock_quantity": 5,
            "category": "Celulares"
        },
        {
            "name": "iPhone 13 Pro",
            "code": "APP001",
            "description": "iPhone 13 Pro 256GB",
            "price": 7999.99,
            "stock_quantity": 3,
            "category": "Celulares"
        },
        {
            "name": "Smart TV LG 55 polegadas",
            "code": "LG002",
            "description": "Smart TV LG 55 polegadas 4K",
            "price": 2999.99,
            "stock_quantity": 7,
            "category": "TVs"
        },
        {
            "name": "Playstation 5",
            "code": "SONY001",
            "description": "Console Playstation 5 Digital Edition",
            "price": 4499.99,
            "stock_quantity": 2,
            "category": "Consoles"
        },
        {
            "name": "Xbox Series X",
            "code": "MS001",
            "description": "Console Xbox Series X 1TB",
            "price": 4299.99,
            "stock_quantity": 4,
            "category": "Consoles"
        },
        {
            "name": "Cadeira Gamer ThunderX3",
            "code": "TX001",
            "description": "Cadeira Gamer ThunderX3 ergonômica",
            "price": 1299.99,
            "stock_quantity": 6,
            "category": "Móveis"
        },
        {
            "name": "Mesa Gamer",
            "code": "MG001",
            "description": "Mesa Gamer com suporte para headset e porta-copos",
            "price": 599.99,
            "stock_quantity": 9,
            "category": "Móveis"
        },
        {
            "name": "Impressora HP LaserJet",
            "code": "HP001",
            "description": "Impressora HP LaserJet monocromática",
            "price": 999.99,
            "stock_quantity": 12,
            "category": "Impressoras"
        },
        {
            "name": "Roteador TP-Link Archer C6",
            "code": "TP001",
            "description": "Roteador TP-Link Archer C6 Dual Band AC1200",
            "price": 299.99,
            "stock_quantity": 18,
            "category": "Redes"
        },
        {
            "name": "SSD Kingston 480GB",
            "code": "KING001",
            "description": "SSD Kingston A400 480GB SATA 3",
            "price": 349.99,
            "stock_quantity": 30,
            "category": "Armazenamento"
        }
    ]
    
    # Primeiro, criamos e salvamos todos os produtos
    for product_data in products_data:
        product = Product(
            name=product_data["name"],
            code=product_data["code"],
            description=product_data["description"],
            price=product_data["price"],
            stock_quantity=product_data["stock_quantity"],
            category=product_data["category"]
        )
        db.session.add(product)
    
    # Fazemos commit para garantir que os produtos tenham IDs
    db.session.commit()
    
    # Agora, criamos os movimentos de estoque para cada produto
    for product in Product.query.all():
        movement = StockMovement(
            product_id=product.id,
            quantity=product.stock_quantity,
            movement_type="entrada",
            reference="Estoque inicial",
            notes="Cadastro inicial do produto"
        )
        db.session.add(movement)
    
    # Commit final para salvar os movimentos de estoque
    db.session.commit()
    
    print(f"Criados {Product.query.count()} produtos")

def seed_sales():
    """Cria vendas de exemplo"""
    print("Criando vendas...")
    
    # Obtém usuários e produtos
    users = User.query.all()
    products = Product.query.all()
    
    # Métodos de pagamento disponíveis
    payment_methods = ["dinheiro", "cartao_credito", "cartao_debito", "pix"]
    
    # Cria vendas dos últimos 30 dias
    for i in range(30):
        # Data da venda (de hoje até 30 dias atrás)
        sale_date = datetime.now() - timedelta(days=i)
        
        # Número de vendas por dia (1 a 5)
        num_sales = random.randint(1, 5)
        
        for j in range(num_sales):
            # Seleciona um vendedor aleatório
            user = random.choice(users)
            
            # Gera um número de venda
            sale_number = f"V{sale_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # Seleciona um método de pagamento aleatório
            payment_method = random.choice(payment_methods)
            
            # Cria detalhes de pagamento
            payment_details = {}
            if payment_method == "dinheiro":
                payment_details = {
                    "received": 0,  # Será calculado depois
                    "change": 0     # Será calculado depois
                }
            elif payment_method in ["cartao_credito", "cartao_debito"]:
                payment_details = {
                    "card_number": f"{random.randint(1000, 9999)}",
                    "installments": random.randint(1, 6) if payment_method == "cartao_credito" else 1
                }
            elif payment_method == "pix":
                payment_details = {
                    "pix_code": f"PIX{random.randint(100000, 999999)}"
                }
            
            # Cria a venda
            sale = Sale(
                sale_number=sale_number,
                user_id=user.id,
                payment_method=payment_method,
                payment_details=json.dumps(payment_details)
            )
            
            # Define a data de criação manualmente
            sale.created_at = sale_date
            
            db.session.add(sale)
            db.session.flush()  # Para obter o ID da venda
            
            # Número de itens na venda (1 a 5)
            num_items = random.randint(1, 5)
            
            # Seleciona produtos aleatórios para a venda
            sale_products = random.sample(products, num_items)
            
            total_amount = 0
            
            # Adiciona os itens à venda
            for product in sale_products:
                # Quantidade aleatória (1 a 3)
                quantity = random.randint(1, 3)
                
                # Verifica se há estoque suficiente
                if product.stock_quantity < quantity:
                    quantity = product.stock_quantity
                
                if quantity > 0:
                    # Cria o item da venda
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=product.price
                    )
                    
                    db.session.add(sale_item)
                    
                    # Atualiza o estoque
                    product.stock_quantity -= quantity
                    
                    # Soma ao total
                    total_amount += product.price * quantity
            
            # Atualiza o total da venda
            sale.total_amount = total_amount
            
            # Atualiza os detalhes de pagamento para dinheiro
            if payment_method == "dinheiro":
                received = total_amount + random.randint(0, 100)
                payment_details["received"] = received
                payment_details["change"] = received - total_amount
                sale.payment_details = json.dumps(payment_details)
    
    # Primeiro commit para salvar as vendas e itens
    db.session.commit()
    
    # Agora registramos os movimentos de estoque para cada venda
    for sale in Sale.query.all():
        for item in sale.items:
            # Registra o movimento de estoque
            movement = StockMovement(
                product_id=item.product_id,
                quantity=-item.quantity,
                movement_type="saída",
                reference=f"Venda {sale.sale_number}",
                notes=f"Venda para cliente"
            )
            db.session.add(movement)
    
    # Commit final para salvar os movimentos de estoque
    db.session.commit()
    
    print(f"Criadas {Sale.query.count()} vendas")

def seed_database():
    """Popula o banco de dados com dados iniciais"""
    with app.app_context():
        # Cria as tabelas
        db.create_all()
        
        # Verifica se já existem dados
        if User.query.count() > 0:
            print("O banco de dados já contém dados. Deseja limpar e recriar? (s/n)")
            response = input().lower()
            
            if response == 's':
                # Remove todos os dados
                db.drop_all()
                db.create_all()
                
                # Popula o banco de dados
                seed_users()
                seed_products()
                seed_sales()
                
                print("Banco de dados populado com sucesso!")
            else:
                print("Operação cancelada.")
        else:
            # Popula o banco de dados
            seed_users()
            seed_products()
            seed_sales()
            
            print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    seed_database()