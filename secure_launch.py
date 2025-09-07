#!/usr/bin/env python3
"""
安全启动脚本 - 自动验证密钥并启动GUI
"""
import os
import sys
import subprocess

def secure_launch():
    """安全启动程序"""
    # 预设的启动密钥
    SECRET_KEY = "DFSX2024AI"
    
    # 设置环境变量，让gui.py自动通过验证
    os.environ['GUI_SECRET_KEY'] = SECRET_KEY
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 激活环境并启动GUI
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(current_dir, 'activate.bat')
        gui_script = os.path.join(current_dir, 'gui.py')
        
        # 使用subprocess启动，传递环境变量
        env = os.environ.copy()
        env['GUI_SECRET_KEY'] = SECRET_KEY
        
        # 启动gui.py
        subprocess.run([sys.executable, gui_script], env=env)
    else:  # Unix-like
        activate_script = os.path.join(current_dir, 'activate')
        gui_script = os.path.join(current_dir, 'gui.py')
        
        env = os.environ.copy()
        env['GUI_SECRET_KEY'] = SECRET_KEY
        
        subprocess.run([sys.executable, gui_script], env=env)

if __name__ == "__main__":
    secure_launch()