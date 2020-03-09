'''
@author: Shaocr
@Date: 2019.10.12
@Description: Program of showing plot which contains all train both running state and time
'''
import sys

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QLegend, \
    QCategoryAxis
from PyQt5.QtCore import Qt, QPointF, QRectF, QPoint
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsLineItem, QWidget, \
    QHBoxLayout, QLabel, QVBoxLayout, QGraphicsProxyWidget


# Child element of the prompt window
#    ############
#    #train1:0,0<--this
#    #train2:1,2#
#    ############
class ToolTipItem(QWidget):
    '''
    Args:
        color: the color of item to show information
        text: the information which you want to show in the item
    return:
        None
    '''

    def __init__(self, color, text, parent=None):
        super(ToolTipItem, self).__init__(parent)
        # Design layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a label to display information
        clabel = QLabel(self)

        # Set parameter of label
        clabel.setMinimumSize(12, 12)
        clabel.setMaximumSize(12, 12)

        # Set QSS of label
        clabel.setStyleSheet("border-radius:6px;background: rgba(%s,%s,%s,%s);" % (
            color.red(), color.green(), color.blue(), color.alpha()))

        # Add label to layout
        layout.addWidget(clabel)

        # Create label to show name
        self.textLabel = QLabel(text, self, styleSheet="color:white;")
        layout.addWidget(self.textLabel)

    def setText(self, text):
        self.textLabel.setText(text)


# prompt window
#    ############
#    #train1:0,0#<--all this
#    #train2:1,2#
#    ############
class ToolTipWidget(QWidget):
    Cache = {}

    def __init__(self, *args, **kwargs):
        super(ToolTipWidget, self).__init__(*args, **kwargs)
        # Set parameter of prompt window
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Ser Qss
        self.setStyleSheet(
            "ToolTipWidget{background: rgba(50, 50, 50, 100);border-radius:6px;}")

        # Create Layout
        layout = QVBoxLayout(self)

        # Add title
        self.titleLabel = QLabel(self, styleSheet="color:white;")
        layout.addWidget(self.titleLabel)

    def updateUi(self, title, points):
        self.titleLabel.setText(title)
        for serie, point in points:
            if serie not in self.Cache:
                item = ToolTipItem(
                    serie.color(),
                    (serie.name() or "-") + ":" + str(point.x()), self)
                self.layout().addWidget(item)
                self.Cache[serie] = item
            else:
                self.Cache[serie].setText(
                    (serie.name() or "-") + ":" + str(point.x()))
            self.Cache[serie].setVisible(serie.isVisible())  # 隐藏那些不可用的项
        self.adjustSize()  # 调整大小


class GraphicsProxyWidget(QGraphicsProxyWidget):

    def __init__(self, *args, **kwargs):
        super(GraphicsProxyWidget, self).__init__(*args, **kwargs)
        self.setZValue(999)
        self.tipWidget = ToolTipWidget()
        self.setWidget(self.tipWidget)
        self.hide()

    def width(self):
        return self.size().width()

    def height(self):
        return self.size().height()

    def show(self, title, points, pos):
        self.setGeometry(QRectF(pos, self.size()))
        self.tipWidget.updateUi(title, points)
        super(GraphicsProxyWidget, self).show()


