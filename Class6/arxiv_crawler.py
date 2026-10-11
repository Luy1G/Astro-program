import requests
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def crawl_arxiv(category="cs.AI", max_results=10):
    """
    从arxiv.org API爬取指定类别的最新论文
    :param category: 论文类别，默认为cs.AI（人工智能）
    :param max_results: 最大爬取数量
    :return: 论文列表
    """
    # 使用 arXiv API
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    url = base_url + query
    
    try:
        print(f"正在请求 arXiv API: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析 XML 响应
        root = ET.fromstring(response.content)
        
        # 定义命名空间
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        papers = []
        entries = root.findall('atom:entry', namespaces)
        
        print(f"找到 {len(entries)} 篇论文")
        
        for entry in entries:
            paper = {}
            
            # 标题
            title_elem = entry.find('atom:title', namespaces)
            paper['title'] = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else ""
            
            # 作者
            authors = entry.findall('atom:author', namespaces)
            author_names = []
            for author in authors:
                name_elem = author.find('atom:name', namespaces)
                if name_elem is not None:
                    author_names.append(name_elem.text)
            paper['authors'] = ', '.join(author_names)
            
            # 摘要
            summary_elem = entry.find('atom:summary', namespaces)
            paper['abstract'] = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
            
            # PDF 链接
            pdf_url = ""
            for link in entry.findall('atom:link', namespaces):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            paper['pdf_url'] = pdf_url
            
            # arXiv ID
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is not None:
                paper['arxiv_id'] = id_elem.text.split('/')[-1]
            
            paper['category'] = category
            paper['crawl_time'] = datetime.now().isoformat()
            
            papers.append(paper)
        
        return papers
    
    except Exception as e:
        print(f"爬取arxiv失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_papers_to_file(papers, filename="arxiv_papers.json"):
    """
    将爬取的论文数据保存到JSON文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"论文数据已保存到 {filename}")

if __name__ == "__main__":
    papers = crawl_arxiv(category="cs.AI", max_results=15)
    if papers:
        save_papers_to_file(papers)
        print(f"成功爬取 {len(papers)} 篇论文")
    else:
        print("未爬取到任何论文")