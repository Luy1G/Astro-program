import json
import requests
import os
import PyPDF2

def load_api_key(config_file="config.env"):
    """
    从配置文件加载API Key
    """
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('DEEPSEEK_API_KEY='):
                return line.strip().split('=', 1)[1]
    return None

def load_selected_paper(filename="selected_paper.json"):
    """
    从JSON文件加载选中的论文信息
    """
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_text_from_pdf(pdf_path):
    """
    从PDF文件提取文本内容
    """
    if not os.path.exists(pdf_path):
        print(f"PDF文件 {pdf_path} 不存在")
        return ""
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"解析PDF失败: {e}")
        return ""

def call_deepseek_api(prompt, api_key):
    """
    调用DeepSeek API
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个优秀的科普作家，擅长将复杂的学术论文转化为通俗易懂的科普文章。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用DeepSeek API失败: {e}")
        return None

def generate_popular_article(paper, pdf_text, api_key):
    """
    调用DeepSeek API生成科普文章
    """
    # 读取提示词
    prompt_file = os.path.join("prompts", "generate_article.txt")
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = """
请将以下学术论文转化为一篇面向大众的科普文章。

要求：
1. 语言通俗易懂，避免专业术语过多，必要时进行解释
2. 结构清晰，包括引言、核心内容、意义/影响等部分
3. 保持趣味性，让非专业读者也能理解
4. 使用markdown格式输出
5. 文章长度约1000-2000字

论文信息：
标题：{TITLE}
作者：{AUTHORS}
摘要：{ABSTRACT}

论文内容（部分）：
{PAPER_TEXT}

请输出科普文章：
"""
    
    # 限制论文文本长度
    truncated_text = pdf_text[:8000] if len(pdf_text) > 8000 else pdf_text
    
    prompt = prompt_template.format(
        TITLE=paper['title'],
        AUTHORS=paper['authors'],
        ABSTRACT=paper.get('abstract', ''),
        PAPER_TEXT=truncated_text
    )
    
    return call_deepseek_api(prompt, api_key)

def save_markdown(content, filename="科普文章.md"):
    """
    将科普文章保存为markdown文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"科普文章已保存到 {filename}")

if __name__ == "__main__":
    # 从配置文件加载API Key
    api_key = load_api_key()
    if not api_key:
        print("请在 config.env 文件中配置 DEEPSEEK_API_KEY")
        exit(1)
    
    print("API Key 已加载")
    
    paper = load_selected_paper()
    print(f"论文信息: {paper['title'] if paper else 'None'}")
    
    if paper and paper.get('pdf_path'):
        print(f"PDF路径: {paper['pdf_path']}")
        pdf_text = extract_text_from_pdf(paper['pdf_path'])
        print(f"提取文本长度: {len(pdf_text)} 字符")
        if pdf_text:
            print("正在调用 DeepSeek API 生成科普文章...")
            article = generate_popular_article(paper, pdf_text, api_key)
            if article:
                save_markdown(article)
            else:
                print("未能生成科普文章")
        else:
            print("未能从PDF提取文本")
    else:
        print("请先运行 paper_selector.py 选择并下载论文")