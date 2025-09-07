import os
import json
from collections import defaultdict

def process_character_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            character_name = os.path.splitext(filename)[0]
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{character_name}.txt")
            
            stats = {}
            stats['角色名称'] = character_name
            
            # Initialize fields
            stats['别名'] = set()
            gender_found = False
            age_found = False
            best_appearance = {
                '气质': '',
                '服饰': '',
                '饰品': '',
                '特殊标记': ''
            }
            
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == '别名':
                        stats['别名'].update(v.strip() for v in value.split('/') if v.strip())
                    elif key == '性别' and not gender_found:
                        if value != '未知':
                            stats['性别'] = value
                            gender_found = True
                    elif key == '年龄' and not age_found:
                        if value != '未知':
                            stats['年龄'] = value
                            age_found = True
                    elif key in ['气质', '服饰', '饰品', '特殊标记']:
                        if len(value) > len(best_appearance[key]):
                            best_appearance[key] = value
            
            # Handle gender and age defaults
            if not gender_found:
                stats['性别'] = '未知'
            if not age_found:
                stats['年龄'] = '未知'
            
            # Update best appearance fields
            for field in best_appearance:
                stats[field] = best_appearance[field] if best_appearance[field] else '无'
            
            # Process aliases - remove duplicates and exclude character name
            aliases = [a.strip() for a in stats['别名'] if a.strip() != character_name]
            unique_aliases = sorted(set(aliases), key=lambda x: aliases.index(x))  # Preserve original order while deduplicating
            stats['别名'] = ', '.join(unique_aliases) if unique_aliases else '无'
            
            # Handle multiple entries for same character
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Merge existing and new stats
                existing_stats = {}
                for line in existing_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        existing_stats[key.strip()] = value.strip()
                
                # Update stats with existing values where new values are empty/unknown
                for key in ['性别', '年龄', '气质', '服饰', '饰品', '特殊标记']:
                    if key in existing_stats and (stats.get(key) == '未知' or stats.get(key) == '无'):
                        stats[key] = existing_stats[key]
                    elif key in existing_stats and key in stats and len(existing_stats[key]) > len(stats[key]):
                        stats[key] = existing_stats[key]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")

import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python character_stats.py <input_dir> <output_dir>")
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    process_character_files(input_dir, output_dir)