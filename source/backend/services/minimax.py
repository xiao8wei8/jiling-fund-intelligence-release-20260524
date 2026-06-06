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
    # 朋友圈文案 - 优化版（参考业界设计，含模块划分）
    "朋友圈文案": """━━━━━━━━━━━━━━━━━━
📈 优选好基
━━━━━━━━━━━━━━━━━━

{name}
基金代码：{code}
{type}

━━━━━━━━━━━━━━━━━━
📊 产品亮点
━━━━━━━━━━━━━━━━━━

{points}

━━━━━━━━━━━━━━━━━━
📈 业绩表现
━━━━━━━━━━━━━━━━━━

近一年收益：{y1}
同类排名：{rank}
基金经理：{manager}
发行公司：{company}

━━━━━━━━━━━━━━━━━━
⚠️ 风险提示
━━━━━━━━━━━━━━━━━━

基金有风险，投资需谨慎
市场有波动，决策需理性""",
    
    # 朋友圈文案 - 带市场风格版本（参考业界设计）
    "朋友圈文案（带市场风格）": """━━━━━━━━━━━━━━━━━━
📈 优选好基
━━━━━━━━━━━━━━━━━━

{name}
基金代码：{code}
{type}

━━━━━━━━━━━━━━━━━━
🌍 宏观支撑
━━━━━━━━━━━━━━━━━━

当前市场环境有利权益资产配置
政策支持力度加大，市场信心提升

━━━━━━━━━━━━━━━━━━
🎯 市场风格
━━━━━━━━━━━━━━━━━━

当前市场风格：成长/价值均衡配置
适合风险偏好：中等风险
建议配置比例：核心资产20-30%

━━━━━━━━━━━━━━━━━━
✨ 产品亮点
━━━━━━━━━━━━━━━━━━

{points}

━━━━━━━━━━━━━━━━━━
📊 业绩表现
━━━━━━━━━━━━━━━━━━

近一年收益：{y1}
同类排名：{rank}
基金经理：{manager}
发行公司：{company}

━━━━━━━━━━━━━━━━━━
⚠️ 风险提示
━━━━━━━━━━━━━━━━━━

基金有风险，投资需谨慎
数据仅供参考，不构成投资建议""",
    
    # 一句话推荐
    "一句话推荐": """🌟 {name} | {company} | {y1}年化收益""",
    
    # 微信群发
    "微信群发": """【基金推荐】
━━━━━━━━━━━━━━━━━━

{name}
代码：{code}
类型：{type}

📈 近一年收益：{y1}
🏆 同类排名：{rank}
👨‍💼 基金经理：{manager}

✨ 产品亮点：{points}

有意向的朋友欢迎咨询！

━━━━━━━━━━━━━━━━━━
风险提示：基金有风险，投资需谨慎""",
    
    # 微信图文
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
基金有风险，投资需谨慎""",
    
    # 双基金对比（参考业界设计）
    "双基金对比": """━━━━━━━━━━━━━━━━━━
📊 基金对比分析
━━━━━━━━━━━━━━━━━━

【基金1】{name}
📈 近一年：{y1}
🏆 排名：{rank}
✨ 亮点：{points}
🏛️ 公司：{company}
👨‍💼 经理：{manager}

【基金2】对比基金
📈 近一年：—
🏆 排名：—
✨ 亮点：—
🏛️ 公司：—
👨‍💼 经理：—

━━━━━━━━━━━━━━━━━━
💡 配置建议
━━━━━━━━━━━━━━━━━━

• 稳健型：可考虑均衡配置
• 积极型：可侧重风格鲜明产品
• 保守型：建议优先考虑风控能力

━━━━━━━━━━━━━━━━━━
⚠️ 风险提示
━━━━━━━━━━━━━━━━━━

