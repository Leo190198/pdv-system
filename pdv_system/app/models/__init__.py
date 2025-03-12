# Este arquivo permite que o diretório models seja tratado como um pacote Python
# Importa todos os modelos para facilitar o acesso
from app.models.user import User
from app.models.product import Product, StockMovement
from app.models.sale import Sale, SaleItem