#!/usr/bin/env python3
"""WindService 测试用例"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.wind import WindService
from services.eastmoney import EastmoneyService
from services.wind_mcp import WindMCP


def test_eastmoney_fund_detail():
    """测试1: 东方财富基金详情获取"""
    print("\n" + "="*60)
    print("测试1: 东方财富基金详情获取")
    print("="*60)
    
    fund_code = '004512'  # 海富通沪深300指数增强C
    print(f"正在获取基金 {fund_code} 的详情...")
    
    detail = EastmoneyService.get_fund_detail(fund_code)
    
    if detail:
        print(f"✅ 成功获取基金详情:")
        print(f"   - 基金名称: {detail.get('name', 'N/A')}")
        print(f"   - 基金代码: {detail.get('code', 'N/A')}")
        print(f"   - 基金类型: {detail.get('type', 'N/A')}")
        print(f"   - 基金公司: {detail.get('company', 'N/A')}")
        print(f"   - 基金经理: {detail.get('manager', 'N/A')}")
        print(f"   - 最新净值: {detail.get('nav', 'N/A')}")
        print(f"   - 净值日期: {detail.get('nav_date', 'N/A')}")
        print(f"   - 近1年收益: {detail.get('yield_1y', 'N/A')}")
        print(f"   - 近3年收益: {detail.get('yield_3y', 'N/A')}")
        print(f"   - 夏普比率: {detail.get('sharpe', 'N/A')}")
        print(f"   - 最大回撤: {detail.get('drawdown', 'N/A')}")
        return True
    else:
        print(f"❌ 获取基金详情失败")
        return False


def test_wind_mcp_connection():
    """测试2: Wind MCP连接测试"""
    print("\n" + "="*60)
    print("测试2: Wind MCP连接测试")
    print("="*60)
    
    print("正在测试Wind MCP连接...")
    
    try:
        # 测试指数K线数据获取
        result = WindMCP.get_index_kline('000300.SH', '20260101', '20260528', '10')
        
        if result.get('success'):
            data = result.get('data', {})
            if data and 'rows' in data:
                rows = data['rows']
                print(f"✅ Wind MCP 连接成功!")
                print(f"   - 获取到 {len(rows)} 条沪深300数据")
                if rows:
                    print(f"   - 最新日期: {rows[-1][9] if len(rows[-1]) > 9 else 'N/A'}")
                    print(f"   - 最新收盘价: {rows[-1][2] if len(rows[-1]) > 2 else 'N/A'}")
                return True
            else:
                print(f"⚠️ Wind MCP 连接成功，但返回数据为空")
                print(f"   - 返回数据: {result}")
                return False
        else:
            print(f"❌ Wind MCP 调用失败")
            print(f"   - 错误: {result.get('error', 'Unknown error')}")
            print(f"   - 代码: {result.get('code', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ Wind MCP 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wind_service_verify():
    """测试3: WindService.verify_fund_data 综合测试"""
    print("\n" + "="*60)
    print("测试3: WindService.verify_fund_data 综合测试")
    print("="*60)
    
    fund_code = '004512'
    fund_name = '海富通沪深300指数增强C'
    
    # 测试文案（含合规问题）
    test_content = """
    海富通沪深300指数增强C（004512）近期表现出色！
    近一年收益率超过30%，稳赚不赔！
    绝对是最好的基金选择！
    """
    
    print(f"正在验证基金 {fund_code} ...")
    print(f"测试文案:\n{test_content}")
    
    try:
        result = WindService.verify_fund_data(
            fund_code=fund_code,
            fund_name=fund_name,
            content=test_content
        )
        
        if result.get('success'):
            print(f"\n✅ WindService 验证成功!")
            print(f"\n📊 基金信息:")
            fund_info = result.get('fund_info', {})
            print(f"   - 基金代码: {fund_info.get('fund_code')}")
            print(f"   - 基金名称: {fund_info.get('fund_name')}")
            print(f"   - 基金公司: {fund_info.get('fund_company')}")
            print(f"   - 基金经理: {fund_info.get('fund_manager')}")
            
            print(f"\n📈 市场数据:")
            market_data = result.get('market_data', {})
            print(f"   - 最新净值: {market_data.get('latest_nav', 'N/A')}")
            print(f"   - 日涨跌幅: {market_data.get('daily_return', 'N/A')}")
            print(f"   - 年涨跌幅: {market_data.get('yearly_return', 'N/A')}")
            
            print(f"\n⚖️ 风险指标:")
            risk_metrics = result.get('risk_metrics', {})
            print(f"   - 波动率: {risk_metrics.get('volatility', 'N/A')}")
            print(f"   - 夏普比率: {risk_metrics.get('sharp_ratio', 'N/A')}")
            print(f"   - 最大回撤: {risk_metrics.get('max_drawdown', 'N/A')}")
            print(f"   - 数据来源: {risk_metrics.get('data_source', 'N/A')}")
            
            print(f"\n✅ 合规检查:")
            data_analysis = result.get('data_analysis', {})
            print(f"   - 合规评分: {data_analysis.get('accuracy_score', 0)}分")
            
            issues = data_analysis.get('issues', [])
            if issues:
                print(f"   - 发现问题:")
                for issue in issues:
                    print(f"     • {issue}")
            else:
                print(f"   - 未发现问题")
            
            print(f"\n📋 验证报告:")
            print(result.get('verification_report', 'N/A'))
            
            return True
        else:
            print(f"❌ WindService 验证失败")
            print(f"   - 错误: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compliance_check():
    """测试4: 合规检查专项测试"""
    print("\n" + "="*60)
    print("测试4: 合规检查专项测试")
    print("="*60)
    
    fund_code = '004512'
    
    test_cases = [
        {
            'name': '正常文案',
            'content': '海富通沪深300指数增强C（004512）表现稳健。基金有风险，投资需谨慎。',
            'expected_issues_min': 0,
            'expected_issues_max': 0,
            'description': '标准合规文案，应无问题'
        },
        {
            'name': '缺少风险提示',
            'content': '海富通沪深300指数增强C（004512）近期上涨20%，收益表现优异！',
            'expected_issues_min': 1,
            'expected_issues_max': 2,
            'description': '提到收益但缺少风险提示'
        },
        {
            'name': '禁用词汇-保本',
            'content': '海富通沪深300指数增强C（004512）保本收益，稳赚不赔！',
            'expected_issues_min': 2,
            'expected_issues_max': 4,
            'description': '包含禁用词汇：保本、稳赚不赔'
        },
        {
            'name': '禁用词汇-绝对化表述',
            'content': '这是最好的基金，唯一的选择！基金有风险，投资需谨慎。',
            'expected_issues_min': 1,
            'expected_issues_max': 3,
            'description': '包含绝对化表述和缺少基金信息'
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n用例{i}: {case['name']}")
        print(f"  说明: {case['description']}")
        print(f"  文案: {case['content']}")
        
        result = WindService.verify_fund_data(
            fund_code=fund_code,
            fund_name='海富通沪深300指数增强C',
            content=case['content']
        )
        
        if result.get('success'):
            issues = result.get('data_analysis', {}).get('issues', [])
            actual_issues = len(issues)
            
            print(f"  预期问题数: {case['expected_issues_min']}-{case['expected_issues_max']}")
            print(f"  实际问题数: {actual_issues}")
            
            if case['expected_issues_min'] <= actual_issues <= case['expected_issues_max']:
                print(f"  ✅ 通过")
            else:
                print(f"  ❌ 未通过 - 问题数超出预期范围")
                all_passed = False
            
            if issues:
                print(f"  发现的问题:")
                for issue in issues:
                    print(f"    • {issue}")
        else:
            print(f"  ❌ 测试失败: {result.get('error')}")
            all_passed = False
    
    return all_passed


def test_multiple_funds():
    """测试5: 多基金数据获取测试"""
    print("\n" + "="*60)
    print("测试5: 多基金数据获取测试")
    print("="*60)
    
    fund_codes = [
        ('004512', '海富通沪深300指数增强C'),
        ('163406', '兴全合润混合'),
        ('003095', '中欧医疗健康混合A'),
    ]
    
    all_success = True
    
    for fund_code, fund_name in fund_codes:
        print(f"\n正在获取 {fund_name} ({fund_code}) 的数据...")
        
        try:
            result = WindService.verify_fund_data(
                fund_code=fund_code,
                fund_name=fund_name
            )
            
            if result.get('success'):
                fund_info = result.get('fund_info', {})
                market_data = result.get('market_data', {})
                
                print(f"  ✅ 成功")
                print(f"     - 基金名称: {fund_info.get('fund_name')}")
                print(f"     - 最新净值: {market_data.get('latest_nav', 'N/A')}")
                print(f"     - 年涨跌幅: {market_data.get('yearly_return', 'N/A')}")
            else:
                print(f"  ❌ 失败: {result.get('error')}")
                all_success = False
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            all_success = False
    
    return all_success


def test_index_data_backup():
    """测试6: 指数数据备份源测试"""
    print("\n" + "="*60)
    print("测试6: 指数数据备份源测试")
    print("="*60)
    
    from services.index_data import IndexDataService
    
    print("正在测试指数数据获取...")
    
    try:
        # 测试获取沪深300数据
        data = IndexDataService.get_index_history('hs300', 30)
        
        if data and len(data) > 0:
            print(f"✅ 获取沪深300数据成功!")
            print(f"   - 数据条数: {len(data)}")
            print(f"   - 最新日期: {data[-1]['date']}")
            print(f"   - 最新收盘价: {data[-1]['close']}")
            
            # 测试批量获取
            multi_data = IndexDataService.get_multiple_index_data(['hs300', 'zz500', 'sh'], 30)
            
            if multi_data:
                print(f"   - 批量获取指数: {', '.join(multi_data.keys())}")
            
            return True
        else:
            print(f"❌ 获取指数数据失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("WindService 测试套件")
    print("="*60)
    
    results = {}
    
    # 测试1: 东方财富基金详情
    results['test1_eastmoney'] = test_eastmoney_fund_detail()
    
    # 测试2: Wind MCP连接
    results['test2_wind_mcp'] = test_wind_mcp_connection()
    
    # 测试3: WindService综合测试
    results['test3_wind_service'] = test_wind_service_verify()
    
    # 测试4: 合规检查
    results['test4_compliance'] = test_compliance_check()
    
    # 测试5: 多基金测试
    results['test5_multi_funds'] = test_multiple_funds()
    
    # 测试6: 指数数据备份源
    results['test6_index_backup'] = test_index_data_backup()
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ 通过" if passed_test else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 项测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
