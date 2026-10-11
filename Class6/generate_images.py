import os
from PIL import Image, ImageDraw

# 创建图片目录
os.makedirs('images', exist_ok=True)

# 绘制圆角矩形
def draw_rounded_rect(draw, x1, y1, x2, y2, radius, fill=None, outline=None, width=1):
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill, outline=outline, width=width)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y1, x1+2*radius, y1+2*radius], fill=fill, outline=outline, width=width)
    draw.ellipse([x2-2*radius, y1, x2, y1+2*radius], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y2-2*radius, x1+2*radius, y2], fill=fill, outline=outline, width=width)
    draw.ellipse([x2-2*radius, y2-2*radius, x2, y2], fill=fill, outline=outline, width=width)

# 生成第一张图：AI与人类协作写作
def create_collaboration_image():
    img = Image.new('RGB', (800, 300), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # 机器人手臂
    draw_rounded_rect(draw, 50, 80, 80, 200, 5, fill='#4facfe')
    draw_rounded_rect(draw, 80, 60, 140, 100, 5, fill='#4facfe')
    draw.ellipse([102, 72, 118, 88], fill='white')
    
    # 人类手臂
    draw.ellipse([715, 90, 785, 110], fill='#ffcdb2')
    draw.ellipse([690, 120, 750, 140], fill='#ffcdb2')
    draw.ellipse([700, 135, 760, 155], fill='#ffcdb2')
    
    # 键盘
    draw_rounded_rect(draw, 300, 180, 500, 220, 10, fill='#2d2d2d')
    draw.rectangle([310, 190, 490, 210], fill='#3d3d3d')
    for i in range(6):
        draw.ellipse([325 + i*30, 192, 333 + i*30, 200], fill='white')
    
    # 连接线
    draw.line([110, 80, 350, 180], fill='#4facfe', width=2)
    draw.line([730, 145, 450, 180], fill='#ff6b6b', width=2)
    
    # 标题
    draw.text((400, 50), 'AI与人类协作写作', fill='#333', anchor='mm')
    
    img.save('images/collaboration.png')
    print("已生成: images/collaboration.png")

# 生成第二张图：流程图
def create_flowchart_image():
    img = Image.new('RGB', (800, 250), color='white')
    draw = ImageDraw.Draw(img)
    
    # 背景框
    draw_rounded_rect(draw, 50, 80, 750, 140, 30, fill='#f8f9fa')
    
    # 起始点
    draw.ellipse([70, 100, 90, 120], fill='#4facfe')
    draw.text((80, 108), '人类', fill='white', anchor='mm')
    
    # 箭头和步骤
    steps = ['打磨', '改写', '风格', '压缩', '扩写']
    x = 140
    for step in steps:
        draw.polygon([(x, 110), (x+15, 100), (x+15, 120)], fill='#4facfe')
        draw_rounded_rect(draw, x+20, 90, x+80, 130, 8, fill='white', outline='#4facfe', width=2)
        draw.text((x+50, 110), step, fill='#4facfe', anchor='mm')
        x += 100
    
    # 终点
    draw.ellipse([710, 100, 730, 120], fill='#764ba2')
    draw.text((720, 108), 'AI', fill='white', anchor='mm')
    
    # 标题
    draw.text((400, 40), 'AI文本编辑流程', fill='#333', anchor='mm')
    
    img.save('images/flowchart.png')
    print("已生成: images/flowchart.png")

# 生成第三张图：曲线图
def create_graph_image():
    img = Image.new('RGB', (800, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # 网格线
    for i in range(7):
        draw.line([100 + i*100, 50, 100 + i*100, 250], fill='#ddd')
    for i in range(5):
        draw.line([100, 50 + i*50, 700, 50 + i*50], fill='#ddd')
    
    # U形曲线（使用贝塞尔曲线）
    draw.line([100, 70, 250, 180, 400, 220, 550, 180, 700, 70], fill='#4facfe', width=3)
    
    # 数据点
    draw.ellipse([96, 66, 104, 74], fill='#4facfe')
    draw.ellipse([396, 216, 404, 224], fill='#ff6b6b')
    draw.ellipse([696, 66, 704, 74], fill='#4facfe')
    
    # 坐标轴标签
    draw.text((400, 280), 'AI内容比例 (%)', fill='#666', anchor='mm')
    draw.text((50, 150), '检测准确率', fill='#666')
    
    # 刻度标签
    draw.text((100, 265), '0%', fill='#666', anchor='mm')
    draw.text((400, 265), '50%', fill='#666', anchor='mm')
    draw.text((700, 265), '100%', fill='#666', anchor='mm')
    
    # 标题
    draw.text((400, 30), 'AI检测准确率曲线', fill='#333', anchor='mm')
    
    # 标注
    draw.text((100, 50), '纯人类', fill='#4facfe', anchor='mm')
    draw.text((400, 240), '最难检测', fill='#ff6b6b', anchor='mm')
    draw.text((700, 50), '纯AI', fill='#4facfe', anchor='mm')
    
    img.save('images/graph.png')
    print("已生成: images/graph.png")

# 生成第四张图：影响图
def create_future_image():
    img = Image.new('RGB', (800, 300), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # 书本图标
    draw_rounded_rect(draw, 100, 180, 160, 260, 3, fill='#4facfe')
    draw.rectangle([105, 185, 155, 255], fill='white')
    for i in range(4):
        draw.line([105, 200 + i*15, 155, 200 + i*15], fill='#ddd')
    draw.text((130, 130), '教育', fill='#333', anchor='mm')
    
    # 屏幕图标
    draw_rounded_rect(draw, 280, 160, 380, 230, 5, fill='#333')
    draw.rectangle([285, 165, 375, 225], fill='#4facfe')
    draw.text((330, 130), '平台', fill='#333', anchor='mm')
    
    # AI大脑图标
    draw.ellipse([490, 160, 570, 240], fill='#764ba2')
    draw.text((530, 130), '开发者', fill='#333', anchor='mm')
    
    # 用户图标
    draw.ellipse([675, 175, 725, 225], fill='#ffcdb2')
    draw.ellipse([690, 185, 710, 205], fill='#ffcdb2')
    draw_rounded_rect(draw, 685, 205, 715, 240, 3, fill='#4facfe')
    draw.text((700, 130), '用户', fill='#333', anchor='mm')
    
    # 连接线
    draw.line([160, 220, 280, 195], fill='#4facfe', width=2)
    draw.line([380, 195, 490, 200], fill='#4facfe', width=2)
    draw.line([570, 200, 675, 200], fill='#4facfe', width=2)
    
    # 中心AI
    draw.ellipse([392, 92, 408, 108], fill='#4facfe')
    draw.text((400, 100), 'AI', fill='white', anchor='mm')
    
    # 辐射线
    draw.line([400, 85, 130, 150], fill='#764ba2', width=2)
    draw.line([400, 85, 330, 150], fill='#764ba2', width=2)
    draw.line([400, 85, 530, 150], fill='#764ba2', width=2)
    draw.line([400, 85, 700, 150], fill='#764ba2', width=2)
    
    # 标题
    draw.text((400, 50), 'AI写作的未来影响', fill='#333', anchor='mm')
    
    img.save('images/future.png')
    print("已生成: images/future.png")

# 主函数
if __name__ == "__main__":
    create_collaboration_image()
    create_flowchart_image()
    create_graph_image()
    create_future_image()
    print("所有图片生成完成！")