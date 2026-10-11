from crawler import WebCrawler
from title_analyzer import TitleAnalyzer
from datetime import datetime


def save_results_to_file(results, statistics, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("科普网站标题爬取与标题党检测报告\n")
        f.write("=" * 70 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"目标网站: https://www.guokr.com/\n")
        f.write("=" * 70 + "\n\n")

        f.write("【统计摘要】\n")
        f.write("-" * 70 + "\n")
        f.write(f"总标题数: {statistics['total']}\n")
        f.write(f"正常标题: {statistics['normal']}\n")
        f.write(f"疑似标题党: {statistics['clickbait']}\n")
        f.write(f"标题党比例: {statistics['clickbait_rate']}%\n")
        f.write("-" * 70 + "\n\n")

        f.write("【详细检测结果】\n")
        f.write("-" * 70 + "\n")

        for i, result in enumerate(results, 1):
            status = "疑似标题党" if result['is_clickbait'] else "正常"
            f.write(f"\n{i}. [{status}] {result['title']}\n")
            if result['is_clickbait'] and result['reasons']:
                f.write(f"   触发关键词: {', '.join(result['reasons'])}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("报告结束\n")
        f.write("=" * 70 + "\n")

    print(f"结果已保存到: {output_file}")


def main():
    print("=" * 70)
    print("科普网站标题爬取与标题党检测系统")
    print("目标网站: https://www.guokr.com/")
    print("=" * 70)

    print("\n>>> 阶段一：爬虫模块工作 <<<\n")
    crawler = WebCrawler()
    url = "https://www.guokr.com/"
    titles = crawler.crawl_titles(url, min_count=10)

    if not titles:
        print("错误：未能获取到任何标题")
        return

    print(f"\n成功获取 {len(titles)} 个标题")

    print("\n>>> 阶段二：分析模块工作 <<<\n")
    analyzer = TitleAnalyzer()
    results = analyzer.analyze_titles(titles)
    statistics = analyzer.get_statistics()

    print("\n" + "=" * 70)
    print("【统计摘要】")
    print("=" * 70)
    print(f"总标题数: {statistics['total']}")
    print(f"正常标题: {statistics['normal']}")
    print(f"疑似标题党: {statistics['clickbait']}")
    print(f"标题党比例: {statistics['clickbait_rate']}%")
    print("=" * 70)

    print("\n【详细检测结果】")
    print("=" * 70)

    for i, result in enumerate(results, 1):
        status = "疑似标题党" if result['is_clickbait'] else "正常"
        print(f"\n{i}. [{status}] {result['title']}")
        if result['is_clickbait'] and result['reasons']:
            print(f"   触发关键词: {', '.join(result['reasons'])}")

    print("=" * 70)

    output_file = "guokr_title_detection_report.txt"
    save_results_to_file(results, statistics, output_file)

    print("\n程序执行完毕！")


if __name__ == "__main__":
    main()
