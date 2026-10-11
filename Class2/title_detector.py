import os

def load_titles(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


CLICKBAIT_PATTERNS = [
    '震惊', '太可怕', '必看', '太甜', '涨知识',
    '太震惊', '别再被骗', '99%', '不可思议', '真相大白',
    '紧急', '惊人', '致命', '恐怖', '炸裂',
    '爆哭', '绝了', '太准了', '神了',
    '懵了', '哭了', '笑喷', '泪目', '破防',
    '上热搜', '全网', '全网首发', '刷爆', '彻底', '沸腾'
]


def is_clickbait(title):
    for pattern in CLICKBAIT_PATTERNS:
        if pattern in title:
            return True
    return False


def classify_title(title):
    if is_clickbait(title):
        return "震惊体/标题党"
    else:
        return "正常标题"


def analyze_titles(titles):
    results = []
    for title in titles:
        category = classify_title(title)
        results.append((title, category))
    return results


def print_results(results):
    print("=" * 60)
    print("标题检测结果")
    print("=" * 60)
    for i, (title, category) in enumerate(results, 1):
        print(f"{i}. [{category}] {title}")
    print("=" * 60)
    print(f"总计: {len(results)} 条标题")
    clickbait_count = sum(1 for _, c in results if c == "震惊体/标题党")
    normal_count = len(results) - clickbait_count
    print(f"正常标题: {normal_count} 条 | 震惊体/标题党: {clickbait_count} 条")


def main():
    file_path = "titles.txt"
    titles = load_titles(file_path)
    results = analyze_titles(titles)
    print_results(results)


if __name__ == "__main__":
    main()
