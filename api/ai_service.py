import os
# Explicitly clear Google Application Credentials to avoid scope conflicts on machines where gcloud is logged in
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import json
import re

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
    print("WARNING: Gemini API Key not set correctly in .env")
genai.configure(api_key=api_key)

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate_wechat_article(self, data: dict, mode='note') -> dict:
        """
        Generates a persuasive listing article using Gemini.
        Supported modes:
        - 'note': Professional style, Simplified Chinese, no emojis.
        - 'xhs': Xiaohongshu style, Simplified Chinese, high emoji count, catchy titles.
        """
        if not self.api_key:
             return {
                "title": "API Key Missing",
                "content_html": f"<h3>[API Key Missing]</h3><p>Please set GEMINI_API_KEY in .env</p><pre>{json.dumps(data, indent=2)}</pre>"
            }

        if mode == 'xhs':
            style_instruction = """
            - 风格：小红书（Xiaohongshu）爆款风格。
            - 语言：简体中文。
            - 特点：标题极其吸引人（使用爆款词汇），正文大量使用Emoji，分段清晰。
            - 内容：突出房产的“氛围感”、“生活方式”、“稀缺性”。
            - 结尾：添加相关标签（Tag），如 #新加坡生活 #新加坡房产 #留学新加坡 等。
            """
        else:
            style_instruction = """
            - 风格：专业、干练、高端。
            - 语言：简体中文。
            - 特点：严禁使用任何Emoji图标（太像AI了），使用清晰的列表和段落。
            - 内容：突出房产的核心价值、地段优势、投资回报率。
            - 语气：自信、诚恳、专业顾问视角。
            """

        prompt = f"""
        你是一位顶级房地产投资顾问。请根据以下 PropertyGuru 房产提取的数据，写一篇极其诱人的房产介绍。

        {style_instruction}

        目标读者：希望在新加坡置业的高端客户或投资者。

        房产数据：
        标题: {data.get('title')}
        价格: {data.get('price')}
        地址: {data.get('address')}
        描述: {data.get('description')[:2000]}  # Truncate to avoid context window issues

        要求：
        1. 使用 HTML 格式输出（仅限正文部分，可以使用 <h1>, <h2>, <p>, <ul>, <li>, <strong>）。
        2. 结构整齐。
        3. 不要包含 <html> 或 <body> 标签，也不要包含文章标题（因为前端会单独处理）。
        4. 如果是小红书模式，标题要放在第一行。
        5. 确保内容是简体中文。
        """

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # Cleanup: Strip markdown code blocks if the AI included them
            content_html = response.text
            if content_html.startswith("```html"):
                content_html = content_html.replace("```html", "", 1)
            if "```" in content_html:
                content_html = content_html.split("```")[0]
            content_html = content_html.strip()

            return {
                "title": data.get('title', 'Generated Article'),
                "content_html": content_html
            }
        except Exception as e:
            print(f"Gemini Error: {e}")
            return {
                "title": data.get('title', 'Error'),
                "content_html": f"<p>Oops! AI Generation failed: {str(e)}</p>"
            }
