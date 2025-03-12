import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pdv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração para alertas de estoque baixo
    LOW_STOCK_THRESHOLD = 5
    
    # Configurações de autenticação
    SESSION_TYPE = 'filesystem'
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    