# Este arquivo permite que o diretório routes seja tratado como um pacote Python
# Importa todos os blueprints para facilitar o acesso
from app.routes.auth import auth
from app.routes.main import main
from app.routes.products import products
from app.routes.sales import sales
from app.routes.reports import reports