class LineChartView(QChartView):

    def __init__(self):
        super(LineChartView, self).__init__()
        self.resize(800, 600)
        self.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        # 自定义x轴label

    def CreatePlot(self, NumSection, Alltime, PlotData,type,name='列车调度'):
        if type == 1:
            self.initChart(NumSection, Alltime, PlotData,name)
        else:
            self.initProgressChart(NumSection, Alltime, PlotData,name)

        # 提示widget
        self.toolTipWidget = GraphicsProxyWidget(self._chart)

        # line
        self.lineItem = QGraphicsLineItem(self._chart)
        pen = QPen(Qt.gray)
        pen.setWidth(1)
        self.lineItem.setPen(pen)
        self.lineItem.setZValue(998)
        #self.lineItem.hide()
        self.lineItem.show()
        # 一些固定计算，减少mouseMoveEvent中的计算量
        # 获取x和y轴的最小最大值
        axisX, axisY = self._chart.axisX(), self._chart.axisY()
        self.min_x, self.max_x = axisX.min(), axisX.max()
        self.min_y, self.max_y = axisY.min(), axisY.max()
    def resizeEvent(self, event):
        super(LineChartView, self).resizeEvent(event)
        # 当窗口大小改变时需要重新计算
        # 坐标系中左上角顶点
        self.point_top = self._chart.mapToPosition(
            QPointF(self.min_x, self.max_y))
        # 坐标原点坐标
        self.point_bottom = self._chart.mapToPosition(
            QPointF(self.min_x, self.min_y))
        self.step_x = (self.max_x - self.min_x) / (self._chart.axisX().tickCount() - 1)

    def mouseMoveEvent(self, event):
        super(LineChartView, self).mouseMoveEvent(event)
        pos = event.pos()
        # 把鼠标位置所在点转换为对应的xy值
        x = self._chart.mapToValue(pos).x()
        y = self._chart.mapToValue(pos).y()
        index = round(int(x/self.step_x)*self.step_x) + round(x%self.step_x)-1
        #index = round((x - self.min_x) / self.step_x)
        # 得到在坐标系中的所有正常显示的series的类型和点
        points = [(serie, serie.at(index))
                  for serie in self._chart.series()
                  if self.min_x <= x <= self.max_x and
                  self.min_y <= y <= self.max_y]
        if points:
            pos_x = self._chart.mapToPosition(
                QPointF(index * self.step_x + self.min_x, self.min_y))
            self.lineItem.setLine(pos_x.x(), self.point_top.y(),
                                  pos_x.x(), self.point_bottom.y())
            self.lineItem.show()
            try:
                title = ""
            except:
                title = ""
            t_width = self.toolTipWidget.width()
            t_height = self.toolTipWidget.height()
            # 如果鼠标位置离右侧的距离小于tip宽度
            x = pos.x() - t_width if self.width() - \
                                     pos.x() - 20 < t_width else pos.x()
            # 如果鼠标位置离底部的高度小于tip高度
            y = pos.y() - t_height if self.height() - \
                                      pos.y() - 20 < t_height else pos.y()
            self.toolTipWidget.show(
                title, points, QPoint(x, y))
        else:
            self.toolTipWidget.hide()
            self.lineItem.hide()

    def handleMarkerClicked(self):
        marker = self.sender()  # 信号发送者
        if not marker:
            return
        visible = not marker.series().isVisible()
        #         # 隐藏或显示series
        marker.series().setVisible(visible)
        marker.setVisible(True)  # 要保证marker一直显示
        # 透明度
        alpha = 1.0 if visible else 0.4
        # 设置label的透明度
        brush = marker.labelBrush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setLabelBrush(brush)
        # 设置marker的透明度
        brush = marker.brush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setBrush(brush)
        # 设置画笔透明度
        pen = marker.pen()
        color = pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)
        marker.setPen(pen)

    def handleMarkerHovered(self, status):
        # 设置series的画笔宽度
        marker = self.sender()  # 信号发送者
        if not marker:
            return
        series = marker.series()
        if not series:
            return
        pen = series.pen()
        if not pen:
            return
        pen.setWidth(pen.width() + (1 if status else -1))
        series.setPen(pen)

    def handleSeriesHoverd(self, point, state):
        # 设置series的画笔宽度
        series = self.sender()  # 信号发送者
        pen = series.pen()
        if not pen:
            return
        pen.setWidth(pen.width() + (1 if state else -1))
        series.setPen(pen)

    def initProgressChart(self,MaxTime, Allgen,PlotData,name):
        MinTime = 100000
        for k in PlotData:
            if min(k[1]) < MinTime:
                MinTime = min(k[1])
        self._chart = QChart(title=name)
        self._chart.setAcceptHoverEvents(True)
        # Series动画

        self._chart.setAnimationOptions(QChart.SeriesAnimations)
        # dataTable = [
        #     ["邮件营销", [120, 132, 101, 134, 90, 230]],
        #     ["联盟广告", [220, 182, 191, 234, 290, 330, 310]],
        #     ["视频广告", [150, 232, 201, 154, 190, 330, 410]],
        #     ["直接访问", [320, 332, 301, 334, 390, 330, 320]],
        #     ["搜索引擎", [820, 932, 901, 934, 1290, 1330, 1320]]
        # ]
        for series_name, data_list, label_list in PlotData:
            series = QLineSeries(self._chart)
            for j, v in zip(label_list, data_list):
                series.append(j, v)
            series.setName(series_name)
            series.setPointsVisible(True)  # 显示圆点
            series.hovered.connect(self.handleSeriesHoverd)  # 鼠标悬停
            self._chart.addSeries(series)
        self._chart.createDefaultAxes()  # 创建默认的轴
        axisX = self._chart.axisX()  # x轴
        axisX.setTickCount(11)  # x轴设置7个刻度
        axisX.setGridLineVisible(False)  # 隐藏从x轴往上的线条
        axisY = self._chart.axisY()
        axisY.setTickCount(10)  # y轴设置7个刻度
        #axisY.setRange(0, MaxTime)  # 设置y轴范围
        # 自定义x轴
        # axis_x = QCategoryAxis(
        #     self._chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
        # axis_x.setTickCount(Allgen)
        # axis_x.setGridLineVisible(False)
        # min_x = axisX.min()
        # for i in range(0, Allgen + 1):
        #     axis_x.append(str(i), min_x + i)
        # self._chart.setAxisX(axis_x, self._chart.series()[-1])

        # 自定义y轴
        # axis_y = QCategoryAxis(
        #     self._chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
        # axis_y.setTickCount(round(MaxTime)-max(round(MinTime)-10,0))
        # axis_y.setRange(max(round(MinTime)-10,0), round(MaxTime))
        # for i in range(max(round(MinTime)-10,0), round(MaxTime) + 1):
        #     axis_y.append('%i' % i, i)
        # self._chart.setAxisY(axis_y, self._chart.series()[-1])
        # chart的图例
        legend = self._chart.legend()
        # 设置图例由Series来决定样式
        legend.setMarkerShape(QLegend.MarkerShapeFromSeries)
        # 遍历图例上的标记并绑定信号
        for marker in legend.markers():
            # 点击事件
            marker.clicked.connect(self.handleMarkerClicked)
            # 鼠标悬停事件
            marker.hovered.connect(self.handleMarkerHovered)
        self.setChart(self._chart)
    def initChart(self, NumSection, Alltime, PlotData,name):
        self._chart = QChart(title=name)
        self._chart.setAcceptHoverEvents(True)
        # Series动画
        self._chart.setAnimationOptions(QChart.SeriesAnimations)
        # dataTable = [
        #     ["邮件营销", [120, 132, 101, 134, 90, 230]],
        #     ["联盟广告", [220, 182, 191, 234, 290, 330, 310]],
        #     ["视频广告", [150, 232, 201, 154, 190, 330, 410]],
        #     ["直接访问", [320, 332, 301, 334, 390, 330, 320]],
        #     ["搜索引擎", [820, 932, 901, 934, 1290, 1330, 1320]]
        # ]
        for series_name, data_list, label_list in PlotData:
            series = QLineSeries(self._chart)
            for j, v in zip(label_list, data_list):
                series.append(j, v)
            series.setName(series_name)
            series.setPointsVisible(True)  # 显示圆点
            series.hovered.connect(self.handleSeriesHoverd)  # 鼠标悬停
            self._chart.addSeries(series)
        self._chart.createDefaultAxes()  # 创建默认的轴
        axisX = self._chart.axisX()  # x轴
        axisX.setTickCount(Alltime)  # x轴设置7个刻度
        axisX.setGridLineVisible(False)  # 隐藏从x轴往上的线条
        axisY = self._chart.axisY()
        axisY.setTickCount(NumSection)  # y轴设置7个刻度
        axisY.setRange(0, NumSection)  # 设置y轴范围
        # 自定义x轴
        axis_x = QCategoryAxis(
            self._chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
        axis_x.setTickCount(Alltime + 1)
        axis_x.setGridLineVisible(False)
        min_x = axisX.min()
        for i in range(0, Alltime + 1):
            axis_x.append(str(i), min_x + i)
        self._chart.setAxisX(axis_x, self._chart.series()[-1])

        # 自定义y轴
        axis_y = QCategoryAxis(
            self._chart, labelsPosition=QCategoryAxis.AxisLabelsPositionCenter)
        axis_y.setTickCount(NumSection)
        axis_y.setRange(0, NumSection)
        for i in range(0, NumSection + 1):
            axis_y.append('section%i' % (NumSection - i + 1), i)
        self._chart.setAxisY(axis_y, self._chart.series()[-1])
        # chart的图例
        legend = self._chart.legend()
        # 设置图例由Series来决定样式
        legend.setMarkerShape(QLegend.MarkerShapeFromSeries)
        # 遍历图例上的标记并绑定信号
        for marker in legend.markers():
            # 点击事件
            marker.clicked.connect(self.handleMarkerClicked)
            # 鼠标悬停事件
            marker.hovered.connect(self.handleMarkerHovered)
        self.setChart(self._chart)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = LineChartView(['1', '1', '1', '1', '1', '1', '1'], 1, 1)
    view.show()
    sys.exit(app.exec_())
