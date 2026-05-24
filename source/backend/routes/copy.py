"""文案生成API路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.minimax import MiniMaxService
from services.wind import WindService

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

@copy_bp.route('/modify', methods=['POST'])
def modify():
    """AI二次修改文案"""
    try:
        data = request.get_json()
        original_content = data.get('original_content', '')
        instruction = data.get('instruction', '请优化这篇文案')
        format_type = data.get('format_type', '朋友圈文案')
        style = data.get('style', '亲切易懂')
        fund_info = data.get('fund_info', {})
        
        if not original_content:
            return jsonify({'success': False, 'error': '请提供原文案'}), 400
        
        content = MiniMaxService.modify_content(original_content, instruction, format_type, style, fund_info)
        
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'original_content': original_content,
                'instruction': instruction,
                'modified_at': datetime.now().isoformat(),
                'ai': 'minimax'
            }
        })
    except Exception as e:
        print(f"文案修改错误: {e}")
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


@copy_bp.route('/wind/verify', methods=['POST'])
def wind_verify():
    """Wind数据验证API"""
    try:
        data = request.get_json()
        fund_code = data.get('fund_code')
        fund_name = data.get('fund_name')
        content = data.get('content')
        
        if not fund_code:
            return jsonify({'success': False, 'error': '请提供基金代码'}), 400
        
        # 调用Wind服务验证
        result = WindService.verify_fund_data(fund_code, fund_name, content)
        
        return jsonify(result)
    except Exception as e:
        print(f"Wind验证错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
