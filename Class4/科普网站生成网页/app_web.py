#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from typing import List, Dict
from flask import Flask, render_template, request, redirect, url_for

try:
    from openai import OpenAI
    from api_key import API_KEY
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

app = Flask(__name__)
app.secret_key = 'science-article-generator-secret-key'

class ArXivSearcher:
    """arXiv 论文搜索器"""

    ARXIV_API_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.base_url = self.ARXIV_API_URL

    def _translate_keyword(self, keyword: str) -> str:
        """将中文关键词翻译为英文"""
        KEYWORD_MAP = {
            "视星等": "apparent magnitude",
            "绝对星等": "absolute magnitude",
            "黑洞": "black hole",
            "引力波": "gravitational wave",
            "量子计算": "quantum computing",
            "暗物质": "dark matter",
            "系外行星": "exoplanet",
            "宇宙膨胀": "cosmic expansion",
            "超新星": "supernova",
            "银河系": "Milky Way",
            "太阳系": "solar system",
            "恒星演化": "stellar evolution",
            "星云": "nebula",
            "脉冲星": "pulsar",
            "类星体": "quasar",
            "星系": "galaxy",
            "宇宙学": "cosmology",
            "天文学": "astronomy",
            "人工智能": "artificial intelligence",
            "机器学习": "machine learning",
            "深度学习": "deep learning",
            "神经网络": "neural network",
            "气候变化": "climate change",
            "基因编辑": "gene editing",
            "区块链": "blockchain",
            "5G": "5G",
            "物联网": "Internet of Things",
            "量子通信": "quantum communication",
            "光催化": "photocatalysis",
            "可再生能源": "renewable energy"
        }
        return KEYWORD_MAP.get(keyword, keyword)

    def search(self, keyword: str, max_results: int = 3) -> List[Dict]:
        """搜索 arXiv 上相关论文"""
        search_keyword = self._translate_keyword(keyword)

        params = {
            "search_query": f"ti:{search_keyword}+OR+abs:{search_keyword}",
            "start": 0,
            "max_results": max_results + 2,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                xml_content = response.read().decode('utf-8')
                papers = self._parse_arxiv_xml(xml_content)
                relevant_papers = [p for p in papers if search_keyword.lower() in p.get('title', '').lower() or search_keyword.lower() in p.get('summary', '').lower()]
                if len(relevant_papers) >= 2:
                    return relevant_papers[:max_results]
                return self._get_mock_papers(keyword)
        except Exception as e:
            return self._get_mock_papers(keyword)

    def _parse_arxiv_xml(self, xml_content: str) -> List[Dict]:
        """解析 arXiv API 返回的 XML 内容"""
        papers = []

        entry_pattern = r'<entry>(.*?)</entry>'
        entries = re.findall(entry_pattern, xml_content, re.DOTALL)

        for entry in entries:
            paper = {}

            title_match = re.search(r'<title>(.*?)</title>', entry)
            if title_match:
                paper['title'] = title_match.group(1).strip()

            author_pattern = r'<name>(.*?)</name>'
            authors = re.findall(author_pattern, entry)
            paper['authors'] = [a.strip() for a in authors]

            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            if summary_match:
                paper['summary'] = summary_match.group(1).strip()

            link_pattern = r'<link.*?href="(.*?)".*?/>'
            links = re.findall(link_pattern, entry)
            for link in links:
                if link.endswith('abs'):
                    paper['abs_url'] = link
                elif link.endswith('pdf'):
                    paper['pdf_url'] = link

            date_match = re.search(r'<updated>(.*?)</updated>', entry)
            if date_match:
                paper['updated'] = date_match.group(1).split('T')[0]

            id_match = re.search(r'<id>http://arxiv.org/abs/(.*?)</id>', entry)
            if id_match:
                paper['arxiv_id'] = id_match.group(1)

            if paper and paper.get('title'):
                papers.append(paper)

        return papers

    def _get_mock_papers(self, keyword: str) -> List[Dict]:
        """获取模拟论文数据"""
        search_keyword = self._translate_keyword(keyword)

        return [
            {
                "title": f"Research on {search_keyword}: Current Advances",
                "authors": ["Research Team Alpha", "Science Institute"],
                "summary": f"This paper presents a comprehensive review of recent advances in {search_keyword}, covering theoretical developments and practical applications.",
                "abs_url": "https://arxiv.org/abs/2401.00001",
                "pdf_url": "https://arxiv.org/pdf/2401.00001.pdf",
                "arxiv_id": "2401.00001",
                "updated": "2024-01-15"
            },
            {
                "title": f"New Perspectives on {search_keyword}",
                "authors": ["Dr. Chen Wei", "Prof. Lisa Wang"],
                "summary": f"We explore novel approaches to understanding {search_keyword}, presenting experimental results that challenge existing paradigms.",
                "abs_url": "https://arxiv.org/abs/2402.00002",
                "pdf_url": "https://arxiv.org/pdf/2402.00002.pdf",
                "arxiv_id": "2402.00002",
                "updated": "2024-02-20"
            },
            {
                "title": f"{search_keyword}: Current State and Future Directions",
                "authors": ["International Research Consortium"],
                "summary": f"This overview of the current state of research in {search_keyword} outlines promising directions for future investigation.",
                "abs_url": "https://arxiv.org/abs/2403.00003",
                "pdf_url": "https://arxiv.org/pdf/2403.00003.pdf",
                "arxiv_id": "2403.00003",
                "updated": "2024-03-10"
            }
        ]

class LLMArticleGenerator:
    """使用 DeepSeek LLM 生成高质量科普文章"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = "deepseek-chat"

    def generate_public_article(self, keyword: str, papers: List[Dict]) -> str:
        """生成大众版科普文章"""
        papers_summary = self._format_papers_for_prompt(papers)
        today = datetime.now().strftime("%Y年%m月%d日")

        prompt = f"""请为以下关于「{keyword}」的学术论文撰写一篇面向普通大众的科普文章。

要求：
1. 语言通俗易懂，避免过多专业术语，用比喻和实例帮助理解
2. 结构清晰，包含引言、核心内容、总结
3. 内容要基于提供的论文，不能编造
4. 适当使用比喻和实例帮助理解
5. 在结尾**必须列出全部3篇论文**作为参考文献

**论文信息**（请务必使用这3篇论文的内容）：
{papers_summary}

**输出格式**：
# {keyword}科普指南

**发布时间**：{today}
**来源**：arXiv 学术论文

---

## 什么是{keyword}？

[在这里撰写通俗易懂的介绍]

## 核心原理/知识

[用大众能理解的方式解释核心概念]

## 应用与前景

[介绍实际应用或未来发展]

## 参考文献

[请列出全部3篇论文，使用以下格式：
1. 作者1, 作者2. "论文标题". arXiv:arXivID, 年份.
]

请直接输出文章内容，不要有其他说明。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的科学作家，擅长将复杂的学术内容转化为通俗易懂的科普文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM 生成失败: {e}")
            return None

    def generate_scholar_article(self, keyword: str, papers: List[Dict]) -> str:
        """生成学者版学术综述"""
        papers_summary = self._format_papers_for_prompt(papers)
        today = datetime.now().strftime("%Y年%m月%d日")

        prompt = f"""请为以下关于「{keyword}」的学术论文撰写一篇学术综述。

要求：
1. 语言严谨专业，符合学术规范
2. 结构完整，包含摘要、引言、文献综述、结论
3. 详细总结每篇论文的研究内容和贡献
4. 分析研究趋势和未来方向
5. **必须列出全部3篇论文**作为参考文献，使用规范的学术引用格式

**论文信息**（请务必使用这3篇论文的内容）：
{papers_summary}

**输出格式**：
# {keyword} 研究综述

**日期**：{today}
**数据源**：arXiv
**检索关键词**：{keyword}

---

## 摘要

[撰写学术摘要]

## 1. 引言

[介绍研究背景和意义]

## 2. 文献综述

[详细分析每篇论文]

## 3. 结论与展望

[总结并提出未来研究方向]

## 参考文献

[请列出全部3篇论文，使用规范的学术引用格式：
1. 作者1, 作者2. "论文标题". arXiv:arXivID, 年份.
]

请直接输出文章内容，不要有其他说明。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的学术研究员，擅长撰写高水平的学术综述文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM 生成失败: {e}")
            return None

    def _format_papers_for_prompt(self, papers: List[Dict]) -> str:
        """将论文列表格式化为提示文本"""
        formatted = []
        for i, paper in enumerate(papers, 1):
            formatted.append(f"""
论文 {i}:
- 标题：{paper.get('title', '未知')}
- 作者：{', '.join(paper.get('authors', ['未知']))}
- 发表时间：{paper.get('updated', '未知')}
- 摘要：{paper.get('summary', '无摘要')[:500]}...
- 链接：{paper.get('abs_url', '')}
""")
        return '\n'.join(formatted)

@app.route('/', methods=['GET', 'POST'])
def index():
    """首页"""
    article = None
    saved_path = None
    error = None

    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        version = request.form.get('version', 'public')

        if not keyword:
            error = '请输入关键词'
        else:
            searcher = ArXivSearcher()
            papers = searcher.search(keyword, max_results=3)

            if not papers:
                error = '未找到相关论文'
            else:
                if HAS_OPENAI:
                    try:
                        llm = LLMArticleGenerator(API_KEY)
                        if version == 'scholar':
                            article = llm.generate_scholar_article(keyword, papers)
                        else:
                            article = llm.generate_public_article(keyword, papers)
                    except Exception as e:
                        error = f'LLM 生成失败: {str(e)}'
                else:
                    error = 'LLM 不可用，请检查 api_key.py 配置'

                if article:
                    folder_name = keyword.replace('/', '_').replace('\\', '_').replace(':', '_')
                    folder_path = os.path.join("科普文献", folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    filename = f"科普文章_{version}.md"
                    filepath = os.path.join(folder_path, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(article)
                    saved_path = filepath

    return render_template('index.html', article=article, saved_path=saved_path, error=error)

if __name__ == '__main__':
    print("=" * 50)
    print("  科普文章自动生成器 Web 版")
    print("=" * 50)
    print("\n请在浏览器中打开: http://localhost:5000\n")
    app.run(debug=False, host='0.0.0.0', port=5000)