class TitleAnalyzer:
    """分析模块：负责检测标题是否为标题党"""

    CLICKBAIT_PATTERNS = [
        '震惊', '太可怕', '必看', '太甜', '涨知识',
        '太震惊', '别再被骗', '99%', '不可思议', '真相大白',
        '紧急', '惊人', '致命', '恐怖', '炸裂',
        '爆哭', '绝了', '太准了', '神了',
        '懵了', '哭了', '笑喷', '泪目', '破防',
        '上热搜', '全网', '全网首发', '刷爆', '彻底', '沸腾'
    ]

    def __init__(self):
        self.total_count = 0
        self.clickbait_count = 0

    def is_clickbait(self, title):
        """
        检测标题是否为标题党
        :param title: 标题文本
        :return: True表示疑似标题党，False表示正常
        """
        for pattern in self.CLICKBAIT_PATTERNS:
            if pattern in title:
                return True
        return False

    def get_clickbait_reasons(self, title):
        """
        获取标题被判定为标题党的原因
        :param title: 标题文本
        :return: 匹配的关键词列表
        """
        reasons = []
        for pattern in self.CLICKBAIT_PATTERNS:
            if pattern in title:
                reasons.append(pattern)
        return reasons

    def analyze_title(self, title):
        """
        分析单个标题
        :param title: 标题文本
        :return: 分析结果字典
        """
        self.total_count += 1
        is_clickbait = self.is_clickbait(title)
        reasons = self.get_clickbait_reasons(title) if is_clickbait else []

        if is_clickbait:
            self.clickbait_count += 1

        return {
            'title': title,
            'is_clickbait': is_clickbait,
            'reasons': reasons
        }

    def analyze_titles(self, titles):
        """
        批量分析标题
        :param titles: 标题列表
        :return: 分析结果列表
        """
        print(f"[分析模块] 收到 {len(titles)} 个标题，开始分析...")
        results = []
        for title in titles:
            result = self.analyze_title(title)
            results.append(result)
        return results

    def get_statistics(self):
        """
        获取统计信息
        :return: 统计字典
        """
        normal_count = self.total_count - self.clickbait_count
        clickbait_rate = (self.clickbait_count / self.total_count * 100) if self.total_count > 0 else 0

        return {
            'total': self.total_count,
            'normal': normal_count,
            'clickbait': self.clickbait_count,
            'clickbait_rate': round(clickbait_rate, 2)
        }
