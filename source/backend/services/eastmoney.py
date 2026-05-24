"""东方财富数据服务 + akshare备用"""
import requests
import json
import re
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config

class EastmoneyService:
    """东方财富数据获取 (主数据源)"""
    
    FUND_LIST_URL = "https://fund.eastmoney.com/js/fundcode_search.js"
    PINGZHONG_BASE = "https://fund.eastmoney.com/pingzhongdata"
    SEARCH_URL = "https://fund.eastmoney.com/center/gridlist.html"
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_fund_list(cls):
        if 'fund_list' in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get('fund_list', 0) < cls.CACHE_DURATION:
                return cls._cache['fund_list']
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://fund.eastmoney.com/'
            }
            resp = requests.get(cls.FUND_LIST_URL, headers=headers, timeout=10)
            match = re.search(r'\[.*\]', resp.text, re.DOTALL)
            if match:
                funds = json.loads(match.group())
                result = [{'code': f[0], 'name': f[2], 'type': cls.normalize_type(f[3]), 'company': f[4]} for f in funds[:500]]
                cls._cache['fund_list'] = result
                cls._cache_time['fund_list'] = datetime.now().timestamp()
                return result
        except Exception as e:
            print(f"获取基金列表失败: {e}")
        return cls.get_backup_funds()
    
    @classmethod
    def get_fund_detail(cls, code):
        cache_key = f'detail_{code}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            url = f"{cls.PINGZHONG_BASE}/{code}.js"
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}
            resp = requests.get(url, headers=headers, timeout=10)
            text = resp.text
            
            data = {}
            nav_data = []
            
            name_match = re.search(r'var fS_name\s*=\s*"([^"]+)"', text)
            if name_match:
                data['name'] = name_match.group(1)
            
            code_match = re.search(r'var fS_code\s*=\s*"([^"]+)"', text)
            if code_match:
                data['code'] = code_match.group(1)
            
            # 尝试解析基金经理信息
            try:
                manager_start = text.find('var Data_currentFundManager =')
                if manager_start != -1:
                    # 找到结束位置
                    manager_end = text.find('];', manager_start)
                    if manager_end != -1:
                        manager_str = text[manager_start + len('var Data_currentFundManager ='):manager_end + 2].strip()
                        # 使用正则提取，避免eval问题
                        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', manager_str)
                        if name_match:
                            data['manager'] = name_match.group(1)
                        start_match = re.search(r'"startDate"\s*:\s*"([^"]+)"', manager_str)
                        if start_match:
                            data['manager_start'] = start_match.group(1)
            except Exception as e:
                print(f"解析基金经理失败: {e}")
            
            # 尝试解析公司信息
            try:
                company_start = text.find('var Data_company =')
                if company_start != -1:
                    company_end = text.find(';', company_start)
                    if company_end != -1:
                        company_str = text[company_start + len('var Data_company ='):company_end].strip()
                        company_data = json.loads(company_str)
                        data['company'] = company_data.get('shortName', company_data.get('name', ''))
            except Exception as e:
                print(f"解析公司信息失败: {e}")
            
            yield_1n_match = re.search(r'var Data_rateInSimilarPersent\s*=\s*(\{[^}]+\});', text)
            if yield_1n_match:
                try:
                    perf_data = json.loads(yield_1n_match.group(1))
                    data['yield_1y'] = perf_data.get('sy', perf_data.get('syl_1n', ''))
                    data['yield_3y'] = perf_data.get('syl_3y', '')
                    data['yield_6m'] = perf_data.get('syl_6y', '')
                    data['rank'] = perf_data.get('syl_1n_pct', '')
                    data['rank_3y'] = perf_data.get('syl_3y_pct', '')
                except:
                    pass
            
            net_worth_match = re.search(r'var Data_netWorthTrend\s*=\s*(\[.*?\]);', text)
            if net_worth_match:
                try:
                    nav_data = eval(net_worth_match.group(1))
                    if nav_data and len(nav_data) > 0:
                        last_nav = nav_data[-1]
                        data['nav'] = last_nav.get('y', '')
                        data['nav_date'] = datetime.fromtimestamp(last_nav.get('x', 0)/1000).strftime('%Y-%m-%d') if last_nav.get('x') else ''
                except:
                    pass
            
            if data.get('name'):
                y1_match = re.search(r'var syl_1n\s*=\s*"([^"]+)"', text)
                y3_match = re.search(r'var syl_3y\s*=\s*"([^"]+)"', text)
                y6_match = re.search(r'var syl_6m\s*=\s*"([^"]+)"', text)
                y3m_match = re.search(r'var syl_3m\s*=\s*"([^"]+)"', text)
                rank_match = re.search(r'var s_yl_1n_pct\s*=\s*"([^"]+)"', text)
                rank_3y_match = re.search(r'var s_yl_3y_pct\s*=\s*"([^"]+)"', text)
                
                yield_1y = y1_match.group(1) if y1_match else ''
                yield_3y = y3_match.group(1) if y3_match else ''
                yield_6m = y6_match.group(1) if y6_match else ''
                yield_3m = y3m_match.group(1) if y3m_match else ''
                rank_1y = rank_match.group(1) if rank_match else ''
                rank_3y = rank_3y_match.group(1) if rank_3y_match else ''
                
                fund_type = '混合型'
                fund_type_match = re.search(r'var fS_type\s*=\s*"([^"]+)"', text)
                if fund_type_match:
                    fund_type = fund_type_match.group(1)
                else:
                    fund_type = data.get('type', '混合型')
                
                result = {
                    'code': code, 
                    'name': data.get('name', ''), 
                    'type': fund_type, 
                    'company': data.get('company', ''), 
                    'manager': data.get('manager', ''), 
                    'nav': data.get('nav', ''), 
                    'nav_date': data.get('nav_date', ''), 
                    'yield_1y': cls.format_yield(yield_1y) if yield_1y else cls.format_yield(data.get('yield_1y', '')), 
                    'yield_3y': cls.format_yield(yield_3y) if yield_3y else cls.format_yield(data.get('yield_3y', '')), 
                    'yield_6m': cls.format_yield(yield_6m) if yield_6m else cls.format_yield(data.get('yield_6m', '')), 
                    'yield_3m': cls.format_yield(yield_3m), 
                    'rank': rank_1y if rank_1y else data.get('rank', ''), 
                    'rank_3y': rank_3y if rank_3y else data.get('rank_3y', ''), 
                }
                
                if nav_data and len(nav_data) > 0:
                    try:
                        vals = [float(p.get('y', 0)) for p in nav_data[-365:] if p.get('y', 0) > 0]
                        if len(vals) > 30:
                            returns = []
                            for i in range(1, len(vals)):
                                if vals[i-1] > 0:
                                    returns.append((vals[i] - vals[i-1]) / vals[i-1])
                            
                            if returns:
                                avg = sum(returns) / len(returns)
                                std = (sum((r - avg) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 1
                                if std > 0:
                                    risk_free = 0.03
                                    sharpe = (avg - risk_free/252) / (std ** 0.5)
                                    result['sharpe'] = f'{sharpe * (252**0.5) :.2f}'
                                else:
                                    result['sharpe'] = ''
                                
                                max_dd = 0.0
                                peak = vals[0]
                                for val in vals:
                                    if val > peak: peak = val
                                    dd = (peak - val) / peak
                                    if dd > max_dd: max_dd = dd
                                result['drawdown'] = cls.format_yield(f'-{max_dd * 100:.2f}')
                            else:
                                result['sharpe'] = ''
                                result['drawdown'] = ''
                        else:
                            result['sharpe'] = ''
                            result['drawdown'] = ''
                    except Exception as e:
                        print(f"计算夏普比率和回撤失败 {code}: {e}")
                        result['sharpe'] = ''
                        result['drawdown'] = ''
                else:
                    result['sharpe'] = ''
                    result['drawdown'] = ''
                
                # 从基金列表中获取公司信息
                all_funds = cls.get_fund_list()
                for f in all_funds:
                    if f['code'] == code:
                        if not result['company']:
                            result['company'] = f.get('company', '')
                        break
                
                # 从API响应中直接提取基金经理信息
                if not result['manager']:
                    try:
                        # 搜索基金经理名字，确保是在Data_currentFundManager中
                        manager_match = re.search(r'Data_currentFundManager.*?"name":"([^"]+)"', text, re.DOTALL)
                        if manager_match:
                            result['manager'] = manager_match.group(1)
                    except Exception as e:
                        print(f"提取基金经理名字失败: {e}")
                
                # 强制从备份基金列表中获取公司信息
                for f in cls.get_backup_funds():
                    if f['code'] == code:
                        result['company'] = f.get('company', '')
                        break
                
                cls._cache[cache_key] = result
                cls._cache_time[cache_key] = datetime.now().timestamp()
                return result
        except Exception as e:
            print(f"获取基金详情失败 {code}: {e}")
        return None
    
    @classmethod
    def get_fund_nav_history(cls, code, days=180):
        cache_key = f'nav_history_{code}_{days}'
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        try:
            # 从pingzhongdata API获取历史净值数据
            url = f"{cls.PINGZHONG_BASE}/{code}.js"
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}
            resp = requests.get(url, headers=headers, timeout=10)
            text = resp.text
            
            # 提取净值趋势数据
            net_worth_match = re.search(r'var Data_netWorthTrend\s*=\s*(\[.*?\]);', text)
            if net_worth_match:
                try:
                    nav_data = eval(net_worth_match.group(1))
                    if nav_data and len(nav_data) > 0:
                        data = []
                        for item in nav_data[-days:]:
                            date = datetime.fromtimestamp(item.get('x', 0)/1000).strftime('%Y-%m-%d')
                            nav = item.get('y', 0)
                            acc_nav = item.get('equityReturn', nav)
                            data.append({'date': date, 'nav': nav, 'acc_nav': acc_nav})
                        cls._cache[cache_key] = data
                        return data
                except Exception as e:
                    print(f"解析净值数据失败: {e}")
        except Exception as e:
            print(f"获取净值历史失败 {code}: {e}")
        return []
    
    @classmethod
    def get_hotspots(cls, code):
        detail = cls.get_fund_detail(code)
        if not detail:
            return []
        
        hotspots = []
        
        # 1. 收益率相关卖点
        yield_1y = detail.get('yield_1y', '')
        yield_6m = detail.get('yield_6m', '')
        yield_3y = detail.get('yield_3y', '')
        
        if yield_1y and yield_1y != '+0%':
            try:
                val_1y = float(yield_1y.replace('%', '').replace('+', ''))
                if val_1y > 30:
                    hotspots.append({'title': '优秀业绩', 'desc': f'近一年收益{yield_1y},表现强劲', 'tag': '高收益', 'source': '东方财富'})
                elif val_1y > 20:
                    hotspots.append({'title': '高收益基金', 'desc': f'近一年收益{yield_1y}', 'tag': '高收益', 'source': '东方财富'})
                elif val_1y > 10:
                    hotspots.append({'title': '稳健收益', 'desc': f'近一年收益{yield_1y}', 'tag': '稳健', 'source': '东方财富'})
                elif val_1y > 0:
                    hotspots.append({'title': '正收益', 'desc': f'近一年收益{yield_1y}', 'tag': '稳健', 'source': '东方财富'})
            except:
                pass
        
        if yield_6m and yield_6m != '+0%':
            try:
                val_6m = float(yield_6m.replace('%', '').replace('+', ''))
                if val_6m > 10:
                    hotspots.append({'title': '短期强劲', 'desc': f'近六月收益{yield_6m}', 'tag': '短期', 'source': '东方财富'})
            except:
                pass
        
        # 2. 排名相关卖点
        rank = detail.get('rank', '')
        if rank:
            try:
                if '/' in rank:
                    rank_num, total = rank.split('/')
                    rank_val = int(rank_num)
                    total_val = int(total)
                    percentile = (total_val - rank_val) / total_val * 100
                    if percentile >= 90:
                        hotspots.append({'title': '同类领先', 'desc': f'近一年排名{rank},位列前10%', 'tag': '排名', 'source': '东方财富'})
                    elif percentile >= 70:
                        hotspots.append({'title': '同类前列', 'desc': f'近一年排名{rank},表现优秀', 'tag': '排名', 'source': '东方财富'})
                    else:
                        hotspots.append({'title': '同类排名', 'desc': f'近一年排名{rank}', 'tag': '排名', 'source': '东方财富'})
                else:
                    hotspots.append({'title': '同类排名', 'desc': f'近一年排名{rank}', 'tag': '排名', 'source': '东方财富'})
            except:
                hotspots.append({'title': '同类排名', 'desc': f'近一年排名{rank}', 'tag': '排名', 'source': '东方财富'})
        
        # 3. 夏普比率和回撤相关卖点
        sharpe = detail.get('sharpe', '')
        drawdown = detail.get('drawdown', '')
        
        if sharpe:
            try:
                sharpe_val = float(sharpe)
                if sharpe_val >= 2.0:
                    hotspots.append({'title': '卓越风险收益比', 'desc': f'夏普比率{sharpe},风险调整后收益优异', 'tag': '夏普', 'source': '东方财富'})
                elif sharpe_val >= 1.0:
                    hotspots.append({'title': '良好风险收益比', 'desc': f'夏普比率{sharpe},风险收益均衡', 'tag': '夏普', 'source': '东方财富'})
                elif sharpe_val > 0:
                    hotspots.append({'title': '夏普比率', 'desc': f'夏普比率{sharpe}', 'tag': '夏普', 'source': '东方财富'})
            except:
                pass
        
        if drawdown and drawdown != '+0%':
            try:
                dd_val = abs(float(drawdown.replace('%', '').replace('-', '').replace('+', '')))
                if dd_val <= 10:
                    hotspots.append({'title': '波动较小', 'desc': f'最大回撤{drawdown},控制出色', 'tag': '回撤', 'source': '东方财富'})
                elif dd_val <= 20:
                    hotspots.append({'title': '回撤可控', 'desc': f'最大回撤{drawdown}', 'tag': '回撤', 'source': '东方财富'})
            except:
                pass
        
        # 4. 基金经理相关卖点
        manager = detail.get('manager', '')
        if manager:
            hotspots.append({'title': '专业管理', 'desc': f'由{manager}管理', 'tag': '经理', 'source': '东方财富'})
        
        # 5. 基金类型相关卖点
        fund_type = detail.get('type', '')
        company = detail.get('company', '')
        
        if '指数' in fund_type or 'ETF' in fund_type:
            hotspots.append({'title': '指数增强', 'desc': '跟踪指数,追求超额收益', 'tag': '指数', 'source': '东方财富'})
        
        if '混合' in fund_type:
            hotspots.append({'title': '灵活配置', 'desc': '股债混合,灵活调整', 'tag': '混合', 'source': '东方财富'})
        
        if '股票' in fund_type:
            hotspots.append({'title': '股票型基金', 'desc': '主要投资股票市场', 'tag': '股票', 'source': '东方财富'})
        
        if company:
            hotspots.append({'title': '品牌基金', 'desc': f'{company}出品', 'tag': '公司', 'source': '东方财富'})
        
        # 6. 如果没有足够的卖点,添加默认的
        if len(hotspots) == 0:
            hotspots.append({'title': '优质基金', 'desc': '值得关注的基金', 'tag': '推荐', 'source': '东方财富'})
        
        return hotspots[:6]
    
    @classmethod
    def search_funds(cls, keyword, limit=20):
        all_funds = cls.get_fund_list()
        if not keyword:
            return all_funds[:limit]
        keyword = keyword.lower()
        results = [f for f in all_funds if keyword in f['code'].lower() or keyword in f['name'].lower()]
        return results[:limit]
    
    @classmethod
    def normalize_type(cls, t):
        if not t: return '混合型'
        t = str(t).lower()
        if '股票' in t: return '股票型'
        elif '混合' in t: return '混合型'
        elif '债券' in t: return '债券型'
        elif '货币' in t: return '货币型'
        elif '指数' in t: return '指数型'
        elif 'QDII' in t: return 'QDII'
        return '混合型'
    
    @classmethod
    def format_yield(cls, v):
        if not v: return '+0%'
        try:
            if isinstance(v, str):
                v = v.strip()
                if '%' in v:
                    if v.startswith('-'):
                        return v
                    if not v.startswith('+'):
                        return f'+{v}'
                    return v
                v = float(v)
            return f'+{v:.2f}%' if v >= 0 else f'{v:.2f}%'
        except: return '+0%'
    
    @classmethod
    def get_backup_funds(cls):
        return [
            {"code": "163406", "name": "兴全合润混合（LOF）", "type": "混合型", "company": "兴证全球基金"},
            {"code": "003095", "name": "中欧医疗健康混合A", "type": "混合型", "company": "中欧基金"},
            {"code": "161005", "name": "富国天惠成长混合A", "type": "混合型", "company": "富国基金"},
            {"code": "110022", "name": "易方达消费行业股票", "type": "股票型", "company": "易方达基金"},
            {"code": "161725", "name": "招商中证白酒指数（LOF）", "type": "指数型", "company": "招商基金"},
            {"code": "320007", "name": "诺安成长混合", "type": "混合型", "company": "诺安基金"},
            {"code": "000198", "name": "天弘余额宝货币", "type": "货币型", "company": "天弘基金"},
            {"code": "004512", "name": "海富通沪深300指数增强C", "type": "指数型", "company": "海富通基金"},
            {"code": "001878", "name": "嘉实沪港深精选股票", "type": "股票型", "company": "嘉实基金"},
            {"code": "000961", "name": "天弘沪深300ETF联接", "type": "指数型", "company": "天弘基金"},
        ]
