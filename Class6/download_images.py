import requests
import os

# 创建图片目录
os.makedirs('images', exist_ok=True)

# AI图片生成提示词
prompts = [
    {
        "name": "ai_writing_collaboration",
        "prompt": "AI writing assistant concept, robot hand and human hand collaborating on typing, futuristic digital interface, blue glow, modern technology, clean minimalist style"
    },
    {
        "name": "writing_flowchart",
        "prompt": "infographic flowchart showing human and AI collaborative writing process, steps like polish rewrite compress expand, modern design, blue and orange colors"
    },
    {
        "name": "ai_detection_graph",
        "prompt": "U-shaped graph visualization showing AI text detection accuracy, data chart, professional scientific style, blue and purple gradient"
    },
    {
        "name": "future_education",
        "prompt": "futuristic education scene with students using AI writing tools in modern classroom, technology integration, hopeful atmosphere"
    }
]

# 下载图片
for item in prompts:
    url = f"https://neeko-copilot.bytedance.net/api/text_to_image?prompt={requests.utils.quote(item['prompt'])}&image_size=landscape_16_9"
    filepath = f"images/{item['name']}.jpg"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"已下载: {filepath}")
        else:
            print(f"下载失败 {item['name']}: {response.status_code}")
    except Exception as e:
        print(f"下载失败 {item['name']}: {e}")

print("图片下载完成！")