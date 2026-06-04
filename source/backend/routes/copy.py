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
        enhance_prompt = data.get('enhance_prompt', '')
        
        content = MiniMaxService.generate_with_ai(fund_info, selling_points, format_type, style, enhance_prompt)
        
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


@copy_bp.route('/agent/result-check', methods=['POST'])
def agent_result_check():
    """文案审核Agent API"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        fund_info = data.get('fund_info', {})
        prompt = data.get('prompt', '')
        
        if not content:
            return jsonify({'success': False, 'error': '请提供文案内容'}), 400
        
        # 调用MiniMax进行文案审核
        result = MiniMaxService.check_content_quality(content, fund_info, prompt)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"文案审核错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@copy_bp.route('/agent/compliance-check', methods=['POST'])
def agent_compliance_check():
    """合规检查Agent API"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        prompt = data.get('prompt', '')
        
        if not content:
            return jsonify({'success': False, 'error': '请提供文案内容'}), 400
        
        # 调用MiniMax进行合规检查
        result = MiniMaxService.check_compliance(content, prompt)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"合规检查错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@copy_bp.route('/wind/verify', methods=['POST'])
def wind_verify():
    """Wind数据验证API"""
    try:
        data = request.get_json()
        fund_code = data.get('fund_code')
        fund_name = data.get('fund_name')
        content = data.get('content')
        prompt = data.get('prompt', '')
        
        if not fund_code:
            return jsonify({'success': False, 'error': '请提供基金代码'}), 400
        
        # 调用Wind服务验证
        result = WindService.verify_fund_data(fund_code, fund_name, content, prompt)
        
        return jsonify(result)
    except Exception as e:
        print(f"Wind验证错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@copy_bp.route('/agent/market-style', methods=['POST'])
def agent_market_style():
    """市场风格分析Agent API"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        fund_info = data.get('fund_info', {})
        prompt = data.get('prompt', '')
        
        # 调用MiniMax进行市场风格分析
        result = MiniMaxService.analyze_market_style(content, fund_info, prompt)
        
        return jsonify(result)
    except Exception as e:
        print(f"市场风格分析错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@copy_bp.route('/agent/fund-comparison', methods=['POST'])
def agent_fund_comparison():
    """基金对比分析Agent API"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        fund_info = data.get('fund_info', {})
        compare_data = data.get('compare_data', None)
        prompt = data.get('prompt', '')
        
        # 调用MiniMax进行基金对比分析
        result = MiniMaxService.compare_funds(content, fund_info, compare_data, prompt)
        
        return jsonify(result)
    except Exception as e:
        print(f"基金对比分析错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
