# 科普文章自动生成器

基于 arXiv 论文和 DeepSeek AI 的科普文章自动生成工具。

## 功能特点

- 自动从 arXiv 检索学术论文
- 支持中文关键词搜索（自动翻译为英文）
- 使用 DeepSeek AI 生成高质量科普文章
- 支持两种版本：
  - **大众版 (public)**：通俗易懂，适合普通读者
  - **学者版 (scholar)**：学术综述，适合专业研究人员
- 自动创建文件夹，保存论文信息和生成的文章
- 每篇文章包含 3 篇参考文献

## 安装依赖

```bash
pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用方法

### 基本用法

```bash
python feature.py <关键词> [版本]
```

### 参数说明

- `关键词`：要搜索的主题（支持中文）
- `版本`：可选，`public`（大众版，默认）或 `scholar`（学者版）

### 使用示例

```bash
# 生成大众版科普文章
python feature.py 黑洞 public
python feature.py 人工智能 public

# 生成学者版学术综述
python feature.py 黑洞 scholar
python feature.py 基因编辑 scholar
```

## 支持的中文关键词

| 中文关键词 | 英文翻译 |
|-----------|---------|
| 视星等 | apparent magnitude |
| 黑洞 | black hole |
| 引力波 | gravitational wave |
| 量子计算 | quantum computing |
| 人工智能 | artificial intelligence |
| 机器学习 | machine learning |
| 深度学习 | deep learning |
| 气候变化 | climate change |
| 基因编辑 | gene editing |
| 区块链 | blockchain |
| 物联网 | Internet of Things |
| ... | ... |

> 也支持直接使用英文关键词

## 文件结构

```
Class4/
├── feature.py          # 主程序
├── api_key.py          # DeepSeek API 密钥配置
├── README.md           # 说明文档
└── 科普文献/           # 生成的科普文章存放目录
    ├── 黑洞/
    │   ├── papers.json           # 论文信息
    │   ├── 科普文章_public.md     # 大众版
    │   └── 科普文章_scholar.md    # 学者版
    ├── 人工智能/
    │   ├── papers.json
    │   └── 科普文章_public.md
    └── ...
```

## 输出内容

每篇科普文章包含：

1. **发布时间**
2. **来源**：arXiv 学术论文
3. **主题介绍**：通俗易懂的概念解释
4. **核心内容**：基于论文的研究进展
5. **参考文献**：3 篇相关论文

## API 配置

在 `api_key.py` 中配置你的 DeepSeek API 密钥：

```python
API_KEY = "your-deepseek-api-key"
```

## 注意事项

1. 需要网络连接访问 arXiv API 和 DeepSeek API
2. 如果 LLM 调用失败，会自动回退到基础模板模式
3. 生成的文章仅供参考，请以原始论文为准

## 技术栈

- Python 3.8+
- arXiv API：论文检索
- DeepSeek API：文章生成
- OpenAI SDK：API 调用

## 作者

自动生成科普文章系统

## 更新日志

- 2026-05-23：初始版本发布
  - 支持 arXiv 论文检索
  - 集成 DeepSeek AI 生成
  - 支持大众版和学者版
  - 自动整理到「科普文献」文件夹
