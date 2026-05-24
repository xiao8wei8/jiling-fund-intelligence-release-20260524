"""团队管理API路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import db, TeamMember, User, GeneratedContent

team_bp = Blueprint('team', __name__)

def seed_team_members():
    """初始化团队成员数据"""
    if TeamMember.query.count() > 0:
        return
    
    members_data = [
        {
            "name": "李明远", "email": "limingyuan@haitong.com", "phone": "138****1234",
            "role": "高级销售经理", "department": "销售部", "avatar": "李",
            "avatar_color": "linear-gradient(135deg, #002E6D, #1A78DB)",
            "stats_generated": 89, "stats_used": 234, "stats_approved": 87, "stats_rejected": 2,
            "perf_this_month": 12, "perf_last_month": 15, "perf_rank": 1
        },
        {
            "name": "王晓华", "email": "wangxiaohua@haitong.com", "phone": "139****5678",
            "role": "销售经理", "department": "销售部", "avatar": "王",
            "avatar_color": "linear-gradient(135deg, #2B7A4B, #4AA876)",
            "stats_generated": 56, "stats_used": 178, "stats_approved": 52, "stats_rejected": 4,
            "perf_this_month": 8, "perf_last_month": 10, "perf_rank": 2
        },
        {
            "name": "张伟", "email": "zhangwei@haitong.com", "phone": "137****9012",
            "role": "渠道经理", "department": "渠道部", "avatar": "张",
            "avatar_color": "linear-gradient(135deg, #8B5A2B, #C4873D)",
            "stats_generated": 34, "stats_used": 112, "stats_approved": 31, "stats_rejected": 3,
            "perf_this_month": 5, "perf_last_month": 7, "perf_rank": 3
        },
        {
            "name": "陈静", "email": "chenjing@haitong.com", "phone": "136****3456",
            "role": "客服专员", "department": "客服部", "avatar": "陈",
            "avatar_color": "linear-gradient(135deg, #6B3A8B, #9B5BBB)",
            "stats_generated": 23, "stats_used": 89, "stats_approved": 22, "stats_rejected": 1,
            "perf_this_month": 3, "perf_last_month": 4, "perf_rank": 4
        },
        {
            "name": "刘洋", "email": "liuyang@haitong.com", "phone": "135****7890",
            "role": "销售主管", "department": "销售部", "avatar": "刘",
            "avatar_color": "linear-gradient(135deg, #1A5A8B, #2A8ADB)",
            "stats_generated": 12, "stats_used": 45, "stats_approved": 11, "stats_rejected": 1,
            "perf_this_month": 0, "perf_last_month": 2, "perf_rank": 5, "status": "inactive"
        },
        {
            "name": "赵敏", "email": "zhaomin@haitong.com", "phone": "134****2345",
            "role": "客户经理", "department": "销售部", "avatar": "赵",
            "avatar_color": "linear-gradient(135deg, #8B3A5A, #BB5A8A)",
            "stats_generated": 18, "stats_used": 56, "stats_approved": 17, "stats_rejected": 1,
            "perf_this_month": 4, "perf_last_month": 3, "perf_rank": 6
        }
    ]
    
    for m in members_data:
        member = TeamMember(
            name=m['name'], email=m['email'], phone=m['phone'],
            role=m['role'], department=m['department'], avatar=m['avatar'],
            avatar_color=m['avatar_color'],
            stats_generated=m['stats_generated'], stats_used=m['stats_used'],
            stats_approved=m['stats_approved'], stats_rejected=m['stats_rejected'],
            perf_this_month=m['perf_this_month'], perf_last_month=m['perf_last_month'],
            perf_rank=m['perf_rank'], status=m.get('status', 'active'),
            joined_at=date(2024, 1, 15)
        )
        db.session.add(member)
    
    db.session.commit()

@team_bp.route('/members')
def list_members():
    try:
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        department = request.args.get('department', '')
        
        query = TeamMember.query
        
        if keyword:
            query = query.filter(
                (TeamMember.name.contains(keyword)) | 
                (TeamMember.email.contains(keyword))
            )
        
        if status and status != 'all':
            query = query.filter(TeamMember.status == status)
        
        if department and department != 'all':
            query = query.filter(TeamMember.department == department)
        
        members = query.order_by(TeamMember.perf_rank).all()
        
        departments = db.session.query(TeamMember.department).distinct().all()
        departments = [d[0] for d in departments if d[0]]
        
        return jsonify({
            'success': True,
            'data': {
                'items': [m.to_dict() for m in members],
                'total': len(members),
                'departments': departments
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/members/<member_id>')
def get_member(member_id):
    try:
        member = TeamMember.query.get(member_id)
        if member:
            return jsonify({'success': True, 'data': member.to_dict()})
        return jsonify({'success': False, 'error': '成员不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/members', methods=['POST'])
def add_member():
    try:
        data = request.get_json()
        member = TeamMember(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            role=data.get('role', '销售代表'),
            department=data.get('department', '销售部'),
            avatar=data.get('name', '?')[0] if data.get('name') else '?',
            avatar_color='linear-gradient(135deg, #0B5FBD, #1A78DB)',
            status='active',
            joined_at=date.today()
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({'success': True, 'data': member.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/members/<member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': '成员不存在'}), 404
        
        data = request.get_json()
        if 'name' in data:
            member.name = data['name']
        if 'role' in data:
            member.role = data['role']
        if 'department' in data:
            member.department = data['department']
        if 'status' in data:
            member.status = data['status']
        
        db.session.commit()
        return jsonify({'success': True, 'data': member.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/members/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        member = TeamMember.query.get(member_id)
        if member:
            db.session.delete(member)
            db.session.commit()
        return jsonify({'success': True, 'message': '成员已移除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/stats')
def team_stats():
    try:
        total = TeamMember.query.count()
        active = TeamMember.query.filter_by(status='active').count()
        total_generated = db.session.query(db.func.sum(TeamMember.stats_generated)).scalar() or 0
        total_used = db.session.query(db.func.sum(TeamMember.stats_used)).scalar() or 0
        
        top_members = TeamMember.query.filter_by(status='active').order_by(
            TeamMember.perf_this_month.desc()
        ).limit(3).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_members': total,
                'active_members': active,
                'total_generated': total_generated,
                'total_used': total_used,
                'approval_rate': round((db.session.query(db.func.sum(TeamMember.stats_approved)).scalar() or 0) / 
                    max(total_generated, 1) * 100, 1),
                'top_performers': [m.to_dict() for m in top_members]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/init')
def init_team():
    try:
        seed_team_members()
        return jsonify({'success': True, 'message': '团队数据初始化完成'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500