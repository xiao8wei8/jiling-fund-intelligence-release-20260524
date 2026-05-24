"""素材库API路由"""
from flask import Blueprint, jsonify, request
import json, os
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

library_bp = Blueprint('library', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)
LIBRARY_FILE = os.path.join(DATA_DIR, 'library.json')

def get_library():
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_library(data):
    with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_data():
    if not os.path.exists(LIBRARY_FILE):
        from services.eastmoney import EastmoneyService
        funds = EastmoneyService.get_backup_funds()
        library = []
        for fund in funds:
            for fmt in ['朋友圈文案', '一句话推荐', '微信群发', '微信图文']:
                library.append({
                    'id': f"{fund['code']}_{fmt}",
                    'fund_code': fund['code'],
                    'fund_name': fund['name'],
                    'category': 'copy',
                    'format': fmt,
                    'content': f"📈 {fund['name']}\n\n{fund['company']}优质基金，欢迎咨询！\n\n⚠️ 基金有风险，投资需谨慎",
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        save_library(library)
    return get_library()

init_data()

@library_bp.route('/list')
def list_library():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        category = request.args.get('category', '')
        keyword = request.args.get('keyword', '')
        
        items = get_library()
        if category and category != 'all':
            items = [i for i in items if i.get('category') == category]
        if keyword:
            kw = keyword.lower()
            items = [i for i in items if kw in i.get('fund_name', '').lower() or kw in i.get('content', '').lower()]
        
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]
        
        return jsonify({'success': True, 'data': {'items': page_items, 'total': total, 'page': page, 'page_size': page_size}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@library_bp.route('/stats')
def stats():
    try:
        items = get_library()
        return jsonify({
            'success': True,
            'data': {
                'total_items': len(items),
                'total_funds': len(set(i.get('fund_code') for i in items)),
                'categories': {'copy': len([i for i in items if i.get('category') == 'copy'])},
                'copy': len([i for i in items if i.get('category') == 'copy']),
                'image': len([i for i in items if i.get('category') == 'image'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@library_bp.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        item = {
            'id': data.get('id') or f"item_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'fund_code': data.get('fund_code', ''),
            'fund_name': data.get('fund_name', ''),
            'category': data.get('category', 'copy'),
            'content': data.get('content', ''),
            'format': data.get('format', ''),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        items = get_library()
        existing_idx = next((i for i, x in enumerate(items) if x.get('id') == item['id']), None)
        if existing_idx is not None:
            items[existing_idx] = {**items[existing_idx], **item}
        else:
            items.append(item)
        
        save_library(items)
        return jsonify({'success': True, 'data': item})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
