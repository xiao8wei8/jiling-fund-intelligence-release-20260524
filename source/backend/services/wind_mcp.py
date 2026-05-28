"""Wind MCP Python 封装类"""
import subprocess
import json
import os
import sys


class WindMCP:
    """Wind MCP CLI 封装类"""
    
    @classmethod
    def _find_skill_dir(cls):
        """查找 Wind MCP skill目录，支持多种路径"""
        # 尝试多个可能的路径
        candidates = []
        
        # 1. 相对于当前文件，向上4级目录（项目根目录）
        try:
            path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                '.agents', 'skills', 'wind-mcp-skill'
            )
            if os.path.exists(path):
                return path
        except:
            pass
            
        # 2. 相对于当前文件，向上3级目录（jiling-source根目录）
        try:
            path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                '.agents', 'skills', 'wind-mcp-skill'
            )
            if os.path.exists(path):
                return path
        except:
            pass
            
        # 3. 相对于当前工作目录
        path = os.path.join(os.getcwd(), '.agents', 'skills', 'wind-mcp-skill')
        if os.path.exists(path):
            return path
            
        # 4. 相对于当前工作目录的source目录
        path = os.path.join(os.getcwd(), 'source', '.agents', 'skills', 'wind-mcp-skill')
        if os.path.exists(path):
            return path
            
        # 5. 相对于当前工作目录的source/backend目录
        path = os.path.join(os.getcwd(), 'source', 'backend', '.agents', 'skills', 'wind-mcp-skill')
        if os.path.exists(path):
            return path
            
        # 6. 检查环境变量
        wind_skill_dir = os.environ.get('WIND_MCP_SKILL_DIR', '')
        if wind_skill_dir and os.path.exists(wind_skill_dir):
            return wind_skill_dir
            
        return None

    @classmethod
    def _get_skill_dir(cls):
        """获取skill目录"""
        skill_dir = cls._find_skill_dir()
        if not skill_dir:
            # 如果找不到，尝试使用项目根目录的默认路径
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                '.agents', 'skills', 'wind-mcp-skill'
            )
        return skill_dir
    
    @classmethod
    def call(cls, server_type, tool_name, params):
        """调用 Wind MCP CLI"""
        # 只在调试模式下打印详细日志，避免生产环境日志噪音
        debug_mode = False
        
        if debug_mode:
            print(f"[Wind MCP] 调用: {server_type}.{tool_name}, 参数: {params}")
        
        try:
            skill_dir = cls._get_skill_dir()
            if debug_mode:
                print(f"[Wind MCP] Skill 目录: {skill_dir}")
            
            cli_path = os.path.join(skill_dir, 'scripts', 'cli.mjs')
            if debug_mode:
                print(f"[Wind MCP] CLI 路径: {cli_path}")
            
            if not os.path.exists(cli_path):
                if debug_mode:
                    print(f"[Wind MCP] 错误: CLI 脚本不存在!")
                return {
                    'success': False,
                    'error': f'CLI 脚本不存在: {cli_path}',
                    'code': 'CLI_NOT_FOUND'
                }
            
            # 检查 Node.js 是否存在
            try:
                subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
                if debug_mode:
                    print(f"[Wind MCP] Node.js 环境检查通过")
            except Exception as e:
                if debug_mode:
                    print(f"[Wind MCP] 错误: Node.js 不可用! {e}")
                return {
                    'success': False,
                    'error': f'Node.js 不可用: {e}',
                    'code': 'NODEJS_NOT_FOUND'
                }
            
            # 构建命令
            cmd = [
                'node',
                cli_path,
                'call',
                server_type,
                tool_name,
                json.dumps(params, ensure_ascii=False)
            ]
            if debug_mode:
                print(f"[Wind MCP] 执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=skill_dir
            )
            
            if debug_mode:
                print(f"[Wind MCP] 退出码: {result.returncode}")
                print(f"[Wind MCP] 标准输出: {repr(result.stdout)}")
                print(f"[Wind MCP] 标准错误: {repr(result.stderr)}")
            
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
                if debug_mode:
                    print(f"[Wind MCP] 解析后的数据: {data}")
                
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
            except json.JSONDecodeError as e:
                if debug_mode:
                    print(f"[Wind MCP] JSON 解析失败: {e}")
                return {
                    'success': True,
                    'data': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            if debug_mode:
                print(f"[Wind MCP] 调用超时")
            return {
                'success': False,
                'error': 'Wind MCP 调用超时',
                'code': 'TIMEOUT'
            }
        except Exception as e:
            if debug_mode:
                print(f"[Wind MCP] 调用异常: {e}")
                import traceback
                traceback.print_exc()
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
