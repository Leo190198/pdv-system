from flask import Flask
from config import Config
from datetime import datetime
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicialização das extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Registro dos blueprints
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.products import products as products_blueprint
    app.register_blueprint(products_blueprint)
    
    from app.routes.sales import sales as sales_blueprint
    app.register_blueprint(sales_blueprint)
    
    from app.routes.reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint)
    
    # Adiciona contexto global para os templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app