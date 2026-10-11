import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime


def fetch_webpage(url):
    """
    获取网页内容
    :param url: 目标网页URL
    :return: 网页HTML内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"获取网页失败: {e}")
        return None


def extract_links_and_titles(html):
    """
    从网页中提取所有链接和标题
    :param html: 网页HTML内容
    :return: 链接列表[(url, title), ...]
    """
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen_urls = set()
    
    for a in soup.find_all('a', href=True):
        url = a['href']
        title = a.get_text(strip=True)
        
        if url and url.startswith('http') and url not in seen_urls:
            seen_urls.add(url)
            results.append({
                'url': url,
                'title': title if title else '无标题'
            })
    
    return results


def load_urls_from_template(template_file):
    """
    从模板文件加载URL列表
    :param template_file: URL模板文件路径
    :return: URL列表
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, template_file)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls


def load_existing_data(json_file):
    """
    加载已有的JSON数据
    :param json_file: JSON文件路径
    :return: 已有的链接数据字典 {url: {title, timestamp}}
    """
    if not os.path.exists(json_file):
        return {}
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {item['url']: item for item in data}


def save_to_json(data, json_file):
    """
    保存数据到JSON文件
    :param data: 链接数据列表
    :param json_file: JSON文件路径
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_file)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_markdown_report(new_links, report_file):
    """
    生成Markdown更新报告
    :param new_links: 新增的链接列表
    :param report_file: 报告文件路径
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, report_file)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("# 网页链接更新报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"新增链接数量: {len(new_links)}\n\n")
        f.write("## 新增链接标题\n\n")
        
        if new_links:
            for i, link in enumerate(new_links, 1):
                f.write(f"{i}. {link['title']}\n")
        else:
            f.write("无新增链接。\n")


def crawl_and_compare():
    """
    爬取网页并对比链接变化
    """
    print("=" * 60)
    print("网页链接爬虫 - 增量更新版")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'links_data.json')
    report_file = os.path.join(script_dir, 'update_report.md')
    template_file = 'url_templates.txt'
    
    # 加载URL列表
    urls = load_urls_from_template(template_file)
    print(f"\n从模板文件加载了 {len(urls)} 个URL")
    
    # 加载已有数据
    existing_data = load_existing_data(json_file)
    print(f"已有数据: {len(existing_data)} 条链接")
    
    all_links = {}
    new_links = []
    
    # 爬取每个URL
    for url in urls:
        print(f"\n正在爬取: {url}")
        html = fetch_webpage(url)
        
        if html:
            print(f"正在提取链接...")
            links = extract_links_and_titles(html)
            print(f"提取到 {len(links)} 个链接")
            
            for link in links:
                all_links[link['url']] = {
                    'title': link['title'],
                    'url': link['url'],
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 检查是否为新链接
                if link['url'] not in existing_data:
                    new_links.append(link)
    
    # 转换为列表并排序
    all_links_list = sorted(all_links.values(), key=lambda x: x['url'])
    
    # 保存JSON
    save_to_json(all_links_list, json_file)
    print(f"\n已保存 {len(all_links_list)} 条链接到: {json_file}")
    
    # 生成报告
    generate_markdown_report(new_links, report_file)
    print(f"更新报告已保存到: {report_file}")
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("执行摘要")
    print("=" * 60)
    print(f"总链接数: {len(all_links_list)}")
    print(f"新增链接: {len(new_links)}")
    print(f"删除链接: {len(existing_data) - len(all_links_list) + len(new_links) if existing_data else 0}")
    
    if new_links:
        print("\n新增链接标题:")
        for i, link in enumerate(new_links[:10], 1):
            print(f"  {i}. {link['title']}")
        if len(new_links) > 10:
            print(f"  ... 还有 {len(new_links) - 10} 条")


def main():
    crawl_and_compare()


if __name__ == "__main__":
    main()
