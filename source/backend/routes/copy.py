"""文案生成API路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.minimax import MiniMaxService

copy_bp = Blueprint('copy', __name__)

@copy_bp.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        fund_info = data.get('fund_info', {})
        selling_points = data.get('selling_points', [])
        format_type = data.get('format_type', '朋友圈文案')
        style = data.get('style', '亲切易懂')
        
        content = MiniMaxService.generate_with_ai(fund_info, selling_points, format_type, style)
        
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'format': format_type,
                'style': style,
                'generated_at': datetime.now().isoformat(),
                'ai': 'minimax'
            }
        })
    except Exception as e:
        print(f"文案生成错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@copy_bp.route('/formats')
def formats():
    return jsonify({
        'success': True,
        'data': [
            {'id': '朋友圈文案', 'name': '朋友圈文案'},
            {'id': '一句话推荐', 'name': '一句话推荐'},
            {'id': '微信群发', 'name': '微信群发'},
            {'id': '微信图文', 'name': '微信图文'},
        ]
    })
