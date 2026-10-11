import math

def calculate_absolute_magnitude(m, d):
    """
    计算绝对星等
    
    参数:
        m: 视星等
        d: 距离（秒差距）
        
    返回:
        绝对星等M
    """
    return m - 5 * math.log10(d / 10)

apparent_magnitude = 0.5 # 视星等
distance = 100  # 距离（秒差距）
absolute_magnitude = calculate_absolute_magnitude(apparent_magnitude, distance)
print(f"绝对星等: {absolute_magnitude}")