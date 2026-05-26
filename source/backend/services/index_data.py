"""指数数据服务 - 使用 Wind MCP 获取沪深300、中证500等指数数据"""
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
    """指数数据获取服务 - 使用 Wind MCP"""
    
    INDEX_NAMES = {
        'hs300': '000300.SH',
        'zz500': '000905.SH',
        'sh': '000001.SH',
        'sz': '399001.SZ',
        'gem': '399006.SZ'
    }
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_index_history(cls, index_key, days=90):
        """获取指数历史数据（使用 Wind MCP）"""
        cache_key = f'index_{index_key}_{days}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            index_name = cls.INDEX_NAMES.get(index_key)
            if not index_name:
                return None
            
            # 使用 Wind MCP 获取K线数据
            end_date = datetime.now().strftime('%Y%m%d')
            begin_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            result = WindMCP.get_index_kline(index_name, begin_date, end_date, '10')
            
            if not result.get('success'):
                print(f"Wind MCP 调用失败: {result.get('error')}")
                return None
            
            data = result.get('data')
            if not data or 'rows' not in data:
                return None
            
            # 解析K线数据
            result_list = []
            for row in data['rows']:
                if len(row) >= 5:
                    # 从第9列获取日期(_DATE)，格式是 YYYYMMDD
                    date_str = row[9] if len(row) > 9 else row[0][:10].replace('-', '')
                    # 转换日期格式: 20260427 -> 2026-04-27
                    if len(date_str) == 8 and date_str.isdigit():
                        year = date_str[:4]
                        month = date_str[4:6]
                        day = date_str[6:8]
                        date_str = f"{year}-{month}-{day}"
                    # 第1列: OPEN, 第2列: MATCH(收盘价), 第3列: HIGH, 第4列: LOW
                    result_list.append({
                        'date': date_str,
                        'open': float(row[1]) if row[1] else 0,
                        'close': float(row[2]) if row[2] else 0,
                        'high': float(row[3]) if row[3] else 0,
                        'low': float(row[4]) if row[4] else 0,
                        'volume': int(float(row[6])) if row[6] else 0
                    })
            
            if result_list:
                cls._cache[cache_key] = result_list
                cls._cache_time[cache_key] = datetime.now().timestamp()
                return result_list
            
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
            try:
                data = cls.get_index_series(key, days)
                if data:
                    result[key] = data
            except Exception as e:
                print(f"获取指数 {key} 数据时出错: {e}")
                # 如果获取失败，跳过该指数，继续获取其他指数
                continue
        return result
