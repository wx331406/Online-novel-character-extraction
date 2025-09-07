from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter
import psutil

class ResourceMonitor(QWidget):
    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

    def __init__(self, monitor_type):
        super().__init__()
        self.monitor_type = monitor_type
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.init_ui()
        self.init_data_series()

    def init_ui(self):
        self.setObjectName('ResourceMonitor')
        self.layout = QVBoxLayout(self)
        
        # 图表设置
        self.chart = QChart()
        self.chart.setTitleBrush(Qt.GlobalColor.white)
        self.chart.setTitle("系统资源监控")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor(12, 20, 32)))
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 添加实时数值显示标签
        self.value_label = QLabel(self.chart_view)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.value_label.setStyleSheet('''
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.5);
                padding: 4px 8px;
                border-radius: 4px;
            }
        ''')
        self.value_label.setGeometry(self.chart_view.width()-100, 30, 80, 30)
        
        self.chart_view.setStyleSheet('''
            QChartView#ResourceMonitor {
                background: transparent;
                border-radius: 8px;
                padding: 12px;
            }
            QChart {
                background: transparent;
                border: none;
            }
            QChart::title {
                color: #80c8ff;
                font-size: 16px;
            }
            QAxis {
                color: #80c8ff;
                grid-line-color: rgba(255,255,255,0.1);
            }
        ''')
        self.layout.addWidget(self.chart_view)

    def init_data_series(self):
        self.series = QLineSeries()
        if self.monitor_type == 'CPU':
            self.series.setName("CPU利用率")
            self.chart.setTitle("CPU使用监控")
        elif self.monitor_type == '内存':
            self.series.setName("内存利用率")
            self.chart.setTitle("内存使用监控")
        else:
            self.series.setName("GPU利用率")
            self.chart.setTitle("GPU使用监控")
        
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.axes(Qt.Orientation.Horizontal)[0].setRange(0, 60)
        self.chart.axes(Qt.Orientation.Vertical)[0].setRange(0, 100)
        
        # 确保图表初始化完成后启动定时器
        self.timer.start(1000)

    def update_data(self):
        if self.monitor_type == 'CPU':
            value = psutil.cpu_percent()
        elif self.monitor_type == '内存':
            value = psutil.virtual_memory().percent
        else:
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                value = util.gpu
                pynvml.nvmlShutdown()
            except Exception as e:
                print(f"GPU监控异常: {e}")
                self.gpu_available = False
                self.timer.stop()
                return

        # 更新数值标签
        self.value_label.setText(f"{value:.1f}%")
        self.value_label.adjustSize()
        self.value_label.move(self.chart_view.width()-self.value_label.width()-20, 40)
        
        # 仅更新数据，避免重复添加组件
        self.update_series(self.series, value)

    def update_series(self, series, value):
        points = series.points()
        if len(points) > 60:
            series.removePoints(0, len(points)-60)
        x_pos = points[-1].x() + 1 if points else 0
        self.chart.axes(Qt.Orientation.Horizontal)[0].setRange(max(0, x_pos-60), x_pos)
        series.append(x_pos, value)