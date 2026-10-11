# ArXiv 论文科普文章生成器

一个从 arXiv 网站爬取最新论文，利用 DeepSeek API 生成面向大众的科普文章的 Python 工具。

## 功能特点

- 自动爬取 arXiv 最新论文
- 智能选择最有趣、最具科普价值的论文
- 自动下载论文 PDF
- 利用大模型将学术论文转化为通俗易懂的科普文章
- 生成美观的 HTML 页面

## 项目结构

```
Class6/
├── arxiv_crawler.py      # 爬取 arXiv 论文
├── paper_selector.py     # 选择论文并下载 PDF
├── pdf_parser.py         # 解析 PDF 生成科普文章
├── html_generator.py     # 生成 HTML 文件
├── run_all.py            # 一键运行脚本
├── config.env            # API Key 配置文件
├── requirements.txt      # 依赖列表
├── prompts/
│   ├── select_paper.txt       # 选择论文提示词
│   └── generate_article.txt   # 生成文章提示词
├── pdfs/                  # PDF 文件存储目录（自动生成）
├── arxiv_papers.json      # 爬取的论文数据
├── selected_paper.json    # 选中的论文信息
├── 科普文章.md            # 生成的科普文章
└── 科普文章.html          # 最终的 HTML 页面
```

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包：
- requests - HTTP 请求
- beautifulsoup4 - HTML 解析
- PyPDF2 - PDF 文本提取
- markdown - Markdown 转 HTML

## 配置

在 `config.env` 文件中配置你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=your_api_key_here
```

获取 API Key：访问 [DeepSeek 平台](https://platform.deepseek.com/) 注册并获取。

## 使用方法

### 方式一：一键运行

```bash
python run_all.py
```

### 方式二：分步运行

```bash
# 步骤 1: 爬取 arXiv 论文
python arxiv_crawler.py

# 步骤 2: 选择论文并下载 PDF
python paper_selector.py

# 步骤 3: 解析 PDF 生成科普文章
python pdf_parser.py

# 步骤 4: 生成 HTML 文件
python html_generator.py
```

## 自定义配置

### 修改爬取类别

在 `arxiv_crawler.py` 中修改 `category` 参数：

```python
papers = crawl_arxiv(category="cs.AI", max_results=15)
```

常用类别：
- `cs.AI` - 人工智能
- `cs.CL` - 计算与语言
- `cs.CV` - 计算机视觉
- `cs.LG` - 机器学习
- `physics` - 物理学
- `math` - 数学

### 修改提示词

提示词存放在 `prompts/` 目录下，可根据需要自行修改：
- `select_paper.txt` - 论文选择提示词
- `generate_article.txt` - 文章生成提示词

## 输出示例

运行完成后会生成：
1. `科普文章.md` - Markdown 格式的科普文章
2. `科普文章.html` - 带有美观样式的 HTML 页面

## 注意事项

1. 请确保网络可以访问 arXiv.org
2. DeepSeek API 需要付费使用，请注意用量
3. PDF 解析可能因论文格式不同而有差异
4. 生成的科普文章仅供参考，建议人工审核

## 许可证

MIT License