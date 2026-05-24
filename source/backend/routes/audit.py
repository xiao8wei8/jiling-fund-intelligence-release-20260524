"""审核管理API路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import db, GeneratedContent, AuditLog, TeamMember

audit_bp = Blueprint('audit', __name__)

def seed_audit_data():
    """初始化审核数据"""
    if GeneratedContent.query.count() > 0:
        return
    
    audit_data = [
        {
            "fund_code": "161005",
            "fund_name": "富国天惠成长混合A",
            "format_type": "基金经理卡",
            "content": "【富国天惠成长混合A】\n\n朱少醒基金经理推荐👍\n\n成立17年，年化收益超20%🔥\n\n适合长期定投，建议配置比例30%",
            "style": "专业推荐",
            "member_id": 2,
            "status": "pending"
        },
        {
            "fund_code": "320007",
            "fund_name": "诺安成长混合",
            "format_type": "微信图文",
            "content": "【诺安成长混合】\n\n专注半导体赛道，近一年收益+45%\n\n基金经理蔡嵩松，科技投资专家",
            "style": "业绩推荐",
            "member_id": 3,
            "status": "pending"
        },
        {
            "fund_code": "163406",
            "fund_name": "兴全合润混合A",
            "format_type": "朋友圈文案",
            "content": "🐂 兴全合润混合A，近一年收益+53.82%！\n\n谢治宇经理实力掌舵，价值投资典范。",
            "style": "高收益推荐",
            "member_id": 1,
            "status": "approved"
        },
        {
            "fund_code": "161725",
            "fund_name": "招商中证白酒指数(LOF)A",
            "format_type": "一句话推荐",
            "content": "白酒赛道龙头，布局消费升级",
            "style": "简短精炼",
            "member_id": 1,
            "status": "rejected"
        },
        {
            "fund_code": "000001",
            "fund_name": "华夏成长混合",
            "format_type": "微商群发",
            "content": "📢 华夏成长混合，稳定增值好选择！",
            "style": "群发推广",
            "member_id": 4,
            "status": "approved"
        }
    ]
    
    for d in audit_data:
        content = GeneratedContent(
            fund_code=d['fund_code'],
            fund_name=d['fund_name'],
            format_type=d['format_type'],
            content=d['content'],
            style=d['style'],
            member_id=d['member_id'],
            status=d['status']
        )
        db.session.add(content)
    
    db.session.commit()

@audit_bp.route('/contents')
def list_contents():
    try:
        status = request.args.get('status', '')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        query = GeneratedContent.query
        
        if status and status != 'all':
            query = query.filter(GeneratedContent.status == status)
        
        total = query.count()
        contents = query.order_by(GeneratedContent.created_at.desc()).offset((page-1)*limit).limit(limit).all()
        
        pending_count = GeneratedContent.query.filter_by(status='pending').count()
        approved_count = GeneratedContent.query.filter_by(status='approved').count()
        rejected_count = GeneratedContent.query.filter_by(status='rejected').count()
        
        items = []
        for c in contents:
            member = TeamMember.query.get(c.member_id)
            items.append({
                'id': c.id,
                'fund_code': c.fund_code,
                'fund_name': c.fund_name,
                'format_type': c.format_type,
                'content': c.content,
                'style': c.style,
                'status': c.status,
                'submitter': member.name if member else '未知',
                'created_at': c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else '',
                'approved_at': c.approved_at.strftime('%Y-%m-%d %H:%M') if c.approved_at else ''
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'total': total,
                'page': page,
                'counts': {
                    'pending': pending_count,
                    'approved': approved_count,
                    'rejected': rejected_count
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_bp.route('/contents/<int:content_id>')
def get_content(content_id):
    try:
        content = GeneratedContent.query.get(content_id)
        if not content:
            return jsonify({'success': False, 'error': '内容不存在'}), 404
        
        member = TeamMember.query.get(content.member_id)
        return jsonify({
            'success': True,
            'data': {
                'id': content.id,
                'fund_code': content.fund_code,
                'fund_name': content.fund_name,
                'format_type': content.format_type,
                'content': content.content,
                'style': content.style,
                'status': content.status,
                'submitter': member.name if member else '未知',
                'submitter_dept': member.department if member else '',
                'created_at': content.created_at.strftime('%Y-%m-%d %H:%M') if content.created_at else '',
                'used_count': content.used_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_bp.route('/contents/<int:content_id>/approve', methods=['POST'])
def approve_content(content_id):
    try:
        content = GeneratedContent.query.get(content_id)
        if not content:
            return jsonify({'success': False, 'error': '内容不存在'}), 404
        
        content.status = 'approved'
        content.approved_at = datetime.now()
        
        log = AuditLog(
            content_id=content_id,
            action='approve',
            operator_id=1
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '审核通过'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_bp.route('/contents/<int:content_id>/reject', methods=['POST'])
def reject_content(content_id):
    try:
        data = request.get_json() or {}
        comment = data.get('comment', '')
        
        content = GeneratedContent.query.get(content_id)
        if not content:
            return jsonify({'success': False, 'error': '内容不存在'}), 404
        
        content.status = 'rejected'
        content.approved_at = datetime.now()
        
        log = AuditLog(
            content_id=content_id,
            action='reject',
            comment=comment,
            operator_id=1
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '已驳回'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_bp.route('/init')
def init_audit():
    try:
        seed_audit_data()
        return jsonify({'success': True, 'message': '审核数据初始化完成'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_bp.route('/stats')
def audit_stats():
    try:
        pending = GeneratedContent.query.filter_by(status='pending').count()
        approved = GeneratedContent.query.filter_by(status='approved').count()
        rejected = GeneratedContent.query.filter_by(status='rejected').count()
        
        return jsonify({
            'success': True,
            'data': {
                'pending': pending,
                'approved': approved,
                'rejected': rejected,
                'total': pending + approved + rejected
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500