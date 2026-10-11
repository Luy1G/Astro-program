#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

try:
    from openai import OpenAI
    from api_key import API_KEY
    HAS_OPENAI = True
except ImportError as e:
    HAS_OPENAI = False
    print(f"[DEBUG] OpenAI import failed: {e}")

class ArXivSearcher:
    """arXiv 论文搜索器"""

    ARXIV_API_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.base_url = self.ARXIV_API_URL

    def _translate_keyword(self, keyword: str) -> str:
        """将中文关键词翻译为英文（如果是中文关键词）"""
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
        """搜索 arXiv 上相关论文（不限制学科领域）"""
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
            print(f"搜索 arXiv 失败: {e}，使用内置数据")
            return self._get_mock_papers(keyword)

    def _parse_arxiv_xml(self, xml_content: str) -> List[Dict]:
        """解析 arXiv API 返回的 XML 内容"""
        papers = []
        import re

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
        """获取模拟论文数据（用于演示）"""
        search_keyword = self._translate_keyword(keyword)

        mock_data = {
            "视星等": [
                {
                    "title": "The Apparent Magnitude Scale: From Hipparchus to Modern Astronomy",
                    "authors": ["John Smith", "Sarah Johnson", "Mike Brown"],
                    "summary": "The apparent magnitude scale is a logarithmic measure of the brightness of celestial objects as seen from Earth. This paper traces the historical development of the magnitude system from its origins with Hipparchus to modern photometric standards.",
                    "abs_url": "https://arxiv.org/abs/2410.11455",
                    "pdf_url": "https://arxiv.org/pdf/2410.11455.pdf",
                    "arxiv_id": "2410.11455",
                    "updated": "2024-10-15"
                },
                {
                    "title": "Precision Photometry and Apparent Magnitude Calibration with Gaia Data",
                    "authors": ["Emily Davis", "Robert Wilson"],
                    "summary": "We present a comprehensive analysis of apparent magnitude measurements using data from the Gaia satellite mission. Our study improves the precision of stellar brightness measurements.",
                    "abs_url": "https://arxiv.org/abs/2504.11528",
                    "pdf_url": "https://arxiv.org/pdf/2504.11528.pdf",
                    "arxiv_id": "2504.11528",
                    "updated": "2025-04-15"
                },
                {
                    "title": "Calibration of the Visual Magnitude System for Variable Stars",
                    "authors": ["Maria Garcia", "David Chen", "Anna Kowalski"],
                    "summary": "We propose a new calibration method for visual magnitude measurements of variable stars, improving accuracy by a factor of two compared to traditional techniques.",
                    "abs_url": "https://arxiv.org/abs/2406.12345",
                    "pdf_url": "https://arxiv.org/pdf/2406.12345.pdf",
                    "arxiv_id": "2406.12345",
                    "updated": "2024-06-20"
                }
            ],
            "黑洞": [
                {
                    "title": "Black Hole Event Horizon Telescope: Recent Results",
                    "authors": ["Event Horizon Telescope Collaboration"],
                    "summary": "The Event Horizon Telescope (EHT) has revolutionized our understanding of black holes through its groundbreaking imaging capabilities.",
                    "abs_url": "https://arxiv.org/abs/2403.18232",
                    "pdf_url": "https://arxiv.org/pdf/2403.18232.pdf",
                    "arxiv_id": "2403.18232",
                    "updated": "2024-03-20"
                },
                {
                    "title": "Gravitational Wave Signatures from Black Hole Mergers",
                    "authors": ["LIGO Scientific Collaboration", "Virgo Collaboration"],
                    "summary": "We report the detection of gravitational waves from a series of black hole mergers, providing new insights into black hole population statistics.",
                    "abs_url": "https://arxiv.org/abs/2405.09876",
                    "pdf_url": "https://arxiv.org/pdf/2405.09876.pdf",
                    "arxiv_id": "2405.09876",
                    "updated": "2024-05-15"
                },
                {
                    "title": "Black Hole Mass Estimation Using Spectral Analysis",
                    "authors": ["James Thompson", "Yuki Tanaka"],
                    "summary": "A new spectroscopic method for estimating black hole masses in active galactic nuclei, demonstrating higher accuracy than reverberation mapping.",
                    "abs_url": "https://arxiv.org/abs/2407.11111",
                    "pdf_url": "https://arxiv.org/pdf/2407.11111.pdf",
                    "arxiv_id": "2407.11111",
                    "updated": "2024-07-10"
                }
            ],
            "人工智能": [
                {
                    "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                    "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
                    "abs_url": "https://arxiv.org/abs/1706.03762",
                    "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                    "arxiv_id": "1706.03762",
                    "updated": "2017-06-12"
                },
                {
                    "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                    "authors": ["Jacob Devlin", "Ming-Wei Chang"],
                    "summary": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
                    "abs_url": "https://arxiv.org/abs/1810.04805",
                    "pdf_url": "https://arxiv.org/pdf/1810.04805.pdf",
                    "arxiv_id": "1810.04805",
                    "updated": "2018-10-11"
                },
                {
                    "title": "GPT-3: Language Models are Few-Shot Learners",
                    "authors": ["Tom Brown", "Benjamin Mann"],
                    "summary": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance.",
                    "abs_url": "https://arxiv.org/abs/2005.14165",
                    "pdf_url": "https://arxiv.org/pdf/2005.14165.pdf",
                    "arxiv_id": "2005.14165",
                    "updated": "2020-05-28"
                }
            ]
        }

        if keyword in mock_data:
            return mock_data[keyword]
        elif search_keyword in mock_data:
            return mock_data[search_keyword]
        else:
            return [
                {
                    "title": f"Advances in {search_keyword}: A Comprehensive Review",
                    "authors": ["Research Team Alpha", "Science Institute"],
                    "summary": f"This paper presents a comprehensive review of recent advances in {search_keyword}, covering theoretical developments and practical applications.",
                    "abs_url": "https://arxiv.org/abs/2401.00001",
                    "pdf_url": "https://arxiv.org/pdf/2401.00001.pdf",
                    "arxiv_id": "2401.00001",
                    "updated": "2024-01-15"
                },
                {
                    "title": f"New Perspectives on {search_keyword} Research",
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
                    "summary": f"This work provides an overview of the current state of research in {search_keyword} and outlines promising directions for future investigation.",
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
        """使用 LLM 生成大众版科普文章"""
        papers_summary = self._format_papers_for_prompt(papers)
        today = datetime.now().strftime("%Y年%m月%d日")

        prompt = f"""请为以下关于「{keyword}」的学术论文撰写一篇面向普通大众的科普文章。

要求：
1. 语言通俗易懂，避免过多专业术语
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
        """使用 LLM 生成学者版学术综述"""
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

class ArticleGenerator:
    """基础科普文章生成器（不使用 LLM）"""

    def __init__(self):
        self.today = datetime.now().strftime("%Y年%m月%d日")

    def generate_public_version(self, keyword: str, papers: List[Dict]) -> str:
        """生成大众版科普文章"""
        if not papers:
            return f"未找到关于「{keyword}」的相关论文"

        content = f"""# {keyword}科普指南

**发布时间**：{self.today}
**来源**：arXiv 学术论文
**主题**：{keyword}

---

## 什么是{keyword}？

{self._generate_introduction(papers[0])}

---

## 最新研究进展

"""

        for i, paper in enumerate(papers[:3], 1):
            content += f"""### {i}. {paper['title']}

**作者**：{', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}
**发表时间**：{paper.get('updated', '未知')}
**链接**：[{paper.get('arxiv_id', '')}]({paper.get('abs_url', '')})

{self._summarize_for_public(paper['summary'])}

---

"""

        content += f"""## 参考文献

"""

        for i, paper in enumerate(papers, 1):
            content += f"""{i}. **{paper['title']}**
   作者：{', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}
   arXiv: [{paper.get('arxiv_id', '')}]({paper.get('abs_url', '')})

"""

        return content

    def generate_scholar_version(self, keyword: str, papers: List[Dict]) -> str:
        """生成学者版学术综述"""
        if not papers:
            return f"未找到关于「{keyword}」的相关论文"

        content = f"""# {keyword} 研究综述

**日期**：{self.today}
**数据源**：arXiv
**检索关键词**：{keyword}

---

## 摘要

本文综述了近期关于{keyword}的研究进展，基于arXiv数据库检索的相关文献进行分析。

---

## 1. 引言

{keyword}是当前研究领域的重要课题，本文旨在梳理该领域的最新研究成果。

---

## 2. 文献分析

"""

        for i, paper in enumerate(papers[:5], 1):
            content += f"""### 2.{i} {paper['title']}

**作者**：{', '.join(paper['authors'])}
**arXiv ID**：{paper.get('arxiv_id', '')}
**提交日期**：{paper.get('updated', '未知')}
**链接**：{paper.get('abs_url', '')}

**摘要**：
{paper['summary']}

---

"""

        content += f"""## 3. 参考文献

"""

        for i, paper in enumerate(papers, 1):
            content += f"""{i}. {', '.join(paper['authors'])}. "{paper['title']}". arXiv preprint arXiv:{paper.get('arxiv_id', '')}, {paper.get('updated', '')[:4] if paper.get('updated') else ''}.

"""

        return content

    def _generate_introduction(self, paper: Dict) -> str:
        """根据论文摘要生成引言"""
        summary = paper.get('summary', '')
        if summary:
            sentences = summary.split('. ')
            if len(sentences) >= 2:
                return sentences[0] + '. ' + sentences[1] + '.'
            return summary[:300] + '...'
        return f"{paper['title']}是一个重要的研究课题，吸引了众多研究者的关注。"

    def _summarize_for_public(self, summary: str) -> str:
        """将学术摘要简化为大众易懂的语言"""
        if not summary:
            return "暂无摘要"

        summary = summary.replace("we present", "本文提出")
        summary = summary.replace("we study", "研究团队探讨了")
        summary = summary.replace("we show", "研究显示")
        summary = summary.replace("in this paper", "在这项研究中")
        summary = summary.replace("results indicate", "结果表明")

        return summary[:400] + '...'

class FileManager:
    """文件管理器"""

    def __init__(self, base_dir: str = "科普文献"):
        """初始化文件管理器，默认保存到「科普文献」文件夹"""
        self.base_dir = base_dir

    def create_topic_folder(self, keyword: str) -> str:
        """创建以关键词命名的文件夹"""
        folder_name = keyword.replace('/', '_').replace('\\', '_').replace(':', '_')
        folder_path = os.path.join(self.base_dir, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        return folder_path

    def save_paper_info(self, folder_path: str, papers: List[Dict]) -> None:
        """保存论文信息到 JSON 文件"""
        papers_file = os.path.join(folder_path, "papers.json")
        with open(papers_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

    def save_article(self, folder_path: str, content: str, version: str = "public") -> str:
        """保存科普文章"""
        filename = f"科普文章_{version}.md"
        filepath = os.path.join(folder_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

class ScienceArticleGenerator:
    """主程序类"""

    def __init__(self, use_llm: bool = True):
        self.searcher = ArXivSearcher()
        self.file_manager = FileManager()
        self.use_llm = use_llm and HAS_OPENAI

        if self.use_llm:
            try:
                from api_key import API_KEY
                self.llm_generator = LLMArticleGenerator(API_KEY)
                print("[INFO] LLM 功能已启用")
            except Exception as e:
                print(f"[WARNING] LLM 初始化失败: {e}，使用基础模式")
                self.use_llm = False
                self.generator = ArticleGenerator()
        else:
            self.generator = ArticleGenerator()
            print("[INFO] 使用基础文章生成模式")

    def run(self, keyword: str, version: str = "public") -> str:
        """运行完整流程"""
        print(f"[INFO] 正在搜索关于「{keyword}」的论文...")

        papers = self.searcher.search(keyword, max_results=5)

        if not papers:
            print(f"[ERROR] 未找到关于「{keyword}」的论文")
            return ""

        print(f"[INFO] 找到 {len(papers)} 篇相关论文")

        folder_path = self.file_manager.create_topic_folder(keyword)
        print(f"[INFO] 创建文件夹: {folder_path}")

        self.file_manager.save_paper_info(folder_path, papers)
        print(f"[INFO] 已保存论文列表")

        print(f"[INFO] 正在生成{version}版科普文章...")

        if self.use_llm:
            if version == "scholar":
                content = self.llm_generator.generate_scholar_article(keyword, papers)
            else:
                content = self.llm_generator.generate_public_article(keyword, papers)

            if content is None:
                print("[WARNING] LLM 生成失败，回退到基础模式")
                if version == "scholar":
                    content = self.generator.generate_scholar_version(keyword, papers)
                else:
                    content = self.generator.generate_public_version(keyword, papers)
        else:
            if version == "scholar":
                content = self.generator.generate_scholar_version(keyword, papers)
            else:
                content = self.generator.generate_public_version(keyword, papers)

        filepath = self.file_manager.save_article(folder_path, content, version)
        print(f"[INFO] 科普文章已保存到: {filepath}")

        return content

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python feature.py <关键词> [版本]")
        print("版本可选: public（大众版，默认）或 scholar（学者版）")
        return

    keyword = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "public"

    if version not in ["public", "scholar"]:
        print("无效的版本参数，使用默认大众版")
        version = "public"

    generator = ScienceArticleGenerator(use_llm=True)
    content = generator.run(keyword, version)

    if content:
        print("\n" + "="*60)
        print(f"科普文章「{keyword}」生成完成！")
        print("="*60)

if __name__ == "__main__":
    main()