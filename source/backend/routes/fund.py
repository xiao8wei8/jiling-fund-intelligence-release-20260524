"""基金API路由"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from io import BytesIO
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import requests
from pypdf import PdfReader

from services.eastmoney import EastmoneyService
from services.tiantianfund import TiantianFundService
from services.index_data import IndexDataService

fund_bp = Blueprint('fund', __name__)

MARKET_SIZE_FALLBACK = {
    'value': '37.53',
    'unit': '万亿元',
    'period': '2026年3月',
    'source': '中国证券投资基金业协会',
    'source_url': 'https://www.amac.org.cn/sjtj/tjbg/gmjj/202604/P020260422599009744026.pdf'
}
MARKET_SIZE_CACHE = {
    'data': None,
    'expires_at': None
}

MARKET_OVERVIEW_FALLBACK = {
    'period': '2026年3月',
    'source': '中国证券投资基金业协会',
    'source_url': 'https://www.amac.org.cn/sjtj/tjbg/gmjj/202604/P020260422599009744026.pdf',
    'updated_at': '2026-04-22',
    'latest': {
        'total_scale': 37.53,
        'total_count': 13930,
        'managers': 165,
        'open_end_scale': 33.72,
        'open_end_count': 12582,
        'closed_end_scale': 3.81,
        'closed_end_count': 1348,
        'non_money_scale': 21.94,
        'non_money_count': 13572,
        'month_delta_scale': -0.12,
        'month_delta_count': 312
    },
    'category_series': [
        {'period': '2017', 'stock': 7550, 'hybrid': 20640, 'bond': 16600, 'money': 67000, 'qdii': 820, 'fof': 120, 'other': 310, 'total': 113040, 'count': 4841},
        {'period': '2018', 'stock': 7180, 'hybrid': 16620, 'bond': 24100, 'money': 78000, 'qdii': 920, 'fof': 420, 'other': 330, 'total': 127570, 'count': 5626},
        {'period': '2019', 'stock': 11250, 'hybrid': 21840, 'bond': 39520, 'money': 73800, 'qdii': 1150, 'fof': 670, 'other': 390, 'total': 148620, 'count': 6544},
        {'period': '2020', 'stock': 20240, 'hybrid': 47080, 'bond': 49560, 'money': 79200, 'qdii': 1610, 'fof': 920, 'other': 470, 'total': 199080, 'count': 7913},
        {'period': '2021', 'stock': 25230, 'hybrid': 61780, 'bond': 69020, 'money': 94100, 'qdii': 2320, 'fof': 1640, 'other': 540, 'total': 254630, 'count': 9288},
        {'period': '2022', 'stock': 24888, 'hybrid': 47834, 'bond': 76558, 'money': 104549, 'qdii': 3283, 'fof': 1927, 'other': 112, 'total': 260351, 'count': 10491},
        {'period': '2023', 'stock': 28401, 'hybrid': 37147, 'bond': 90458, 'money': 112780, 'qdii': 4186, 'fof': 1555, 'other': 1590, 'total': 276117, 'count': 11514},
        {'period': '2024', 'stock': 44646, 'hybrid': 31756, 'bond': 105491, 'money': 136086, 'qdii': 6097, 'fof': 1332, 'other': 2902, 'total': 328310, 'count': 12359},
        {'period': '2025', 'stock': 60509, 'hybrid': 36596, 'bond': 111128, 'money': 150104, 'qdii': 9738, 'fof': 2442, 'other': 6200, 'total': 376717, 'count': 13618},
        {'period': '2026-03', 'stock': 49516, 'hybrid': 37876, 'bond': 111224, 'money': 155896, 'qdii': 10084, 'fof': 3551, 'other': 7153, 'total': 375300, 'count': 13930}
    ],
    'company_ranking': [
        {'rank': 1, 'company': '易方达基金', 'total_scale': 25074, 'total_count': 517, 'stock': 6595, 'hybrid': 2530, 'bond': 4878, 'money': 8450, 'qdii': 1518, 'fof': 314},
        {'rank': 2, 'company': '华夏基金', 'total_scale': 20606, 'total_count': 547, 'stock': 6215, 'hybrid': 1311, 'bond': 2938, 'money': 7657, 'qdii': 1528, 'fof': 207},
        {'rank': 3, 'company': '广发基金', 'total_scale': 16851, 'total_count': 476, 'stock': 2556, 'hybrid': 2172, 'bond': 3825, 'money': 6619, 'qdii': 1240, 'fof': 291},
        {'rank': 4, 'company': '南方基金', 'total_scale': 14659, 'total_count': 437, 'stock': 2775, 'hybrid': 1102, 'bond': 2916, 'money': 7163, 'qdii': 424, 'fof': 142},
        {'rank': 5, 'company': '富国基金', 'total_scale': 13777, 'total_count': 452, 'stock': 2428, 'hybrid': 1618, 'bond': 4229, 'money': 4751, 'qdii': 297, 'fof': 305},
        {'rank': 6, 'company': '天弘基金', 'total_scale': 12845, 'total_count': 260, 'stock': 1919, 'hybrid': 272, 'bond': 2386, 'money': 7700, 'qdii': 458, 'fof': 38},
        {'rank': 7, 'company': '博时基金', 'total_scale': 11631, 'total_count': 405, 'stock': 813, 'hybrid': 597, 'bond': 3704, 'money': 4858, 'qdii': 600, 'fof': 111},
        {'rank': 8, 'company': '汇添富基金', 'total_scale': 11619, 'total_count': 411, 'stock': 1929, 'hybrid': 1710, 'bond': 2831, 'money': 4747, 'qdii': 281, 'fof': 72},
        {'rank': 9, 'company': '鹏华基金', 'total_scale': 11123, 'total_count': 401, 'stock': 1392, 'hybrid': 846, 'bond': 3435, 'money': 5305, 'qdii': 88, 'fof': 26},
        {'rank': 10, 'company': '嘉实基金', 'total_scale': 10466, 'total_count': 381, 'stock': 2899, 'hybrid': 830, 'bond': 2618, 'money': 3623, 'qdii': 395, 'fof': 25}
    ],
    'issuance': [
        {'period': '2025-08', 'count': 141, 'amount': 1008},
        {'period': '2025-09', 'count': 202, 'amount': 1632},
        {'period': '2025-10', 'count': 92, 'amount': 718},
        {'period': '2025-11', 'count': 137, 'amount': 928},
        {'period': '2025-12', 'count': 180, 'amount': 1110},
        {'period': '2026-01', 'count': 124, 'amount': 1181},
        {'period': '2026-02', 'count': 110, 'amount': 892},
        {'period': '2026-03', 'count': 148, 'amount': 1116}
    ]
}

MARKET_OVERVIEW_CACHE = {
    'data': None,
    'expires_at': None
}

def _fetch_latest_market_size():
    """Fetch latest public fund market size with official AMAC data as fallback."""
    # AMAC publishes monthly PDFs. This fallback is the latest verified data as of 2026-05-23.
    # The live refresh keeps the endpoint ready for newer AMAC pages without blocking the UI.
    listing_url = 'https://www.amac.org.cn/sjtj/tjbg/gmjj/'
    data = dict(MARKET_SIZE_FALLBACK)
    try:
        resp = requests.get(listing_url, timeout=6)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        text = resp.text
        pdf_match = re.search(r'href="([^"]*P020\d+[^"]*\.pdf)"[^>]*>\s*公募基金市场数据（(\d{4})\s*年\s*(\d{1,2})\s*月）', text)
        if pdf_match:
            href, year, month = pdf_match.groups()
            if not href.startswith('http'):
                href = 'https://www.amac.org.cn' + href
            pdf_resp = requests.get(href, timeout=10)
            pdf_resp.raise_for_status()
            reader = PdfReader(BytesIO(pdf_resp.content))
            pdf_text = '\n'.join(page.extract_text() or '' for page in reader.pages)
            value_match = re.search(r'资产净值合计.*?([\d.]+)\s*万亿元', pdf_text, re.S)
            if not value_match:
                value_match = re.search(r'合计\s+[\d,]+\s+[\d,]+\s+([\d.]+)', pdf_text)
            data.update({
                'value': value_match.group(1) if value_match else data['value'],
                'period': f'{year}年{int(month)}月',
                'source_url': href
            })
        return data
    except Exception:
        return data

@fund_bp.route('/market-size')
def market_size():
    try:
        now = datetime.now()
        if MARKET_SIZE_CACHE['data'] and MARKET_SIZE_CACHE['expires_at'] and now < MARKET_SIZE_CACHE['expires_at']:
            return jsonify({'success': True, 'data': MARKET_SIZE_CACHE['data']})

        data = _fetch_latest_market_size()
        data['updated_at'] = now.strftime('%Y-%m-%d %H:%M')
        MARKET_SIZE_CACHE['data'] = data
        MARKET_SIZE_CACHE['expires_at'] = now + timedelta(hours=6)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        fallback = dict(MARKET_SIZE_FALLBACK)
        fallback['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        return jsonify({'success': True, 'data': fallback, 'warning': str(e)})

@fund_bp.route('/market-overview')
def market_overview():
    """Public fund market dashboard data.

    AMAC publishes the market overview as monthly PDF/table files. The endpoint
    returns a verified official fallback immediately and keeps the response shape
    ready for live refreshes when the AMAC page is reachable.
    """
    try:
        now = datetime.now()
        force = request.args.get('refresh') in ['1', 'true', 'yes']
        if not force and MARKET_OVERVIEW_CACHE['data'] and MARKET_OVERVIEW_CACHE['expires_at'] and now < MARKET_OVERVIEW_CACHE['expires_at']:
            return jsonify({'success': True, 'data': MARKET_OVERVIEW_CACHE['data']})

        data = dict(MARKET_OVERVIEW_FALLBACK)
        latest_size = _fetch_latest_market_size()
        try:
            data['latest'] = dict(data['latest'])
            data['latest']['total_scale'] = float(latest_size.get('value', data['latest']['total_scale']))
            data['period'] = latest_size.get('period', data['period'])
            data['source_url'] = latest_size.get('source_url', data['source_url'])
        except Exception:
            pass
        data['updated_at'] = now.strftime('%Y-%m-%d %H:%M')
        data['is_live'] = data['period'] != MARKET_OVERVIEW_FALLBACK['period'] or data['source_url'] != MARKET_OVERVIEW_FALLBACK['source_url']
        MARKET_OVERVIEW_CACHE['data'] = data
        MARKET_OVERVIEW_CACHE['expires_at'] = now + timedelta(hours=6)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        fallback = dict(MARKET_OVERVIEW_FALLBACK)
        fallback['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        return jsonify({'success': True, 'data': fallback, 'warning': str(e)})

@fund_bp.route('/list')
def list_funds():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '') or request.args.get('q', '')
        
        if keyword:
            funds = EastmoneyService.search_funds(keyword, 100)
        else:
            funds = EastmoneyService.get_fund_list()
        
        total = len(funds)
        start = (page - 1) * page_size
        end = start + page_size
        items = funds[start:end]
        
        return jsonify({'success': True, 'data': items, 'total': total, 'page': page, 'page_size': page_size})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/search')
def search():
    try:
        keyword = request.args.get('q', '') or request.args.get('keyword', '')
        limit = request.args.get('limit', 20, type=int)
        
        # First search in fund list
        results = EastmoneyService.search_funds(keyword, limit)
        
        # If no results and keyword looks like a fund code (6 digits), try to get details directly
        if not results and keyword.isdigit() and len(keyword) >= 5:
            detail = EastmoneyService.get_fund_detail(keyword)
            if detail:
                results = [detail]
        
        # If still no results, try searching with different query
        if not results and len(keyword) >= 2:
            # Try partial match
            all_funds = EastmoneyService.get_fund_list()
            keyword_lower = keyword.lower()
            results = [f for f in all_funds if keyword_lower in f['code'].lower() or keyword_lower in f['name'].lower()][:limit]
        
        return jsonify({'success': True, 'data': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>')
def detail(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        if detail:
            return jsonify({'success': True, 'data': detail})
        
        funds = EastmoneyService.get_fund_list()
        fund = next((f for f in funds if f['code'] == code), None)
        if fund:
            return jsonify({'success': True, 'data': fund})
        return jsonify({'success': False, 'error': '基金不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/detail')
def fund_detail(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        if detail:
            return jsonify({'success': True, 'data': detail})
        return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/full')
def fund_full(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        history = EastmoneyService.get_fund_nav_history(code, 365)
        hotspots = EastmoneyService.get_hotspots(code)
        
        if not detail:
            return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'detail': detail,
                'history': history,
                'hotspots': hotspots
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/hotspots')
def fund_hotspots(code):
    try:
        hotspots = EastmoneyService.get_hotspots(code)
        return jsonify({'success': True, 'data': hotspots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/nav')
def fund_nav(code):
    try:
        days = request.args.get('days', 180, type=int)
        history = EastmoneyService.get_fund_nav_history(code, days)
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/home/recommend')
def home_recommend():
    try:
        codes = ['163406', '003095', '161005', '110022', '161725', '320007', '000198', '004512']
        funds = []
        for code in codes:
            detail = EastmoneyService.get_fund_detail(code)
            if detail:
                funds.append(detail)
            else:
                funds.append({'code': code, 'name': '加载中...'})
        return jsonify({'success': True, 'data': funds})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/rank')
def fund_rank(code):
    try:
        rank_data = TiantianFundService.get_fund_rank(code)
        if rank_data:
            return jsonify({'success': True, 'data': rank_data})
        return jsonify({'success': False, 'error': '获取排名数据失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/comparison')
def fund_comparison(code):
    try:
        comparison_data = TiantianFundService.get_performance_comparison(code)
        if comparison_data:
            return jsonify({'success': True, 'data': comparison_data})
        return jsonify({'success': False, 'error': '获取对比数据失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/full_plus')
def fund_full_plus(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        history = EastmoneyService.get_fund_nav_history(code, 365)
        hotspots = EastmoneyService.get_hotspots(code)
        rank_data = TiantianFundService.get_fund_rank(code)
        comparison_data = TiantianFundService.get_performance_comparison(code)
        
        if not detail:
            return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'detail': detail,
                'history': history,
                'hotspots': hotspots,
                'rank': rank_data,
                'comparison': comparison_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/copywriting', methods=['POST'])
def generate_copywriting():
    try:
        data = request.json
        fund_info = data.get('fund_info', {})
        selling_points = data.get('selling_points', [])
        format_type = data.get('format_type', '朋友圈短文')
        style = data.get('style', '亲切易懂')
        
        # 构建提示词
        prompt = f"""请为基金产品生成一篇营销文案。

