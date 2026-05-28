"""指数数据服务 - 使用 Wind MCP 获取沪深300、中证500等指数数据，东方财富作为备用"""
import requests
import re
import json
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config
from services.wind_mcp import WindMCP


class IndexDataService:
    """指数数据获取服务 - 使用 Wind MCP，东方财富作为备用"""
    
    INDEX_NAMES = {
        'hs300': '000300.SH',
        'zz500': '000905.SH',
        'sh': '000001.SH',
        'sz': '399001.SZ',
        'gem': '399006.SZ'
    }
    
    # 东方财富指数代码映射
    EASTMONEY_INDEX_CODES = {
        'hs300': '000300',
        'zz500': '000905',
        'sh': '000001',
        'sz': '399001',
        'gem': '399006'
    }
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_index_history_from_eastmoney(cls, index_key, days=90):
        """从东方财富获取指数历史数据（备用数据源）"""
        try:
            code = cls.EASTMONEY_INDEX_CODES.get(index_key)
            if not code:
                return None
            
            # 东方财富指数K线API
            url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{code}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20500101&lmt={days}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com/'
            }
            
            resp = requests.get(url, headers=headers, timeout=15)
            data = resp.json()
            
            if data.get('data', {}).get('code') != 0:
                return None
            
            klines = data.get('data', {}).get('klines', [])
            if not klines:
                return None
            
            result_list = []
            for kline in klines:
                parts = kline.split(',')
                if len(parts) >= 6:
                    result_list.append({
                        'date': parts[0],
                        'open': float(parts[1]) if parts[1] else 0,
                        'close': float(parts[2]) if parts[2] else 0,
                        'high': float(parts[3]) if parts[3] else 0,
                        'low': float(parts[4]) if parts[4] else 0,
                        'volume': int(float(parts[5])) if parts[5] else 0
                    })
            
            return result_list if result_list else None
            
        except Exception as e:
            print(f"从东方财富获取指数数据失败 {index_key}: {e}")
            return None
    
    @classmethod
    def get_index_history(cls, index_key, days=90):
        """获取指数历史数据（优先使用 Wind MCP，失败则使用东方财富）"""
        cache_key = f'index_{index_key}_{days}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        result_list = None
        
        # 优先使用 Wind MCP
        try:
            index_name = cls.INDEX_NAMES.get(index_key)
            if index_name:
                end_date = datetime.now().strftime('%Y%m%d')
                begin_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
                
                result = WindMCP.get_index_kline(index_name, begin_date, end_date, '10')
                
                if result.get('success'):
                    data = result.get('data')
                    if data and 'rows' in data and len(data['rows']) > 0:
                        result_list = []
                        for row in data['rows']:
                            if len(row) >= 5:
                                date_str = row[9] if len(row) > 9 else row[0][:10].replace('-', '')
                                if len(date_str) == 8 and date_str.isdigit():
                                    year = date_str[:4]
                                    month = date_str[4:6]
                                    day = date_str[6:8]
                                    date_str = f"{year}-{month}-{day}"
                                result_list.append({
                                    'date': date_str,
                                    'open': float(row[1]) if row[1] else 0,
                                    'close': float(row[2]) if row[2] else 0,
                                    'high': float(row[3]) if row[3] else 0,
                                    'low': float(row[4]) if row[4] else 0,
                                    'volume': int(float(row[6])) if row[6] else 0
                                })
        except Exception as e:
            print(f"Wind MCP 获取指数数据失败 {index_key}: {e}")
        
        # 如果 Wind MCP 失败，使用东方财富备用
        if not result_list or len(result_list) < 10:
            print(f"Wind MCP 返回数据不足，尝试使用东方财富备用数据源 {index_key}")
            result_list = cls.get_index_history_from_eastmoney(index_key, days)
        
        if result_list and len(result_list) > 0:
            cls._cache[cache_key] = result_list
            cls._cache_time[cache_key] = datetime.now().timestamp()
            return result_list
        
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
        """获取指数收盘价序列（原始价格数据，前端自己计算收益率）"""
        history = cls.get_index_history(index_key, days)
        if not history or len(history) < 2:
            return None
        
        result = []
        for item in history:
            result.append({
                'date': item['date'],
                'close': item['close']
            })
        
        return result
    
    @classmethod
    def get_multiple_index_data(cls, index_keys, days=90):
        """批量获取多个指数数据"""
        result = {}
        for key in index_keys:
            try:
                data = cls.get_index_series(key, days)
                if data:
                    result[key] = data
            except Exception as e:
                print(f"获取指数 {key} 数据时出错: {e}")
                # 如果获取失败，跳过该指数，继续获取其他指数
                continue
        return result
