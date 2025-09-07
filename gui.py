import os
import sys
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QSizePolicy, QTabWidget, QGroupBox, QCheckBox, QMessageBox
)
from ui.resource_monitor import ResourceMonitor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QIcon

# 启动密钥验证
STARTUP_KEY = "DFSX2024AI"  # 设置启动密钥

def verify_startup_key():
    """静默验证启动密钥"""
    import os
    
    # 从环境变量获取密钥（由run.bat设置）
    secret_key = os.environ.get('GUI_SECRET_KEY', '')
    
    # 验证密钥
    if secret_key == 'DFSX2024AI':
        print("启动密钥验证通过")
        return True
    else:
        print("启动密钥验证失败")
        return False

class FilePathWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(QPixmap("ui/images/ioc.png").scaled(32, 32)))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(" 开发方：东方数学")
        self.setMinimumSize(1000, 720)  # 最小尺寸限制[2]()

        # 中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget) 
        main_layout = QVBoxLayout(central_widget)

        # 添加标题
        # 标题容器布局
        title_container = QWidget()
        outer_title_layout = QHBoxLayout()
        outer_title_layout.addStretch(1)
        title_layout = QHBoxLayout(title_container)
        outer_title_layout.addWidget(title_container)
        outer_title_layout.addStretch(1)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(10)
        title_layout.addSpacing(10)  # 调整标题左侧间距
        
        
        # 添加标题文本
        title_label = QLabel("AI人工智能网络小说角色描述词提取系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet('''
            QLabel {
                font: bold 34px 'Microsoft YaHei';
                color: white;
                padding: 15px 0;
                border-bottom: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #4CAF50);
            }
        ''')
        title_layout.addWidget(title_label, 1)
        
        # 设置容器布局策略
        title_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addLayout(outer_title_layout)

        # 创建统一背景的监控容器
        monitor_container = QWidget()
        monitor_container.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e0f2e9, stop:1 #c7e6d9);
            border-radius: 8px;
            padding: 12px;
        ''')
        
        # 内部水平布局
        monitor_layout = QHBoxLayout(monitor_container)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.setSpacing(0)
        
        # 创建监控组件（移除独立背景）
        self.cpu_monitor = ResourceMonitor('CPU')
        self.mem_monitor = ResourceMonitor('内存')
        self.gpu_monitor = ResourceMonitor('GPU')
        
        # 添加组件时设置拉伸比例
        monitor_layout.addWidget(self.cpu_monitor, 1)
        monitor_layout.addWidget(self.mem_monitor, 1)
        monitor_layout.addWidget(self.gpu_monitor, 1)

        # 主布局设置
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(monitor_container)
        main_layout.setSpacing(10)
 
        # 创建父级分组容器
        process_group = QGroupBox("小说处理")
        process_group.setObjectName('ProcessGroup')
        process_layout = QVBoxLayout(process_group)

        # 输入路径组件
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_label = QLabel("选择小说路径:")
        self.input_line_edit  = QLineEdit()
        self.input_line_edit.setPlaceholderText(" 点击浏览选择文件或输入路径...")
        input_button = QPushButton("浏览...")
        input_button.setFixedWidth(80)
        input_button.clicked.connect(self.select_input_file)
        input_hbox = QHBoxLayout()
        input_hbox.addWidget(self.input_line_edit)
        input_hbox.addWidget(input_button)
        input_layout.addWidget(input_label)
        input_layout.addLayout(input_hbox)

        # 输出路径组件
        output_group = QWidget()
        output_layout = QVBoxLayout(output_group)
        output_label = QLabel("角色输出路径:")
        self.output_line_edit  = QLineEdit()
        self.output_line_edit.setPlaceholderText(" 处理结果将保存到这里...")
        output_button = QPushButton("浏览...")
        output_button.setFixedWidth(80)
        output_button.clicked.connect(self.select_output_file)
        output_hbox = QHBoxLayout()
        output_hbox.addWidget(self.output_line_edit)
        output_hbox.addWidget(output_button)
        output_layout.addWidget(output_label)
        output_layout.addLayout(output_hbox)

        # 思考模式开关
        self.thinking_checkbox = QCheckBox("慢思考模式（推荐√开启，开启以后速度慢30%—50%）")
        self.thinking_checkbox.setChecked(False)
        
        # 开始按钮
        self.start_button  = QPushButton("开始处理")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_processing)
        
        # 复位按钮
        self.reset_button = QPushButton("复位")
        self.reset_button.setFixedHeight(40)
        self.reset_button.setStyleSheet("background-color: #FFA500;")
        self.reset_button.clicked.connect(self.reset_processing)

        # 添加组件到父容器
        process_layout.addWidget(input_group)
        process_layout.addWidget(output_group)
        process_layout.addWidget(self.thinking_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.start_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        process_layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # 添加父容器到主布局
        main_layout.addWidget(process_group)

        # 添加操作说明标签
        instruction_label = QLabel("使用说明：本程序纯傻瓜式操作，选择你的小说文本路径和角色描述导出路径，然后点击开始即可全自动执行。")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet('''
            QLabel {
                font: 18px 'Microsoft YaHei';
                color: #000000;
                background-color: rgba(224, 242, 233, 0.7);
                padding: 8px 12px;
                border-radius: 4px;
                margin: 10px 20px;
            }
        ''')
        main_layout.addWidget(instruction_label)

        # 样式设置更新
        self.setStyleSheet(""" 
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a1a2f, stop:1 #00ffff);
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                font-size: 12px;
                color: #555;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QGroupBox {
                border: 2px solid #ffffff;
                border-radius: 6px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #d3d3d3;
                font: bold 14px 'Microsoft YaHei';
            }
        """)

    def select_output_file(self):
        directory = QFileDialog.getExistingDirectory(
            self, "选择保存目录", ""
        )
        if directory:
            self.output_line_edit.setText(directory)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName( 
            self, "选择文本文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.input_line_edit.setText(file_path) 

    def start_processing(self):
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class ProcessingThread(QThread):
            finished = pyqtSignal(bool, str)
            
            def __init__(self, input_path, output_path=None, enable_thinking=True):
                super().__init__()
                self.input_path = input_path
                self.output_path = output_path
                self.enable_thinking = enable_thinking
                self.output_line_edit = None
                
            def run(self):
                import subprocess
                import tempfile
                from shutil import copytree
                
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # 小说分割
                        if subprocess.run(["python", "split_novel.py", self.input_path, tmpdir]).returncode != 0:
                            raise Exception("小说分割失败")

                        # 角色提取
                        if subprocess.run(["python", "Qwen3_backup.py", tmpdir, str(int(self.enable_thinking))]).returncode != 0:
                            raise Exception("角色提取失败")

                        # 角色分割
                        if subprocess.run(["python", "sort_characters.py", tmpdir]).returncode != 0:
                            raise Exception("角色分割失败")

                        # 角色合并
                        if subprocess.run(["python", "merge_characters.py", tmpdir]).returncode != 0:
                            raise Exception("角色合并失败")

                        # 角色过滤
                        if subprocess.run(["python", "filter_characters.py", tmpdir]).returncode != 0:
                            raise Exception("角色过滤失败")
                            
                        # 角色信息合并
                        # 使用固定输入目录和GUI指定输出目录
                        output_path = self.output_line_edit.text() or os.path.join(os.path.dirname(__file__), 'Character_Stats')
                        if subprocess.run(["python", "character_stats.py", "Character_Descriptors", output_path]).returncode != 0:
                            raise Exception("角色信息合并失败")
                            
                        # 复制Character_Descriptors到输出路径
                        if self.output_line_edit.text():
                            import shutil
                            src_dir = os.path.join(tmpdir, "Character_Descriptors")
                            dst_dir = os.path.join(self.output_line_edit.text(), "Character_Descriptors")
                            if os.path.exists(src_dir):
                                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
                        
                        self.finished.emit(True, "所有处理步骤已成功完成！")
                except Exception as e:
                    self.finished.emit(False, f"处理过程中发生错误：{str(e)}")
                finally:
                    # 清理临时文件
                    if 'tmpdir' in locals() and os.path.exists(tmpdir):
                        try:
                            # 确保输出目录存在且有效
                            if self.output_path and not os.path.exists(self.output_path):
                                os.makedirs(self.output_path, exist_ok=True)
                            
                            # 复制临时目录内容到输出目录
                            if os.path.exists(tmpdir) and self.output_path:
                                copytree(tmpdir, self.output_path, dirs_exist_ok=True)
                        except Exception as cleanup_error:
                            self.finished.emit(False, f"临时文件清理失败：{str(cleanup_error)}")
                    elif 'tmpdir' in locals() and not os.path.exists(tmpdir):
                        self.finished.emit(True, "处理完成，临时目录已自动清理")
        
        input_path = self.input_line_edit.text()

        if not os.path.exists(input_path):
            self.show_message("错误", "请选择有效的小说路径！")
            return
            
        # 禁用开始按钮防止重复点击
        self.start_button.setEnabled(False)
        
        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(
            input_path, 
            self.output_line_edit.text(),
            self.thinking_checkbox.isChecked()
        )
        self.processing_thread.output_line_edit = self.output_line_edit
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()
        
    def on_processing_finished(self, success, message):
        # 重新启用开始按钮
        self.start_button.setEnabled(True)
        
        if success:
            self.show_message("处理完成", message)
        else:
            self.show_message("处理错误", message)
 
    def show_message(self, title, message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self,  title, message)
        
    def reset_processing(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, '确认复位', '确定要复位吗？这将删除所有生成的角色数据！', 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            import shutil
            folders_to_delete = ["Character_Descriptors", "demerger", "exports", "logs", "Character_Stats"]
            for folder in folders_to_delete:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                    except Exception as e:
                        self.show_message("错误", f"删除{folder}文件夹失败: {str(e)}")
                        return
            self.show_message("成功", "所有生成数据已清除！")

    def closeEvent(self, event):
        # 安全停止所有监控组件
        self.cpu_monitor.stop()
        self.mem_monitor.stop()
        self.gpu_monitor.stop()
        event.accept()

# 修改主程序入口点
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 启动验证
    if verify_startup_key():
        window = FilePathWindow()
        window.show() 
        sys.exit(app.exec())
    else:
        QMessageBox.critical(None, "启动失败", "密钥验证失败，程序即将退出！")
        sys.exit(1)