基金信息：
- 基金名称：{fund_info.get('name', '海富通沪深300指数增强C')}
- 基金代码：{fund_info.get('code', '004512')}
- 基金类型：{fund_info.get('type', '混合型')}
- 近1年收益：{fund_info.get('y1', fund_info.get('yield_1y', '—'))}
- 近3年收益：{fund_info.get('y3', fund_info.get('yield_3y', '—'))}
- 夏普比率：{fund_info.get('sharpe', '—')}
- 最大回撤：{fund_info.get('dd', fund_info.get('drawdown', '—'))}
- 基金经理：{fund_info.get('manager', '—')}
- 基金公司：{fund_info.get('company', '—')}

选定卖点：
{chr(10).join([f"- {point}" for point in selling_points])}

文案要求：
- 格式：{format_type}
- 风格：{style}
- 字数：根据格式要求适当调整
- 内容：结合基金信息和选定卖点，突出产品优势
- 语言：简洁明了，富有感染力
- 结尾：包含风险提示
"""
        
        # 模拟AI生成文案
        # 实际项目中可以调用真实的AI API
        # 使用\n作为换行符，确保在前端正确显示
        generated_content = f"{fund_info.get('name', '海富通沪深300指数增强C')}，您的投资新选择！\n\n"
        generated_content += "\n".join([f"• {point}" for point in selling_points])
        generated_content += f"\n\n该基金由{fund_info.get('manager', '专业基金经理')}精心管理，"
        generated_content += f"近1年收益{fund_info.get('y1', fund_info.get('yield_1y', '—'))}，表现出色。\n\n"
        generated_content += f"选择{fund_info.get('name', '海富通沪深300指数增强C')}，把握市场机遇，开启您的财富增长之旅！\n\n"
        generated_content += "*基金有风险，投资需谨慎。过往业绩不代表未来表现。*"
        
        return jsonify({
            'success': True,
            'data': {
                'content': generated_content
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@fund_bp.route('/index/<index_key>')
def get_index_data(index_key):
    """获取指数数据"""
    try:
        days = request.args.get('days', 90, type=int)
        data = IndexDataService.get_index_series(index_key, days)
        if data:
            return jsonify({'success': True, 'data': data})
        return jsonify({'success': False, 'error': '获取指数数据失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@fund_bp.route('/index/multiple')
def get_multiple_index_data():
    """批量获取多个指数数据"""
    try:
        keys = request.args.get('keys', '')
        index_keys = keys.split(',') if keys else ['hs300']
        days = request.args.get('days', 90, type=int)
        
        # 至少获取5年的数据，确保"近3年"、"近5年"、"成立以来"都有完整数据
        buffer_days = max(days + 60, 365 * 5)
        
        data = IndexDataService.get_multiple_index_data(index_keys, buffer_days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
