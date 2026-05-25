"""Wind MCP Python 封装类"""
import subprocess
import json
import os
import sys


class WindMCP:
    """Wind MCP CLI 封装类"""
    
    # skill 目录在项目根目录下
    SKILL_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        '.agents', 'skills', 'wind-mcp-skill'
    )
    CLI_PATH = os.path.join(SKILL_DIR, 'scripts', 'cli.mjs')
    
    @classmethod
    def call(cls, server_type, tool_name, params):
        """调用 Wind MCP CLI"""
        try:
            # 构建命令
            cmd = [
                'node',
                cls.CLI_PATH,
                'call',
                server_type,
                tool_name,
                json.dumps(params, ensure_ascii=False)
            ]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cls.SKILL_DIR
            )
            
            # 检查退出码
            if result.returncode != 0:
                # 解析错误信息
                try:
                    error_data = json.loads(result.stdout)
                    return {
                        'success': False,
                        'error': error_data.get('error', {}).get('agent_action', 'Unknown error'),
                        'code': error_data.get('error', {}).get('code', 'UNKNOWN')
                    }
                except:
                    return {
                        'success': False,
                        'error': result.stdout or result.stderr,
                        'code': 'UNKNOWN'
                    }
            
            # 解析成功结果
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict) and 'content' in data:
                    # CLI 返回格式：{"content": [{"type": "text", "text": "..."}]}
                    content_text = data['content'][0]['text']
                    inner_data = json.loads(content_text)
                    return {
                        'success': True,
                        'data': inner_data.get('data'),
                        'error': inner_data.get('error')
                    }
                else:
                    return {
                        'success': True,
                        'data': data
                    }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'data': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Wind MCP 调用超时',
                'code': 'TIMEOUT'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'code': 'EXCEPTION'
            }
    
    @classmethod
    def get_index_price(cls, index_name, indexes='最新成交价,涨跌幅'):
        """获取指数行情快照"""
        return cls.call(
            'index_data',
            'get_index_price_indicators',
            {'windcode': index_name, 'indexes': indexes}
        )
    
    @classmethod
    def get_index_kline(cls, index_name, begin_date, end_date, period='10'):
        """获取指数K线数据"""
        return cls.call(
            'index_data',
            'get_index_kline',
            {
                'windcode': index_name,
                'begin_date': begin_date,
                'end_date': end_date,
                'period': period
            }
        )
    
    @classmethod
    def get_fund_price(cls, fund_name, indexes='最新成交价,涨跌幅'):
        """获取基金行情快照"""
        return cls.call(
            'fund_data',
            'get_fund_price_indicators',
            {'windcode': fund_name, 'indexes': indexes}
        )
    
    @classmethod
    def get_fund_kline(cls, fund_name, begin_date, end_date, period='10'):
        """获取基金K线数据"""
        return cls.call(
            'fund_data',
            'get_fund_kline',
            {
                'windcode': fund_name,
                'begin_date': begin_date,
                'end_date': end_date,
                'period': period
            }
        )
    
    @classmethod
    def get_stock_price(cls, stock_name, indexes='最新成交价,涨跌幅'):
        """获取股票行情快照"""
        return cls.call(
            'stock_data',
            'get_stock_price_indicators',
            {'windcode': stock_name, 'indexes': indexes}
        )
    
    @classmethod
    def get_index_fundamentals(cls, question, lang='中文'):
        """获取指数基本面数据（NL）"""
        return cls.call(
            'index_data',
            'get_index_fundamentals',
            {'question': question, 'lang': lang}
        )
