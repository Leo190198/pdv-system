from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.active:
                flash('Esta conta está desativada. Entre em contato com o administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Apenas administradores podem registrar novos usuários
    if not current_user.is_admin():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'vendedor')
        
        # Validações
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso.', 'danger')
            return render_template('auth/register.html')
        
        # Criação do usuário
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuário {username} criado com sucesso!', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/register.html')

@auth.route('/users')
@login_required
def users():
    # Apenas administradores podem ver a lista de usuários
    if not current_user.is_admin():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('auth/users.html', users=users)

@auth.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Apenas administradores podem editar usuários
    if not current_user.is_admin():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role', 'vendedor')
        user.active = 'active' in request.form
        
        # Atualiza a senha apenas se uma nova senha for fornecida
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/edit_user.html', user=user)

@auth.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    # Apenas administradores podem ativar/desativar usuários
    if not current_user.is_admin():
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Não permite desativar o próprio usuário
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
        return redirect(url_for('auth.users'))
    
    user.active = not user.active
    db.session.commit()
    
    status = 'ativado' if user.active else 'desativado'
    flash(f'Usuário {user.username} {status} com sucesso!', 'success')
    return redirect(url_for('auth.users'))