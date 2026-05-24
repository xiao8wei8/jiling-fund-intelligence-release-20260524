"""MiniMax AI 文案生成服务 - 使用Anthropic兼容API"""
import requests
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config

ANTHROPIC_BASE_URL = Config.ANTHROPIC_BASE_URL
ANTHROPIC_AUTH_TOKEN = Config.ANTHROPIC_AUTH_TOKEN
ANTHROPIC_MODEL = Config.ANTHROPIC_MODEL
API_TIMEOUT = Config.API_TIMEOUT_MS / 1000.0

TEMPLATES = {
    "朋友圈文案": """📈 {name}

各位朋友好！给大家推荐一只我很看好的基金——{name}！

近一年收益达到 {y1}，大幅跑赢同类平均水平！

✅ {points}

{company}出品，{manager}掌舵，值得信赖！

💬 感兴趣的朋友可以私信我了解详情~

⚠️ 基金有风险，投资需谨慎""",
    "一句话推荐": """🌟 {name} | {company} | {y1}年化收益""",
    "微信群发": """【基金推荐】
{name}
代码：{code}
类型：{type}

📈 近一年收益：{y1}
🏆 同类排名：{rank}
👨‍💼 基金经理：{manager}

有意向的朋友欢迎咨询！

风险提示：基金有风险，投资需谨慎""",
    "微信图文": """# {name}

## 基金概况
- 代码：{code}
- 类型：{type}
- 公司：{company}
- 经理：{manager}

## 业绩表现
- 近一年：{y1}
- 近三年：{y3}
- 排名：{rank}

## 推荐理由
1. {points}
2. {company}旗下产品
3. {manager}管理

## 风险提示
基金有风险，投资需谨慎"""
}

class MiniMaxService:
    """MiniMax AI 文案生成"""
    
    @classmethod
    def generate_copy(cls, fund_info, selling_points, format_type="朋友圈文案", style="亲切易懂"):
        """生成营销文案"""
        template = TEMPLATES.get(format_type, TEMPLATES["朋友圈文案"])
        
        if selling_points:
            if isinstance(selling_points[0], dict):
                points = "、".join([sp.get('title', '') for sp in selling_points[:3]])
            else:
                points = "、".join(selling_points[:3])
        else:
            points = "长期表现稳健"
        
        # 语气调整
        if style == "专业正式":
            template = template.replace("各位朋友好", "尊敬的投资者")
            template = template.replace("感兴趣的朋友", "有投资意向的客户")
        
        content = template.format(
            name=fund_info.get('name', '优质基金'),
            code=fund_info.get('code', ''),
            type=fund_info.get('type', '混合型'),
            company=fund_info.get('company', ''),
            manager=fund_info.get('manager', '专业经理'),
            y1=fund_info.get('y1', '+0%'),
            y3=fund_info.get('y3', '+0%'),
            rank=fund_info.get('rank', '前50%'),
            points=points
        )
        
        return content
    
    @classmethod
    def generate_with_ai(cls, fund_info, selling_points, format_type, style):
        """调用MiniMax Anthropic兼容API生成文案"""
        user_prompt = f"""请为基金"{fund_info.get('name', '')}"生成一段{format_type}风格的营销文案。

基金信息：
- 代码：{fund_info.get('code', '')}
- 公司：{fund_info.get('company', '')}
- 经理：{fund_info.get('manager', '')}
- 近一年收益：{fund_info.get('y1', '')}
- 风格：{style}

卖点：
"""
        for sp in (selling_points or []):
            if isinstance(sp, dict):
                user_prompt += f"- {sp.get('title', '')}: {sp.get('desc', '')}\n"
            else:
                user_prompt += f"- {sp}\n"
        
        user_prompt += """
要求：专业但不生硬，突出业绩，提醒风险，字数适中。直接输出文案，不要markdown格式。"""
        
        try:
            # 使用Anthropic兼容的API格式
            api_url = f"{ANTHROPIC_BASE_URL}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "x-api-key": ANTHROPIC_AUTH_TOKEN
            }
            
            data = {
                "model": ANTHROPIC_MODEL,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 512,
                "temperature": 0.7
            }
            
            print(f"调用API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()
            
            result = resp.json()
            print(f"API响应: {result}")
            
            # 检查API是否成功
            base_resp = result.get("base_resp", {})
            if base_resp.get("status_code", 0) != 0:
                error_msg = base_resp.get("status_msg", "未知错误")
                print(f"API错误: {error_msg}")
            else:
                # 解析MiniMax的Anthropic兼容API格式
                content_blocks = result.get("content", [])
                for block in content_blocks:
                    # 查找text类型的块（跳过thinking块）
                    if block.get("type") == "text" and block.get("text"):
                        reply = block.get("text", "")
                        if reply:
                            return reply.strip()
            
            # 备用解析方式
            if "error" in result:
                error_msg = result["error"].get("message", "未知错误")
                print(f"API错误: {error_msg}")
                
        except requests.exceptions.Timeout:
            print(f"API超时: {api_url}")
        except requests.exceptions.ConnectionError as e:
            print(f"API连接失败: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"API HTTP错误: {e}")
        except Exception as e:
            print(f"API未知错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 降级策略：使用模板生成
        print("使用模板生成文案作为降级方案")
        return cls.generate_copy(fund_info, selling_points, format_type, style)
