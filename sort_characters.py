import re
import os
from collections import defaultdict

# 输入文件路径
input_path = os.path.join(os.path.dirname(__file__), 'exports', 'character_analysis.txt')

try:
    # 读取文件内容
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按空行分割角色信息块并过滤空内容
    blocks = [block.strip() for block in content.split('\n\n') if block.strip()]

    # 定义排序键：提取角色名称
    def get_name(block):
        match = re.search(r'名称: (.+)', block)
        return match.group(1) if match else ''

    # 按中文名称排序
    sorted_blocks = sorted(blocks, key=get_name)

    # 重新组合内容并写入文件
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(sorted_blocks))

    # 创建角色描述目录
    descriptor_dir = os.path.join(os.path.dirname(__file__), 'Character_Descriptors')
    os.makedirs(descriptor_dir, exist_ok=True)

    # 按角色名称分组
    role_groups = defaultdict(list)
    for block in sorted_blocks:
        name_match = re.search(r'名称: (.+)', block)
        if name_match:
            role_name = name_match.group(1).strip()
            safe_name = re.sub(r'[\\/:*?"<>|]', '_', role_name)
            role_groups[safe_name].append(block)

    # 写入分组文件
    for role_name, blocks in role_groups.items():
        logs_path = os.path.join(descriptor_dir, f'{role_name}.txt')
        try:
            with open(logs_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(blocks))
        except Exception as e:
            print(f'写入 {role_name} 文件时出错: {str(e)}')

    print(f'成功排序并保存 {len(sorted_blocks)} 个角色信息到 {descriptor_dir}')

except FileNotFoundError:
    print(f'错误：文件 {input_path} 不存在')
except Exception as e:
    print(f'排序过程中发生错误: {str(e)}')