import subprocess
import sys
import os

def run_command(cmd):
    """运行命令并显示输出"""
    print(f"正在执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def check_api_key():
    """检查配置文件中是否存在API Key"""
    config_file = "config.env"
    if not os.path.exists(config_file):
        print("错误: 配置文件 config.env 不存在")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('DEEPSEEK_API_KEY=') and len(line.strip().split('=', 1)[1]) > 0:
                return True
    print("错误: 请在 config.env 文件中配置 DEEPSEEK_API_KEY")
    return False

if __name__ == "__main__":
    # 检查API Key是否已配置
    if not check_api_key():
        sys.exit(1)
    
    # 步骤1: 爬取arxiv论文
    print("\n=== 步骤1: 爬取arxiv论文 ===")
    if not run_command("python arxiv_crawler.py"):
        print("爬取失败，退出")
        sys.exit(1)
    
    # 步骤2: 选择论文并下载PDF
    print("\n=== 步骤2: 选择论文并下载PDF ===")
    if not run_command("python paper_selector.py"):
        print("选择论文失败，退出")
        sys.exit(1)
    
    # 步骤3: 解析PDF并生成科普文章
    print("\n=== 步骤3: 解析PDF并生成科普文章 ===")
    if not run_command("python pdf_parser.py"):
        print("生成科普文章失败，退出")
        sys.exit(1)
    
    # 步骤4: 生成HTML文件
    print("\n=== 步骤4: 生成HTML文件 ===")
    if not run_command("python html_generator.py"):
        print("生成HTML失败，退出")
        sys.exit(1)
    
    print("\n=== 所有步骤完成！===")
    print("科普文章已生成: 科普文章.html")