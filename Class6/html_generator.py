import markdown
import os

def read_markdown_file(filename="科普文章.md"):
    """
    读取markdown文件内容
    """
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def convert_markdown_to_html(markdown_content):
    """
    将markdown内容转换为HTML
    """
    html_content = markdown.markdown(markdown_content, extensions=['extra', 'toc'])
    return html_content

def generate_html_page(html_content, title="科普文章"):
    """
    生成完整的HTML页面
    """
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 40px;
            text-align: center;
            color: white;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .content h2 {{
            color: #2c3e50;
            margin: 30px 0 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
            font-size: 22px;
        }}
        
        .content h3 {{
            color: #34495e;
            margin: 25px 0 12px;
            font-size: 18px;
        }}
        
        .content p {{
            margin: 15px 0;
            text-align: justify;
            font-size: 16px;
            color: #555;
        }}
        
        .content ul, .content ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        .content li {{
            margin: 10px 0;
            color: #555;
        }}
        
        .content blockquote {{
            border-left: 4px solid #4facfe;
            padding: 15px 20px;
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #666;
        }}
        
        .content code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        }}
        
        .content pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        
        .content pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        
        .content img {{
            max-width: 100%;
            border-radius: 8px;
            margin: 15px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #888;
            font-size: 14px;
            border-top: 1px solid #e9ecef;
        }}
        
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .toc h3 {{
            margin-top: 0;
            color: #333;
        }}
        
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
        }}
        
        .toc a {{
            color: #4facfe;
            text-decoration: none;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p class="subtitle">科学科普系列文章</p>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>© 2024 科普文章生成器 | 基于 arXiv 论文</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template

def save_html_file(html_content, filename="科普文章.html"):
    """
    将HTML内容保存为文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML文件已保存到 {filename}")

def extract_title_from_markdown(markdown_content):
    """
    从markdown内容中提取标题
    """
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "科普文章"

if __name__ == "__main__":
    md_content = read_markdown_file()
    if md_content:
        title = extract_title_from_markdown(md_content)
        html_content = convert_markdown_to_html(md_content)
        full_html = generate_html_page(html_content, title)
        save_html_file(full_html)
    else:
        print("请先运行 pdf_parser.py 生成科普文章")