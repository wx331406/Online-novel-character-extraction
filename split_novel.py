import os
import re
import sys

# 输入文件和输出目录
input_file = sys.argv[1]  # 从命令行参数获取输入文件路径
text_dir = os.path.join(os.path.dirname(__file__), 'demerger')  # 默认输出目录

# 创建输出目录
os.makedirs(text_dir, exist_ok=True)

# 读取文件内容（自动尝试常见中文编码）
encodings = ['utf-8', 'gbk', 'gb2312']
content = ''
for enc in encodings:
    try:
        with open(input_file, 'r', encoding=enc) as f:
            content = f.read()
        break
    except UnicodeDecodeError:
        continue

# 分割章节（匹配'第X章'开头，支持中文数字和阿拉伯数字）
chapters = re.split(r'(\n?第[\u4e00-\u9fa5\d]+章[^\n]*\n)', content)

# 过滤空内容并保存
chapter_num = 0
for i in range(len(chapters)):
    if i % 2 == 1 and i < len(chapters)-1:
        title = chapters[i].strip()
        body = chapters[i+1]
    else:
        continue
    
    # 清理标题中的非法文件名字符
    clean_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    
    # 生成文件名（序号+标题）
    chapter_num += 1
    filename = f"{chapter_num:03d}_{clean_title}.txt"
    text_path = os.path.join(text_dir, filename)
    
    # 写入文件
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n{body}")

print(f"成功分割 {chapter_num} 个章节到 {text_dir}")