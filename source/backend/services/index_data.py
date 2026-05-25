"""指数数据服务 - 获取沪深300、中证500等指数数据"""
import requests
import re
import json
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config


class IndexDataService:
    """指数数据获取服务"""
    
    INDEX_CODES = {
        'hs300': {'code': '000300', 'name': '沪深300', 'market': 'SH'},
        'zz500': {'code': '000905', 'name': '中证500', 'market': 'SH'},
        'sh': {'code': '000001', 'name': '上证指数', 'market': 'SH'},
        'sz': {'code': '399001', 'name': '深证成指', 'market': 'SZ'},
        'gem': {'code': '399006', 'name': '创业板指', 'market': 'SZ'}
    }
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_index_history(cls, index_key, days=90):
        """获取指数历史数据（只使用真实数据）"""
        cache_key = f'index_{index_key}_{days}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            index_info = cls.INDEX_CODES.get(index_key)
            if not index_info:
                return None
            
            code = index_info['code']
            market = index_info['market']
            
            url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get'
            params = {
                'secid': f'{market}.{code}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',
                'fqt': '1',
                'beg': '20200101',
                'end': datetime.now().strftime('%Y%m%d')
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': f'https://quote.eastmoney.com/{market}{code}.html'
            }
            
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            data = resp.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                result = []
                
                for kline in klines[-days:]:
                    parts = kline.split(',')
                    if len(parts) >= 6:
                        result.append({
                            'date': parts[0],
                            'open': float(parts[1]),
                            'close': float(parts[2]),
                            'high': float(parts[3]),
                            'low': float(parts[4]),
                            'volume': int(parts[5])
                        })
                
                cls._cache[cache_key] = result
                cls._cache_time[cache_key] = datetime.now().timestamp()
                return result
            
        except Exception as e:
            print(f"获取指数数据失败 {index_key}: {e}")
        
        return None
    
    @classmethod
    def get_index_performance(cls, index_key, days=30):
        """获取指数在指定天数内的收益率"""
        history = cls.get_index_history(index_key, days + 30)
        if not history or len(history) < days:
            return None
        
        start_price = history[-days - 1]['close'] if len(history) > days else history[0]['close']
        end_price = history[-1]['close']
        
        return ((end_price - start_price) / start_price) * 100
    
    @classmethod
    def get_index_series(cls, index_key, days=90):
        """获取指数收益率序列（用于图表）"""
        history = cls.get_index_history(index_key, days)
        if not history or len(history) < 2:
            return None
        
        result = []
        base_price = history[0]['close']
        
        for item in history:
            result.append({
                'date': item['date'],
                'return': ((item['close'] - base_price) / base_price) * 100
            })
        
        return result
    
    @classmethod
    def get_multiple_index_data(cls, index_keys, days=90):
        """批量获取多个指数数据"""
        result = {}
        for key in index_keys:
            data = cls.get_index_series(key, days)
            if data:
                result[key] = data
        return result