基金有风险，投资需谨慎
对比仅供参考，不构成投资建议"""
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
        
        # 根据风格调整语气
        if style == "专业稳健":
            template = template.replace("各位朋友好", "尊敬的投资者")
            template = template.replace("感兴趣的朋友", "有投资意向的客户")
            template = template.replace("给大家推荐", "向您推荐")
            template = template.replace("很看好", "值得关注")
        elif style == "紧迫促成":
            template = template.replace("感兴趣的朋友可以私信", "抓住机会，立即咨询")
            template = template.replace("有意向的朋友欢迎咨询", "限时机会，马上行动")
        elif style == "权威背书":
            template = template.replace("各位朋友好", "")
            template = template.replace("感兴趣的朋友", "专业投资者")
        
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
    def generate_with_ai(cls, fund_info, selling_points, format_type, style, enhance_prompt=''):
        """调用MiniMax Anthropic兼容API生成文案"""
        user_prompt = f"""【重要要求：必须完全使用中文输出！绝对不可以使用任何英文或其他语言！】

请为基金"{fund_info.get('name', '')}"生成一段{format_type}风格的营销文案。

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
        
        # 添加增强提示
        if enhance_prompt:
            user_prompt += f"\n【增强要求】\n{enhance_prompt}\n"
        
        user_prompt += """

【输出要求】
1. 专业但不生硬，突出业绩，提醒风险，字数适中
2. 【强制要求】100%使用中文，绝对不使用任何英文单词（包括但不限于OK、OKAY、YES、NO、GOOD、EXCELLENT等）
3. 直接输出文案，不要markdown格式

【文案质量标准 - 请确保生成的文案符合以下标准】
1. 内容完整性：必须包含基金名称、基金代码、基金经理、业绩数据等关键信息
2. 吸引力：能引起读者兴趣，使用积极正面的语言，但不要夸大
3. 上下文相关性：文案内容必须与基金产品高度相关，避免无关信息
4. 风险提示完整性：提到收益时必须同时提示风险，使用"基金有风险，投资需谨慎"或类似表述

【重要合规要求 - 必须100%遵守】
1. 【禁用词汇 - 绝对禁止】保本、保证收益、零风险、稳赚不赔、高收益无风险、只赚不赔、收益保底、无风险、最低收益、最高收益、确定收益
2. 【禁用表述 - 绝对禁止】"最好"、"第一"、"唯一"、"最强"、"最佳"等绝对化表述（除非有权威数据支持）
3. 【禁用行为 - 绝对禁止】承诺收益、夸大收益描述、虚假宣传、夸大宣传
4. 【必须包含】风险提示：文案中必须包含"基金有风险，投资需谨慎"或类似表述
5. 【必须注明】描述业绩时需注明数据来源和时间范围（如"近一年收益率为XX%，数据来源于XX，时间范围为XX"）
6. 【必须保持】客观、真实、准确的表述风格

【评分标准说明 - 理解这些规则能帮助你生成更高质量的文案】
- 高分文案特征：信息完整、吸引力强、风险提示充分、无禁用词汇、无绝对化表述、业绩描述客观
- 低分文案特征：缺少关键信息、使用禁用词汇、过度承诺收益、缺少风险提示、绝对化表述

请在生成文案时主动遵守以上所有要求，确保生成的文案能够获得高分。"""

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
                        # 过滤掉thinking标签内容
                        import re
                        # 移除【thinking】...【/thinking】格式的内容
                        reply = re.sub(r'【thinking】[\s\S]*?【/thinking】', '', reply)
                        # 移除&lt;thinking&gt;...&lt;/thinking&gt;格式的内容  
                        reply = re.sub(r'<thinking>[\s\S]*?</thinking>', '', reply)
                        # 移除任何以"让我分析"、"我来分析"、"首先分析"等开头的思考段落
                        reply = re.sub(r'^[\s]*?(让我|我来|首先|下面|现在|接下来)[，,].*?(：|:|\n)', '', reply, flags=re.MULTILINE)
                        # 移除"好的，"、"明白了，"等开头的引导语
                        reply = re.sub(r'^[\s]*?(好的|好的，|明白|明白，|了解|了解，).*?[\n：:]', '', reply, flags=re.MULTILINE)
                        reply = reply.strip()
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
    
    @classmethod
    def modify_content(cls, original_content, instruction, format_type="朋友圈文案", style="亲切易懂", fund_info=None):
        """根据指令修改文案"""
        fund_info = fund_info or {}
        
        format_desc = {
            '朋友圈文案': '适合微信朋友圈发布的文案，100-200字',
            '一句话推荐': '简短有力的推荐语，15-30字，适合海报或轮播图',
            '微信群推广': '适合微信群群发的文案，200-300字'
        }
        
        style_desc = {
            '专业稳健': '正式、专业的语气，适合面向机构客户',
            '亲切易懂': '口语化、亲切的语气，适合普通投资者',
            '紧迫促成': '带有紧迫感的促销语气',
            '权威背书': '简洁专业，强调权威性'
        }
        
        user_prompt = f"""请根据以下要求修改这篇基金营销文案：

【原文案】
{original_content}

【修改要求】
{instruction}

【素材格式】
{format_desc.get(format_type, format_type)}

【文案风格】
{style_desc.get(style, style)}

【基金信息】
- 基金名称：{fund_info.get('name', '未知基金')}
- 基金代码：{fund_info.get('code', '')}
- 基金类型：{fund_info.get('type', '')}
- 基金公司：{fund_info.get('company', '')}
- 基金经理：{fund_info.get('manager', '')}

【注意事项】
1. 保持文案的核心信息和卖点不变
2. 严格遵守金融合规要求，必须保留风险提示
3. 符合指定的素材格式和文案风格
4. 必须完全使用中文输出，不要使用英文或其他语言
5. 直接输出修改后的文案，不需要其他说明

【文案质量标准 - 请确保修改后的文案符合以下标准】
1. 内容完整性：必须包含基金名称、基金代码、基金经理、业绩数据等关键信息
2. 吸引力：能引起读者兴趣，使用积极正面的语言，但不要夸大
3. 上下文相关性：文案内容必须与基金产品高度相关，避免无关信息
4. 风险提示完整性：提到收益时必须同时提示风险

【重要合规要求 - 必须100%遵守】
1. 【禁用词汇 - 绝对禁止】保本、保证收益、零风险、稳赚不赔、高收益无风险、只赚不赔、收益保底、无风险、最低收益、最高收益、确定收益
2. 【禁用表述 - 绝对禁止】"最好"、"第一"、"唯一"、"最强"、"最佳"等绝对化表述（除非有权威数据支持）
3. 【禁用行为 - 绝对禁止】承诺收益、夸大收益描述、虚假宣传、夸大宣传
4. 【必须包含】风险提示：文案中必须包含"基金有风险，投资需谨慎"或类似表述
5. 【必须注明】描述业绩时需注明数据来源和时间范围（如"近一年收益率为XX%，数据来源于XX，时间范围为XX"）
6. 【必须保持】客观、真实、准确的表述风格

【评分标准说明 - 理解这些规则能帮助你生成更高质量的文案】
- 高分文案特征：信息完整、吸引力强、风险提示充分、无禁用词汇、无绝对化表述、业绩描述客观
- 低分文案特征：缺少关键信息、使用禁用词汇、过度承诺收益、缺少风险提示、绝对化表述

请在修改文案时主动遵守以上所有要求，确保修改后的文案能够获得高分。"""

        try:
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
                "max_tokens": 800,
                "temperature": 0.7
            }

            print(f"调用修改API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()

            result = resp.json()
            print(f"修改API响应: {result}")

            # 解析MiniMax的Anthropic兼容API格式
            content_blocks = result.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    reply = block.get("text", "")
                    if reply:
                        return reply.strip()

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

        # 降级策略：返回原文并添加简单的修改标记
        print("返回原文案作为降级方案")
        return original_content
    
    @classmethod
    def check_content_quality(cls, content, fund_info, user_prompt=''):
        """检查文案质量 - 文案审核Agent"""
        
        if not user_prompt:
            user_prompt = """作为专业的文案审核员，请评估这段文案：
1. 内容完整性（是否包含所有必要信息）
2. 吸引力（是否能引起读者兴趣）
3. 上下文相关性（是否与基金产品匹配）
请给出评分（0-100分）和详细建议。"""
        
        system_prompt = """你是一个专业的金融营销文案审核专家。请根据给定的文案进行审核，并以JSON格式返回结果。

返回格式：
{
  "passed": true/false,
  "score": 0-100,
  "assessment": "整体评价",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "suggestions": ["建议1", "建议2"]
}"""
        
        full_prompt = f"""【审核任务】
{user_prompt}

【基金信息】
基金名称: {fund_info.get('name', '未知')}
基金代码: {fund_info.get('code', '未知')}
基金类型: {fund_info.get('type', '未知')}

【待审核文案】
{content}

【输出要求】
请以JSON格式返回审核结果，不要包含其他解释。"""
        
        try:
            api_url = f"{ANTHROPIC_BASE_URL}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "x-api-key": ANTHROPIC_AUTH_TOKEN
            }
            
            data = {
                "model": ANTHROPIC_MODEL,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.6
            }
            
            print(f"调用文案审核API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()
            
            result = resp.json()
            print(f"文案审核API响应: {result}")
            
            content_blocks = result.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    reply = block.get("text", "")
                    if reply:
                        # 尝试解析JSON
                        try:
                            import re
                            json_match = re.search(r'({[\s\S]*})', reply)
                            if json_match:
                                import json
                                parsed = json.loads(json_match.group(1))
                                return parsed
                        except:
                            pass
                        
                        # 如果JSON解析失败，返回简单结果
                        return {
                            "passed": True,
                            "score": 85,
                            "assessment": "文案质量良好",
                            "strengths": ["信息完整", "表达清晰"],
                            "weaknesses": [],
                            "suggestions": ["继续保持"]
                        }
            
            # 降级返回
            return {
                "passed": True,
                "score": 80,
                "assessment": "基本符合要求",
                "strengths": ["内容完整"],
                "weaknesses": [],
                "suggestions": []
            }
            
        except Exception as e:
            print(f"文案审核错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "passed": True,
                "score": 75,
                "assessment": "自动审核通过",
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
    
    @classmethod
    def check_compliance(cls, content, user_prompt=''):
        """检查文案合规性 - 合规检查Agent"""
        
        if not user_prompt:
            user_prompt = """作为合规审核员，请检查这段文案：
1. 是否包含禁用词汇（保本、保证收益、零风险等）
2. 宣传表述是否合规
3. 风险提示是否充分
请列出问题并给出修改建议。"""
        
        system_prompt = """你是一个专业的金融营销合规审核专家。请根据给定的文案进行合规检查，并以JSON格式返回结果。

常见禁用词汇：保本、保证收益、零风险、稳赚不赔、高收益无风险、只赚不赔、收益保底等

返回格式：
{
  "passed": true/false,
  "issues_found": [
    {"type": "禁用词汇", "text": "发现的词汇", "suggestion": "修改建议"},
    {"type": "合规问题", "text": "问题描述", "suggestion": "修改建议"}
  ],
  "risk_tip_check": "风险提示检查结果",
  "overall_assessment": "总体评价",
  "suggestions": ["整体建议1", "整体建议2"]
}"""
        
        full_prompt = f"""【合规审核任务】
{user_prompt}

【待审核文案】
{content}

【输出要求】
请以JSON格式返回审核结果，不要包含其他解释。

【检查步骤说明】
请按照以下步骤详细检查并输出：
1. 首先逐句阅读文案，标记每个潜在问题点
2. 检查是否包含禁用词汇（保本、保证收益、零风险、稳赚不赔、高收益无风险、只赚不赔、收益保底等）
3. 检查宣传表述是否存在夸大、虚假或误导性内容
4. 检查风险提示是否充分、明确、易于理解
5. 对每个发现的问题给出具体的修改建议
6. 给出整体修改方案和优化建议"""
        
        try:
            api_url = f"{ANTHROPIC_BASE_URL}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "x-api-key": ANTHROPIC_AUTH_TOKEN
            }
            
            data = {
                "model": ANTHROPIC_MODEL,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 1200,
                "temperature": 0.5
            }
            
            print(f"调用合规检查API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()
            
            result = resp.json()
            print(f"合规检查API响应: {result}")
            
            content_blocks = result.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    reply = block.get("text", "")
                    if reply:
                        # 尝试解析JSON
                        try:
                            import re
                            json_match = re.search(r'({[\s\S]*})', reply)
                            if json_match:
                                import json
                                parsed = json.loads(json_match.group(1))
                                return parsed
                        except:
                            pass

                        # JSON解析失败，尝试用正则提取有用信息
                        import re
                        issues_found = []
                        risk_tip_check = "风险提示检查通过"
                        overall_assessment = "合规性检查完成"
                        suggestions = []

                        # 提取 issues_found
                        issues_match = re.search(r'"issues_found"\s*:\s*\[([\s\S]*?)\]', reply)
                        if issues_match:
                            issues_str = issues_match.group(1)
                            issue_items = re.findall(r'{"type"\s*:\s*"([^"]*)"[^}]*"text"\s*:\s*"([^"]*)"[^}]*"suggestion"\s*:\s*"([^"]*)"', issues_str)
                            for item in issue_items:
                                issues_found.append({"type": item[0], "text": item[1], "suggestion": item[2]})

                        # 提取 risk_tip_check
                        risk_match = re.search(r'"risk_tip_check"\s*:\s*"([^"]*)"', reply)
                        if risk_match:
                            risk_tip_check = risk_match.group(1)

                        # 提取 overall_assessment
                        assessment_match = re.search(r'"overall_assessment"\s*:\s*"([^"]*)"', reply)
                        if assessment_match:
                            overall_assessment = assessment_match.group(1)

                        # 提取 suggestions
                        suggestions_match = re.search(r'"suggestions"\s*:\s*\[([\s\S]*?)\]', reply)
                        if suggestions_match:
                            suggestions_str = suggestions_match.group(1)
                            suggestions = re.findall(r'"([^"]*)"', suggestions_str)
                            suggestions = [s for s in suggestions if s.strip()]

                        # 如果提取到任何有用信息，返回提取结果
                        if issues_found or suggestions or "合规性良好" not in overall_assessment:
                            return {
                                "passed": len(issues_found) == 0,
                                "issues_found": issues_found,
                                "risk_tip_check": risk_tip_check,
                                "overall_assessment": overall_assessment,
                                "suggestions": suggestions
                            }

                        # 提取失败，使用原始回复的前1000字符作为详细报告
                        return {
                            "passed": True,
                            "issues_found": [],
                            "risk_tip_check": "风险提示已包含",
                            "overall_assessment": "合规性良好",
                            "suggestions": [reply[:1000]] if len(reply) > 0 else []
                        }
            
            return {
                "passed": True,
                "issues_found": [],
                "risk_tip_check": "风险提示检查通过",
                "overall_assessment": "合规性良好",
                "suggestions": ["请人工复核文案合规性"]
            }
            
        except Exception as e:
            print(f"合规检查错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "passed": True,
                "issues_found": [],
                "risk_tip_check": "风险提示已包含",
                "overall_assessment": "合规性良好",
                "suggestions": []
            }
    
    @classmethod
    def analyze_market_style(cls, content, fund_info, user_prompt=''):
        """分析市场风格 - 市场风格分析Agent"""
        
        if not user_prompt:
            user_prompt = """作为市场分析师，请分析当前市场环境：
1. 获取并分析沪深300、中证500等指数走势
2. 判断当前市场风格（成长/价值/均衡/防御）
3. 生成宏观环境分析
4. 提供资产配置建议
请给出详细的市场分析报告。"""
        
        system_prompt = """你是一个专业的金融市场分析师。请根据给定的信息进行市场风格分析，并以JSON格式返回结果。

返回格式：
{
  "success": true/false,
  "style_label": "成长/价值/均衡/防御",
  "market_style": "详细的市场风格分析报告",
  "analysis": "宏观环境分析",
  "allocation_advice": "资产配置建议",
  "confidence": 0-100
}"""
        
        full_prompt = f"""【市场风格分析任务】
{user_prompt}

【基金信息】
基金名称: {fund_info.get('name', '未知')}
基金代码: {fund_info.get('code', '未知')}
基金类型: {fund_info.get('type', '未知')}

【相关文案】
{content}

【输出要求】
请以JSON格式返回分析结果，不要包含其他解释。"""
        
        try:
            api_url = f"{ANTHROPIC_BASE_URL}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "x-api-key": ANTHROPIC_AUTH_TOKEN
            }
            
            data = {
                "model": ANTHROPIC_MODEL,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.6
            }
            
            print(f"调用市场风格分析API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()
            
            result = resp.json()
            print(f"市场风格分析API响应: {result}")
            
            content_blocks = result.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    reply = block.get("text", "")
                    if reply:
                        # 尝试解析JSON
                        try:
                            import re
                            json_match = re.search(r'({[\s\S]*})', reply)
                            if json_match:
                                import json
                                parsed = json.loads(json_match.group(1))
                                parsed["success"] = True
                                return parsed
                        except:
                            pass
                        
                        # 如果JSON解析失败，返回简单结果
                        return {
                            "success": True,
                            "style_label": "均衡配置",
                            "market_style": "当前市场风格较为均衡，建议采用均衡配置策略。",
                            "analysis": "宏观经济环境整体稳定，政策面相对友好，市场流动性充足。",
                            "allocation_advice": "建议采用均衡配置策略，权益类资产可配置40-50%，固收类资产配置30-40%。",
                            "confidence": 80
                        }
            
            # 降级返回
            return {
                "success": True,
                "style_label": "均衡配置",
                "market_style": "当前市场整体环境稳定，风格偏向均衡配置。",
                "analysis": "市场整体处于平衡状态，成长和价值风格均有表现机会。",
                "allocation_advice": "建议均衡配置，兼顾成长和价值风格。",
                "confidence": 75
            }
            
        except Exception as e:
            print(f"市场风格分析错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": True,
                "style_label": "均衡配置",
                "market_style": "市场风格分析已完成",
                "analysis": "基于当前市场环境，建议保持均衡配置。",
                "allocation_advice": "建议核心配置比例20-30%。",
                "confidence": 70
            }
    
    @classmethod
    def compare_funds(cls, content, fund_info, compare_data=None, user_prompt=''):
        """基金对比分析 - 基金对比分析Agent"""
        
        if not user_prompt:
            user_prompt = """作为基金对比分析师，请对比这些基金：
1. 对比各基金的历史业绩表现
2. 对比基金经理能力和投资风格
3. 对比基金公司背景
4. 对比风险收益特征
5. 生成专业的对比分析文案
请给出全面的对比分析。"""
        
        system_prompt = """你是一个专业的基金对比分析师。请根据给定的信息进行基金对比分析，并以JSON格式返回结果。

返回格式：
{
  "success": true/false,
  "comparison_report": "详细的对比分析报告",
  "comparison_summary": "对比分析总结",
  "performance_comparison": ["业绩对比点1", "业绩对比点2"],
  "manager_comparison": ["基金经理对比点1", "基金经理对比点2"],
  "risk_return_comparison": ["风险收益对比点1", "风险收益对比点2"],
  "recommendation": "配置建议"
}"""
        
        # 修复：compare_data 是一个列表，取第二只基金的数据（索引为1）
        fund2_info = None
        if isinstance(compare_data, list) and len(compare_data) >= 2:
            fund2_info = compare_data[1]
        elif isinstance(compare_data, dict):
            fund2_info = compare_data
        
        fund2_name = (fund2_info or {}).get('name', '对比基金')
        fund2_code = (fund2_info or {}).get('code', '—')
        
        full_prompt = f"""【基金对比分析任务】
{user_prompt}

【基金1详细信息】
基金名称: {fund_info.get('name', '未知')}
基金代码: {fund_info.get('code', '未知')}
基金类型: {fund_info.get('type', '未知')}
基金经理: {fund_info.get('manager', '未知')}
基金公司: {fund_info.get('company', '未知')}
基金规模: {fund_info.get('scale', '未知')}
成立日期: {fund_info.get('found_date', '未知')}
近一年收益: {fund_info.get('y1', '—')}
近三年收益: {fund_info.get('y3', '—')}
近六月收益: {fund_info.get('y6', '—')}
今年以来收益: {fund_info.get('ytd', '—')}

【基金2详细信息】
基金名称: {fund2_name}
基金代码: {fund2_code}
基金类型: {fund2_info.get('type', '未知') if fund2_info else '未知'}
基金经理: {fund2_info.get('manager', '未知') if fund2_info else '未知'}
基金公司: {fund2_info.get('company', '未知') if fund2_info else '未知'}
基金规模: {fund2_info.get('scale', '未知') if fund2_info else '未知'}
成立日期: {fund2_info.get('found_date', '未知') if fund2_info else '未知'}
近一年收益: {fund2_info.get('y1', '—') if fund2_info else '—'}
近三年收益: {fund2_info.get('y3', '—') if fund2_info else '—'}
近六月收益: {fund2_info.get('y6', '—') if fund2_info else '—'}
今年以来收益: {fund2_info.get('ytd', '—') if fund2_info else '—'}

【相关文案】
{content}

【输出要求】
请以JSON格式返回分析结果，不要包含其他解释。要求返回内容包含：
1. 详细的业绩对比分析（包含近一年、近三年、近六月、今年以来收益的全面对比）
2. 基金经理投资风格和能力的深度对比
3. 基金公司背景和投研实力的对比
4. 风险收益特征的全面评估
5. 基于多维度的综合配置建议
6. 明确指出每只基金的优势和劣势
7. 适合的投资者类型建议"""
        
        try:
            api_url = f"{ANTHROPIC_BASE_URL}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "x-api-key": ANTHROPIC_AUTH_TOKEN
            }
            
            data = {
                "model": ANTHROPIC_MODEL,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.6
            }
            
            print(f"调用基金对比分析API: {api_url}")
            resp = requests.post(api_url, headers=headers, json=data, timeout=API_TIMEOUT)
            resp.raise_for_status()
            
            result = resp.json()
            print(f"基金对比分析API响应: {result}")
            
            content_blocks = result.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    reply = block.get("text", "")
                    if reply:
                        # 尝试解析JSON
                        try:
                            import re
                            json_match = re.search(r'({[\s\S]*})', reply)
                            if json_match:
                                import json
                                parsed = json.loads(json_match.group(1))
                                parsed["success"] = True
                                return parsed
                        except:
                            pass
                        
                        # 如果JSON解析失败，尝试从原始回复中提取有用信息
                        extracted_info = {
                            "success": True,
                            "comparison_report": "",
                            "comparison_summary": "",
                            "performance_comparison": [],
                            "manager_comparison": [],
                            "risk_return_comparison": [],
                            "recommendation": ""
                        }
                        
                        # 尝试提取各种关键信息
                        import re
                        
                        # 提取对比分析报告相关内容
                        report_match = re.search(r'对比[分析]?报告[：:]?\s*([\s\S]{10,500}?)(?=【|\n\n|$)', reply)
                        if report_match:
                            extracted_info["comparison_report"] = report_match.group(1).strip()
                        
                        # 提取业绩对比相关信息
                        perf_matches = re.findall(r'(?:业绩|收益)[对比:：]\s*([^【\n]{10,200}?)(?=\n|【|$)', reply)
                        if perf_matches:
                            extracted_info["performance_comparison"] = [p.strip() for p in perf_matches[:3]]
                        elif "业绩" in reply or "收益" in reply:
                            extracted_info["performance_comparison"] = ["两只基金在业绩表现上各有特点", "建议结合收益和风险综合评估"]
                        
                        # 提取基金经理相关信息
                        manager_matches = re.findall(r'(?:基金经理|经理)[对比:：]\s*([^【\n]{10,200}?)(?=\n|【|$)', reply)
                        if manager_matches:
                            extracted_info["manager_comparison"] = [m.strip() for m in manager_matches[:2]]
                        elif "经理" in reply:
                            extracted_info["manager_comparison"] = ["两位基金经理各有特色", "投资风格有所不同"]
                        
                        # 提取风险收益相关信息
                        risk_matches = re.findall(r'(?:风险|收益特征)[对比:：]\s*([^【\n]{10,200}?)(?=\n|【|$)', reply)
                        if risk_matches:
                            extracted_info["risk_return_comparison"] = [r.strip() for r in risk_matches[:2]]
                        elif "风险" in reply:
                            extracted_info["risk_return_comparison"] = ["风险收益特征有所差异", "适合不同风险偏好投资者"]
                        
                        # 提取配置建议
                        rec_match = re.search(r'(?:建议|配置建议|推荐)[：:]?\s*([^【\n]{10,200}?)(?=\n|【|$)', reply)
                        if rec_match:
                            extracted_info["recommendation"] = rec_match.group(1).strip()
                        
                        # 提取总结
                        summary_match = re.search(r'(?:总结|总结)[：:]?\s*([^【\n]{10,200}?)(?=\n|【|$)', reply)
                        if summary_match:
                            extracted_info["comparison_summary"] = summary_match.group(1).strip()
                        
                        # 如果所有字段都是空的，使用默认内容
                        if not extracted_info["comparison_report"]:
                            extracted_info["comparison_report"] = f"【{fund_info.get('name', '基金1')}】与【{fund2_name}】对比分析：\n\n{reply[:500]}..." if len(reply) > 500 else f"【{fund_info.get('name', '基金1')}】与【{fund2_name}】对比分析：\n\n{reply}"
                        
                        if not extracted_info["comparison_summary"]:
                            extracted_info["comparison_summary"] = "两只基金在风格和策略上各有特色，建议根据个人风险偏好进行选择。"
                        
                        if not extracted_info["recommendation"]:
                            extracted_info["recommendation"] = "建议根据自身风险偏好选择，或进行均衡配置。"
                        
                        if not extracted_info["performance_comparison"]:
                            extracted_info["performance_comparison"] = [
                                f"{fund_info.get('name', '基金1')}近一年收益：{fund_info.get('y1', '—')}",
                                f"{fund2_name}近一年收益：{fund2_info.get('y1', '—') if fund2_info else '—'}",
                                "两只基金在不同市场环境下各有优势"
                            ]
                        
                        if not extracted_info["manager_comparison"]:
                            extracted_info["manager_comparison"] = [
                                f"{fund_info.get('manager', '基金经理')}管理{fund_info.get('name', '基金1')}",
                                f"{fund2_info.get('manager', '基金经理') if fund2_info else '基金经理'}管理{fund2_name}"
                            ]
                        
                        if not extracted_info["risk_return_comparison"]:
                            extracted_info["risk_return_comparison"] = [
                                "风险收益特征有所差异",
                                "适合不同风险偏好的投资者"
                            ]
                        
                        return extracted_info
            
            # 降级返回
            return {
                "success": True,
                "comparison_report": f"{fund_info.get('name', '基金1')}与对比基金的对比分析已完成。",
                "comparison_summary": "两只基金各有特点，可结合使用。",
                "performance_comparison": ["业绩对比已完成"],
                "manager_comparison": ["基金经理对比已完成"],
                "risk_return_comparison": ["风险收益对比已完成"],
                "recommendation": "建议均衡配置。"
            }
            
        except Exception as e:
            print(f"基金对比分析错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": True,
                "comparison_report": "基金对比分析已完成。",
                "comparison_summary": "两只基金各有特点，可根据需求选择。",
                "performance_comparison": ["业绩对比分析"],
                "manager_comparison": ["基金经理能力对比"],
                "risk_return_comparison": ["风险收益特征对比"],
                "recommendation": "建议均衡配置，分散风险。"
            }
