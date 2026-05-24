"""用户认证API路由"""
from flask import Blueprint, jsonify, request, session
from datetime import datetime
import hashlib
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import db, User

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash

def seed_users():
    """初始化用户数据"""
    if User.query.count() > 0:
        return
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@hftf.com',
            'password': 'admin123',
            'name': '系统管理员',
            'role': 'admin',
            'department': '技术部'
        },
        {
            'username': 'manager1',
            'email': 'manager1@hftf.com',
            'password': 'manager123',
            'name': '张经理',
            'role': 'manager',
            'department': '市场部'
        },
        {
            'username': 'user1',
            'email': 'user1@hftf.com',
            'password': 'user123',
            'name': '李文案',
            'role': 'user',
            'department': '销售部'
        }
    ]
    
    for u in users_data:
        user = User(
            username=u['username'],
            email=u['email'],
            password_hash=hash_password(u['password']),
            name=u['name'],
            role=u['role'],
            department=u['department']
        )
        db.session.add(user)
    
    db.session.commit()

def ensure_demo_user():
    """确保演示账号存在且密码固定"""
    user = User.query.filter_by(username='ai4leader').first()
    if not user:
        user = User(
            username='ai4leader',
            email='ai4leader@fund-intelligence.local',
            name='AI4Leader',
            role='admin',
            department='演示账号'
        )
        db.session.add(user)
    user.password_hash = hash_password('ai4leader')
    user.status = 'active'
    db.session.commit()
    return user

@auth_bp.route('/register', methods=['POST'])
def register():
    return jsonify({'success': False, 'error': '请联系管理员申请账号密码'}), 403

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'}), 400

        if username != 'ai4leader' or password != 'ai4leader':
            return jsonify({'success': False, 'error': '用户名或密码错误，请重新输入'}), 401
        
        user = ensure_demo_user()
        
        if user.status == 'inactive':
            return jsonify({'success': False, 'error': '账号已被禁用'}), 403
        
        user.last_login = datetime.now()
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['name'] = user.name
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'department': user.department,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else ''
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': '已退出登录'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/status', methods=['GET'])
def get_status():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': True, 'logged_in': False})
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({'success': True, 'logged_in': False})
        
        return jsonify({
            'success': True,
            'logged_in': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'department': user.department
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
def list_users():
    try:
        if session.get('role') not in ['admin', 'manager']:
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in users]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>/role', methods=['POST'])
def update_user_role(user_id):
    try:
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': '仅管理员可修改角色'}), 403
        
        data = request.get_json() or {}
        new_role = data.get('role', '')
        
        if new_role not in ['admin', 'manager', 'user']:
            return jsonify({'success': False, 'error': '无效的角色'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({'success': True, 'message': '角色已更新'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>/status', methods=['POST'])
def update_user_status(user_id):
    try:
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': '仅管理员可修改状态'}), 403
        
        data = request.get_json() or {}
        new_status = data.get('status', '')
        
        if new_status not in ['active', 'inactive']:
            return jsonify({'success': False, 'error': '无效的状态'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        user.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': '状态已更新'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
