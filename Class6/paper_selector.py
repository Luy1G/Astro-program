import json
import requests
import os

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

def load_papers_from_file(filename="arxiv_papers.json"):
    """
    从JSON文件加载论文数据
    """
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

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
            {"role": "system", "content": "你是一个专业的学术论文评估助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用DeepSeek API失败: {e}")
        return None

def select_interesting_paper(papers, api_key):
    """
    调用DeepSeek API分析论文，选择最有趣的一篇
    """
    if not papers:
        print("没有论文数据可分析")
        return None
    
    # 读取提示词
    prompt_file = os.path.join("prompts", "select_paper.txt")
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = """
请分析以下论文列表，选择一篇最有趣、最有创新性的论文。
请输出论文的序号（从0开始），只输出数字，不要输出其他内容。

论文列表：
{PAPERS}
"""
    
    papers_text = "\n".join([f"{i}. {paper['title']}\n   作者: {paper['authors']}\n   摘要: {paper['abstract'][:200]}..." for i, paper in enumerate(papers)])
    prompt = prompt_template.replace("{PAPERS}", papers_text)
    
    result = call_deepseek_api(prompt, api_key)
    if result is None:
        return None
    
    try:
        selected_index = int(result.strip())
        if 0 <= selected_index < len(papers):
            return papers[selected_index]
        else:
            print("选择的序号超出范围，默认选择第一篇")
            return papers[0]
    except ValueError:
        print("API返回结果不是有效的数字，默认选择第一篇")
        return papers[0]

def download_pdf(paper, save_dir="pdfs"):
    """
    下载论文的PDF文件
    """
    if not paper.get('pdf_url'):
        print("该论文没有PDF链接")
        return None
    
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名，移除所有非法字符
    title = paper['title'][:50]
    # Windows 文件名非法字符: \ / : * ? " < > |
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        title = title.replace(char, '_')
    title = title.replace(' ', '_')
    filename = f"{title}.pdf"
    filepath = os.path.join(save_dir, filename)
    
    try:
        response = requests.get(paper['pdf_url'], stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"PDF文件已下载到 {filepath}")
        return filepath
    except Exception as e:
        print(f"下载PDF失败: {e}")
        return None

def save_selected_paper(paper, filename="selected_paper.json"):
    """
    保存选中的论文信息
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(paper, f, ensure_ascii=False, indent=2)
    print(f"选中的论文信息已保存到 {filename}")

if __name__ == "__main__":
    # 从配置文件加载API Key
    api_key = load_api_key()
    if not api_key:
        print("请在 config.env 文件中配置 DEEPSEEK_API_KEY")
        exit(1)
    
    papers = load_papers_from_file()
    if papers:
        selected_paper = select_interesting_paper(papers, api_key)
        if selected_paper:
            print(f"选中的论文: {selected_paper['title']}")
            pdf_path = download_pdf(selected_paper)
            if pdf_path:
                selected_paper['pdf_path'] = pdf_path
                save_selected_paper(selected_paper)
        else:
            print("未能选择论文")
    else:
        print("请先运行 arxiv_crawler.py 爬取论文")