import os 
import json 
import re 
import time 
import gc
from transformers import AutoModelForCausalLM, AutoTokenizer 
 
# 初始化输出目录
os.makedirs('exports', exist_ok=True)
os.makedirs('logs', exist_ok=True)
txt_path = 'exports/character_analysis.txt'  
model_name = "models/Qwen3-Embedding-4B"

try:
    # 加载模型和分词器
    print("正在加载模型...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)   
    model = AutoModelForCausalLM.from_pretrained(   
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    print("模型加载完成")
 
    # 获取章节文件列表
    chapter_files = []
    for f in os.listdir('demerger'):  
        if f.endswith('.txt')  and f != 'character_analysis.txt':  
            if re.match(r'^\d+_',  f):  
                chapter_files.append(f)  

    # 按数字前缀排序 
    chapter_files.sort(key=lambda  x: int(x.split('_')[0]))  

    # 批量处理（每3章为一批）
    for i in range(0, len(chapter_files), 3):
        batch_files = chapter_files[i:i+3]
        batch_content = []
        enable_thinking = enable_thinking if 'enable_thinking' in locals() else False
        
        # 读取批量章节内容 
        for filename in batch_files:
            file_path = os.path.join('demerger',  filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                batch_content.append({   
                    'filename': filename.replace('.txt',  ''),
                    'content': f.read()   
                })
        
        # 构建prompt
        chapters_str = '\n'.join([f'章节{item["filename"]}:\n{item["content"]}' for item in batch_content])
        messages = [{"role": "user", "content": f"""
    请从小说内容中提取详细角色描述词，必须包含以下要素：
    1. 角色名称：（本名/化名/外号）
    2. 性别：（未知则填写：未知）
    3. 职业：（根据文本推断）
    4. 年龄：（根据文本推断）
    5. 气质：（根据文本推理大概气质）
    6 外貌：（必须详细描述并过滤掉血腥暴力描述）
    7.提取必须严谨，禁止出现幻觉

     
    提取规则：
    1. 如果角色有多个别名，全部列出 
    2. 未知信息填写：未知 
    请严格按以下JSON格式返回：
    1. 必须返回纯JSON内容 
    2. JSON字段必须正确闭合 
     
    示例模板：
    {{"chapters": [
      {{
        "characters": [
          {{
            "name": "角色名称",
            "another_name": ["别名1", "别名2"],
            "gender": "性别",
            "careers": "职业",
            "age": "年龄",
            "temper": "气质",
            "appearance": {{
              "clothing": "服饰描述",
              "hairstyle": "发型特征",
              "accessories": "佩戴物品",
              "special_marks": "特殊标识"
            }}
          }}
        ]
      }}
    ]}}
     
    小说内容:
    {chapters_str}
    """}]
 
        text = tokenizer.apply_chat_template(   
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)   

        # 生成文本 
        generated_ids = model.generate(   
            **model_inputs,
            max_new_tokens=32768 
        )
        text_ids= generated_ids[0][len(model_inputs.input_ids[0]):].tolist()   

        # 解析内容 
        try:
            index = len(text_ids) - text_ids[::-1].index(151668)
        except ValueError:
            index = 0 
        content = tokenizer.decode(text_ids[index:],  skip_special_tokens=True).strip("\n")

        # 解析并保存到文件 
        max_retries = 3 
        for attempt in range(max_retries):
            try:
                clean_content = re.sub(r'[\x00-\x1F]+',  '', content)
                clean_content = re.sub(r'^```json\n |```$', '', clean_content, flags=re.MULTILINE)
                bracket_count = clean_content.count('{')  - clean_content.count('}') 
                if bracket_count > 0:
                    clean_content += '}' * bracket_count
                data = json.loads(clean_content)   
                
                # 检查数据结构 
                if not isinstance(data, dict) or 'chapters' not in data:
                    raise ValueError('JSON结构缺少必要字段chapters')
                
                with open(txt_path, 'a', encoding='utf-8') as f:
                    for chapter in data['chapters']:
                        for character in chapter.get('characters',  []):
                            # 直接处理所有角色（不再检查记忆库）
                            char_data = {
                                'name': character.get('name',  '未知'),
                                'another_name': ', '.join(character.get('another_name',  [])),
                                'gender': character.get('gender',  '未知'),
                                'careers': character.get('careers',  '未知'),
                                'age': character.get('age',  '未知'),
                                'temper': character.get('temper',  '未知'),
                                'appearance': character.get('appearance',  {})
                            }
                            
                            # 写入格式化数据 
                            f.write(   
                                f"角色名称: {char_data['name']}\n"
                                f"别名: {char_data['another_name']}\n"
                                f"性别: {char_data['gender']}\n"
                                f"职业: {char_data['careers']}\n"
                                f"年龄: {char_data['age']}\n"
                                f"气质: {char_data['temper']}\n"
                                f"服饰: {char_data['appearance'].get('clothing', '无描述')}\n"
                                f"发型: {char_data['appearance'].get('hairstyle', '无描述')}\n"
                                f"饰品: {char_data['appearance'].get('accessories', '无')}\n"
                                f"特殊标记: {char_data['appearance'].get('special_marks', '无')}\n\n"
                            )
                break 
            except (json.JSONDecodeError, ValueError) as e:
                if attempt < max_retries - 1:
                    print(f"JSON解析失败，重试中... ({attempt+1}/{max_retries})")
                    time.sleep(2  ** attempt)
                else:
                    print(f"解析失败: {e}")
                    with open('logs/error_log.txt',  'a', encoding='utf-8') as log_file:
                        log_file.write(f' 处理批次 {i}-{i+len(batch_files)-1} 时发生错误:\n{str(e)}\n原始内容:\n{content[:500]}...\n\n')
            except Exception as e:
                print(f"未知错误: {e}")
                with open('logs/error_log.txt',  'a', encoding='utf-8') as log_file:
                    log_file.write(f' 处理批次 {i}-{i+len(batch_files)-1} 时发生未知错误:\n{str(e)}\n\n')
                break 
 
        print(f"已处理章节: {', '.join([f['filename'] for f in batch_content])}")

finally:
    # 模型卸载和内存清理
    try:
        # 清理模型资源
        if 'model' in locals():
            del model
            print("模型已卸载")
        if 'tokenizer' in locals():
            del tokenizer
            print("分词器已卸载")
            
        # 强制垃圾回收
        gc.collect()
        print("垃圾回收完成")
        
        # 清理GPU缓存
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("GPU缓存已清理")
        except ImportError:
            pass
            
        # 显示最终内存使用情况
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            print(f"最终内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
        except ImportError:
            pass
            
        print("所有资源已清理完成")
        
    except Exception as e:
        print(f"清理模型资源时发生错误: {e}")