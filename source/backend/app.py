#!/usr/bin/env python3
"""海富通基金营销平台后端"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

from config import Config

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

from models import db
db.init_app(app)

with app.app_context():
    db.create_all()
    from models import User
    if User.query.count() == 0:
        from routes.auth import seed_users
        from routes.audit import seed_audit_data
        from routes.team import seed_team_members
        seed_users()
        seed_audit_data()
        seed_team_members()
        print('=== Initial data seeded ===')

from routes.fund import fund_bp
from routes.copy import copy_bp
from routes.library import library_bp
from routes.team import team_bp
from routes.audit import audit_bp
from routes.auth import auth_bp

app.register_blueprint(fund_bp, url_prefix='/api/fund')
app.register_blueprint(copy_bp, url_prefix='/api/copy')
app.register_blueprint(library_bp, url_prefix='/api/library')
app.register_blueprint(team_bp, url_prefix='/api/team')
app.register_blueprint(audit_bp, url_prefix='/api/audit')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def index():
    try:
        return send_from_directory('../frontend', 'index.html')
    except:
        return jsonify({'name': '基金营销平台', 'status': 'running', 'ai': 'minimax'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'ai': 'minimax', 'data': 'eastmoney', 'time': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])