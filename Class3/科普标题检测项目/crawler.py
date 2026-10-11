import requests
from bs4 import BeautifulSoup


class WebCrawler:
    """爬虫模块：负责从网页抓取标题"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_webpage(self, url):
        """
        获取网页内容
        :param url: 目标网页URL
        :return: 网页HTML内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"获取网页失败: {e}")
            return None

    def extract_titles(self, html):
        """
        从网页中提取标题
        :param html: 网页HTML内容
        :return: 标题列表
        """
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        titles = []

        # 提取所有链接的标题
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            if title and len(title) > 5:
                titles.append(title)

        return titles

    def crawl_titles(self, url, min_count=10):
        """
        爬取网页标题
        :param url: 目标网页URL
        :param min_count: 最少需要的标题数量
        :return: 标题列表
        """
        print(f"[爬虫模块] 正在爬取: {url}")
        html = self.fetch_webpage(url)

        if html:
            titles = self.extract_titles(html)
            print(f"[爬虫模块] 提取到 {len(titles)} 个标题")
            return titles[:max(min_count, len(titles))]

        return []
