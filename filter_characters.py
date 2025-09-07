import os
import re
import time

def filter_character_files(directory):
    os.makedirs(directory, exist_ok=True)
    delete_queue = []
    total_files = 0  # 新增统计总文件数
    
    # 第一阶段：统计文件
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            total_files += 1
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    count = len(re.findall(r'^角色名称:\s+([^\s]+)', content, flags=re.M))
                    
                    if count < 3:
                        delete_queue.append(filepath)
                        print(f'待删除文件: {filename}（角色描述不足）')
                    else:
                        print(f'保留文件: {filename}（找到{count}条角色描述）')
            except Exception as e:
                print(f'处理文件 {filename} 时发生系统错误: {type(e).__name__} - {str(e)}')
    
    # 第二阶段：批量删除
    for filepath in delete_queue:
        max_retries = 3
        filename = os.path.basename(filepath)
        for attempt in range(max_retries):
            try:
                os.remove(filepath)
                print(f'已删除文件: {filename}')
                break
            except PermissionError as pe:
                if attempt < max_retries - 1:
                    print(f'文件 {filename} 被占用，正在重试 ({attempt+1}/{max_retries})')
                    time.sleep(0.5 * (attempt + 1))
                else:
                    print(f'无法删除 {filename}: 文件被占用超过最大重试次数，请手动处理 | 错误详情: {str(pe)}')
            except Exception as e:
                print(f'删除 {filename} 时发生意外错误: {type(e).__name__} - {str(e)}')
                break
    
    remaining = total_files - len(delete_queue)
    print(f'处理完成，共删除 {len(delete_queue)} 个无效角色文件，剩余 {remaining} 个有效角色文件')

if __name__ == '__main__':
    target_dir = os.path.join(os.path.dirname(__file__), 'Character_Descriptors')
    filter_character_files(target_dir)