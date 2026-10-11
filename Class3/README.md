# 网页链接爬虫

一个模块化的Python网页爬虫程序，用于监控网页链接的变化并生成增量更新报告。

## 功能特点

- 从URL模板文件读取多个网页地址
- 自动提取网页中的所有链接和标题
- 增量更新：对比新旧数据，只保存有变化的链接
- 生成Markdown格式的更新报告，只显示新增链接标题
- 支持添加注释的URL模板文件

## 文件结构

```
Class3/
├── web_crawler.py       # 主程序
├── url_templates.txt    # URL模板文件（需要监控的网页列表）
├── links_data.json      # 生成的JSON数据文件
├── update_report.md     # 生成的更新报告
└── README.md            # 本说明文件
```

## 依赖安装

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 1. 配置URL模板

编辑 `url_templates.txt` 文件，每行放一个URL：

```
# 政治新闻
https://www.news.cn/politics/leaders/20260425/077507a4aeb142c39dc486cc13d8120c/c.html

# 体育新闻
https://www.news.cn/sports/20260425/7cf8fa66a7d8458685d9d3b735d63e11/c.html

# 科技新闻
https://www.news.cn/tech/20260425/63fd408ee9a048e4956d6cd65dc8ca12/c.html
```

### 2. 运行爬虫

```bash
python web_crawler.py
```

### 3. 查看结果

- `links_data.json` - 包含所有链接的JSON数据
- `update_report.md` - 新增链接标题报告

## 程序模块

| 函数 | 功能 |
|------|------|
| `fetch_webpage()` | 发送HTTP请求获取网页HTML |
| `extract_links_and_titles()` | 解析HTML提取链接和标题 |
| `load_urls_from_template()` | 从模板文件加载URL列表 |
| `load_existing_data()` | 加载已有的JSON数据 |
| `save_to_json()` | 保存数据到JSON文件 |
| `generate_markdown_report()` | 生成Markdown更新报告 |
| `crawl_and_compare()` | 主流程：爬取并对比链接变化 |

## 增量更新逻辑

- **首次运行**：提取所有链接，保存到JSON，报告中显示所有链接
- **后续运行**：对比新旧链接数据，只报告新增的链接标题

## 输出格式

### JSON数据格式 (links_data.json)

```json
[
  {
    "url": "https://example.com/article1.html",
    "title": "文章标题1",
    "crawl_time": "2026-04-25 10:30:00"
  }
]
```

### Markdown报告格式 (update_report.md)

```markdown
# 网页链接更新报告

生成时间: 2026-04-25 10:30:00

新增链接数量: 5

## 新增链接标题

1. 新文章标题1
2. 新文章标题2
...
```

## 注意事项

- 请遵守目标网站的robots.txt规则
- 爬取速度适中，避免对目标网站造成负担
- 本程序仅供学习和研究使用
