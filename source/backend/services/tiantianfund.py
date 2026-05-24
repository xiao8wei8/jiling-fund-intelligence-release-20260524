"""天天基金数据服务 - 获取同类排名和业绩表现对比"""
import requests
import re
import html
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config


class TiantianFundService:
    """天天基金数据获取"""
    
    FUND_DETAIL_URL = "https://fund.eastmoney.com"
    RANK_URL = "https://fund.eastmoney.com/data/rankhandler.aspx"
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_fund_rank(cls, code):
        """获取基金同类排名数据"""
        cache_key = f'rank_{code}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            # 先从基金详情页获取排名信息
            url = f"{cls.FUND_DETAIL_URL}/{code}.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://fund.eastmoney.com/'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.encoding = resp.apparent_encoding or resp.encoding
            raw = resp.text
            text = html.unescape(raw)
            text = re.sub(r'<script[\s\S]*?</script>', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = text.replace('\xa0', ' ')
            text = re.sub(r'\s+', ' ', text)
            
            result = {
                'code': code,
                'rank_1w': '',
                'rank_1y': '',
                'rank_3y': '',
                'rank_6m': '',
                'rank_1m': '',
                'rank_3m': '',
                'rank_ytd': '',
                'rank_2y': '',
                'rank_type': '',
                'total_funds': '',
                'peer_funds': []
            }
            
            # 提取排名信息
            rank_patterns = [
                (r'近1月排名.*?([\d]+)/([\d]+)', 'rank_1m'),
                (r'近3月排名.*?([\d]+)/([\d]+)', 'rank_3m'),
                (r'近6月排名.*?([\d]+)/([\d]+)', 'rank_6m'),
                (r'近1年排名.*?([\d]+)/([\d]+)', 'rank_1y'),
                (r'近3年排名.*?([\d]+)/([\d]+)', 'rank_3y'),
            ]
            
            for pattern, key in rank_patterns:
                match = re.search(pattern, text)
                if match:
                    result[key] = f"{match.group(1)}/{match.group(2)}"
                    if not result['total_funds']:
                        result['total_funds'] = match.group(2)

            if not result.get('rank_1y'):
                seg_match = re.search(r'同类排名\s*(.*?)(四分位排名|累计收益率走势|选择时间|$)', text)
                if seg_match:
                    seg = seg_match.group(1)
                    pairs = re.findall(r'(\d{1,6})\s*\|\s*(\d{1,6})', seg)
                    if len(pairs) >= 8:
                        result['rank_1w'] = f"{pairs[0][0]}/{pairs[0][1]}"
                        result['rank_1m'] = f"{pairs[1][0]}/{pairs[1][1]}"
                        result['rank_3m'] = f"{pairs[2][0]}/{pairs[2][1]}"
                        result['rank_6m'] = f"{pairs[3][0]}/{pairs[3][1]}"
                        result['rank_ytd'] = f"{pairs[4][0]}/{pairs[4][1]}"
                        result['rank_1y'] = f"{pairs[5][0]}/{pairs[5][1]}"
                        result['rank_2y'] = f"{pairs[6][0]}/{pairs[6][1]}"
                        result['rank_3y'] = f"{pairs[7][0]}/{pairs[7][1]}"
                        if not result['total_funds']:
                            result['total_funds'] = pairs[5][1]
            
            # 提取基金类型
            type_match = re.search(r'基金类型.*?>([^<]+)<', raw)
            if type_match:
                result['rank_type'] = type_match.group(1).strip()
            
            # 从排名API获取同类型基金数据
            peer_funds = cls.get_peer_funds(code)
            if peer_funds:
                result['peer_funds'] = peer_funds
            
            cls._cache[cache_key] = result
            cls._cache_time[cache_key] = datetime.now().timestamp()
            return result
            
        except Exception as e:
            print(f"获取基金排名失败 {code}: {e}")
            return None
    
    @classmethod
    def get_peer_funds(cls, code, limit=10):
        """获取同类型基金列表用于对比"""
        try:
            # 获取该基金的详情以确定类型
            from services.eastmoney import EastmoneyService
            detail = EastmoneyService.get_fund_detail(code)
            if not detail:
                return []
            
            # 返回一些常见的同类型基金做对比
            fund_type = detail.get('type', '')
            
            peer_list = []
            
            if '指数' in fund_type:
                peer_list = [
                    {'code': '000051', 'name': '华夏沪深300ETF联接A'},
                    {'code': '110020', 'name': '易方达沪深300ETF联接A'},
                    {'code': '001630', 'name': '天弘中证500指数增强A'},
                    {'code': '161017', 'name': '富国中证500指数(LOF)'},
                    {'code': '000961', 'name': '天弘沪深300ETF联接A'},
                ]
            elif '混合' in fund_type:
                peer_list = [
                    {'code': '163406', 'name': '兴全合润混合（LOF）'},
                    {'code': '003095', 'name': '中欧医疗健康混合A'},
                    {'code': '161005', 'name': '富国天惠成长混合A'},
                    {'code': '320007', 'name': '诺安成长混合'},
                    {'code': '001878', 'name': '嘉实沪港深精选股票'},
                ]
            elif '股票' in fund_type:
                peer_list = [
                    {'code': '110022', 'name': '易方达消费行业股票'},
                    {'code': '000001', 'name': '华夏成长混合'},
                    {'code': '161725', 'name': '招商中证白酒指数（LOF）'},
                ]
            else:
                peer_list = [
                    {'code': '163406', 'name': '兴全合润混合（LOF）'},
                    {'code': '003095', 'name': '中欧医疗健康混合A'},
                    {'code': '161005', 'name': '富国天惠成长混合A'},
                ]
            
            # 获取这些基金的详情数据
            from services.eastmoney import EastmoneyService
            result = []
            for f in peer_list[:limit]:
                try:
                    f_detail = EastmoneyService.get_fund_detail(f['code'])
                    if f_detail:
                        result.append({
                            'code': f_detail.get('code', f['code']),
                            'name': f_detail.get('name', f['name']),
                            'yield_1y': f_detail.get('yield_1y', ''),
                            'yield_3y': f_detail.get('yield_3y', ''),
                            'yield_6m': f_detail.get('yield_6m', ''),
                            'type': f_detail.get('type', ''),
                            'nav': f_detail.get('nav', ''),
                            'manager': f_detail.get('manager', ''),
                        })
                except:
                    pass
            
            return result
            
        except Exception as e:
            print(f"获取同类型基金失败 {code}: {e}")
            return []
    
    @classmethod
    def get_performance_comparison(cls, code):
        """获取业绩表现对比数据"""
        cache_key = f'perf_compare_{code}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            from services.eastmoney import EastmoneyService
            detail = EastmoneyService.get_fund_detail(code)
            
            if not detail:
                return None
            
            result = {
                'code': code,
                'name': detail.get('name', ''),
                'yield_1y': detail.get('yield_1y', ''),
                'yield_3y': detail.get('yield_3y', ''),
                'yield_6m': detail.get('yield_6m', ''),
                'yield_3m': detail.get('yield_3m', ''),
                'sharpe': detail.get('sharpe', ''),
                'drawdown': detail.get('drawdown', ''),
                'type': detail.get('type', ''),
                'benchmark': '沪深300',
                'peer_funds': cls.get_peer_funds(code, 8),
                'rank_data': cls.get_fund_rank(code)
            }
            
            cls._cache[cache_key] = result
            cls._cache_time[cache_key] = datetime.now().timestamp()
            return result
            
        except Exception as e:
            print(f"获取业绩对比失败 {code}: {e}")
            return None
