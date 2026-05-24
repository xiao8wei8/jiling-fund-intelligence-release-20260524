"""数据库模型"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(80))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    department = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'department': self.department,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M') if self.last_login else ''
        }

class TeamMember(db.Model):
    """团队成员表"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))
    department = db.Column(db.String(50))
    avatar = db.Column(db.String(1))
    avatar_color = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    joined_at = db.Column(db.Date, default=datetime.now().date)
    
    stats_generated = db.Column(db.Integer, default=0)
    stats_used = db.Column(db.Integer, default=0)
    stats_approved = db.Column(db.Integer, default=0)
    stats_rejected = db.Column(db.Integer, default=0)
    
    perf_this_month = db.Column(db.Integer, default=0)
    perf_last_month = db.Column(db.Integer, default=0)
    perf_rank = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone or '',
            'role': self.role or '',
            'department': self.department or '',
            'avatar': self.avatar or self.name[0] if self.name else '?',
            'avatar_color': self.avatar_color or 'linear-gradient(135deg, #0B5FBD, #1A78DB)',
            'status': self.status,
            'joined_at': self.joined_at.strftime('%Y-%m-%d') if self.joined_at else '',
            'stats': {
                'generated': self.stats_generated,
                'used': self.stats_used,
                'approved': self.stats_approved,
                'rejected': self.stats_rejected
            },
            'performance': {
                'this_month': self.perf_this_month,
                'last_month': self.perf_last_month,
                'rank': self.perf_rank
            }
        }

class GeneratedContent(db.Model):
    """生成的文案内容表"""
    __tablename__ = 'generated_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    fund_code = db.Column(db.String(20))
    fund_name = db.Column(db.String(100))
    format_type = db.Column(db.String(50))  # 朋友圈文案、一句话推荐等
    content = db.Column(db.Text)
    style = db.Column(db.String(50))
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'))
    
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    used_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    creator = db.relationship('User', foreign_keys=[created_by])
    member = db.relationship('TeamMember', foreign_keys=[member_id])
    approver = db.relationship('User', foreign_keys=[approved_by])

class FundFavorite(db.Model):
    """基金收藏表"""
    __tablename__ = 'fund_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(20), nullable=False)
    fund_name = db.Column(db.String(100))
    fund_type = db.Column(db.String(50))
    category = db.Column(db.String(20))  # focus, hold, all
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'fund_code', name='unique_user_fund'),)

class AuditLog(db.Model):
    """审核日志表"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('generated_contents.id'))
    action = db.Column(db.String(20))  # approve, reject, edit
    comment = db.Column(db.Text)
    
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    content = db.relationship('GeneratedContent', foreign_keys=[content_id])
    operator = db.relationship('User', foreign_keys=[operator_id])

class SystemSettings(db.Model):
    """系统设置表"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)