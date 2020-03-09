# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
from MIP.CalculateByMIP_back import Solve as MIPSolve
from GA.CalculateByGA import Solve as GASolve
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import Qt
from GUI.RunningLine import LineChartView
from GUI.Graph.optimizationprocess import PlotData,ShowData
import random
_translate = QtCore.QCoreApplication.translate
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(718, 736)
        self.InfotmationTable = QtWidgets.QTableWidget(Form)
        self.InfotmationTable.setGeometry(QtCore.QRect(0, 0, 721, 511))
        self.InfotmationTable.setObjectName("InfotmationTable")
        self.InfotmationTable.setColumnCount(0)
        self.InfotmationTable.setRowCount(0)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 520, 301, 101))
        self.groupBox.setObjectName("groupBox")
        self.AddTrain = QtWidgets.QPushButton(self.groupBox)
        self.AddTrain.setGeometry(QtCore.QRect(20, 20, 93, 28))
        self.AddTrain.setObjectName("AddTrain")
        self.AddSection = QtWidgets.QPushButton(self.groupBox)
        self.AddSection.setGeometry(QtCore.QRect(170, 20, 93, 28))
        self.AddSection.setObjectName("AddSection")
        self.AddMultiTrack = QtWidgets.QPushButton(self.groupBox)
        self.AddMultiTrack.setGeometry(QtCore.QRect(20, 60, 93, 28))
        self.AddMultiTrack.setObjectName("AddMultiTrack")
        self.CreateRandomData = QtWidgets.QPushButton(self.groupBox)
        self.CreateRandomData.setGeometry(QtCore.QRect(170, 60, 93, 28))
        self.CreateRandomData.setObjectName("CreateRandomData")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(330, 520, 371, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.RunningLinePlot = QtWidgets.QCheckBox(self.groupBox_2)
        self.RunningLinePlot.setGeometry(QtCore.QRect(10, 20, 101, 19))
        self.RunningLinePlot.setObjectName("RunningLinePlot")
        self.gantPolt = QtWidgets.QCheckBox(self.groupBox_2)
        self.gantPolt.setGeometry(QtCore.QRect(140, 20, 91, 19))
        self.gantPolt.setObjectName("gantPolt")
        self.ProcessingPlot = QtWidgets.QCheckBox(self.groupBox_2)
        self.ProcessingPlot.setGeometry(QtCore.QRect(10, 60, 101, 19))
        self.ProcessingPlot.setObjectName("ProcessingPlot")
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 630, 691, 101))
        self.groupBox_3.setObjectName("groupBox_3")
        self.GA = QtWidgets.QRadioButton(self.groupBox_3)
        self.GA.setGeometry(QtCore.QRect(20, 30, 115, 19))
        self.GA.setObjectName("GA")
        self.GA_improve = QtWidgets.QRadioButton(self.groupBox_3)
        self.GA_improve.setGeometry(QtCore.QRect(20, 60, 115, 19))
        self.GA_improve.setObjectName("GA_improve")
        self.MIP = QtWidgets.QRadioButton(self.groupBox_3)
        self.MIP.setGeometry(QtCore.QRect(170, 30, 115, 19))
        self.MIP.setObjectName("MIP")
        self.FJSP = QtWidgets.QRadioButton(self.groupBox_3)
        self.FJSP.setGeometry(QtCore.QRect(170, 60, 115, 19))
        self.FJSP.setObjectName("FJSP")
        self.StartSolve = QtWidgets.QPushButton(self.groupBox_3)
        self.StartSolve.setGeometry(QtCore.QRect(460, 40, 93, 28))
        self.StartSolve.setObjectName("StartSolve")
        self.IfMultiTrack=False

        self.AddTrain.clicked.connect(self.Signal_AddTrain)
        self.AddSection.clicked.connect(self.Signal_AddSection)
        self.StartSolve.clicked.connect(self.Signal_StartSolve)
        self.AddMultiTrack.clicked.connect(self.Signal_AddMultiTrack)
        self.CreateRandomData.clicked.connect(self.Signal_CreateRandomData)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.RunningView_MIP = LineChartView()
        self.RunningView_GA = LineChartView()
        self.RunningView_GAimprove = LineChartView()
        self.RunningView_FJSP = LineChartView()
        self.RunningProcess_MIP = LineChartView()
        self.RunningProcess_GA = LineChartView()
        self.RunningProcess_GAimporve = LineChartView()
        self.RunningProcess_FJSP = LineChartView()
        self.allbest = []

        self.InfotmationTable.insertColumn(0)
        item = QtWidgets.QTableWidgetItem()
        self.InfotmationTable.setHorizontalHeaderItem(self.InfotmationTable.columnCount() - 1, item)
        # item = self.InfotmationTable.horizontalHeaderItem(self.InfotmationTable.columnCount()-1)
        item.setText(_translate("Form", "Direction"))
    def Signal_AddTrain(self):
        self.InfotmationTable.insertRow(self.InfotmationTable.rowCount()-self.IfMultiTrack)
        item = QtWidgets.QTableWidgetItem()
        self.InfotmationTable.setVerticalHeaderItem(self.InfotmationTable.rowCount()-1-self.IfMultiTrack, item)
        #item = self.InfotmationTable.verticalHeaderItem(0)
        item.setText(_translate("Form","Train%i"%(self.InfotmationTable.rowCount()-self.IfMultiTrack)))
    def Signal_AddSection(self):
        self.InfotmationTable.insertColumn(self.InfotmationTable.columnCount())
        item = QtWidgets.QTableWidgetItem()
        self.InfotmationTable.setHorizontalHeaderItem(self.InfotmationTable.columnCount() - 1, item)
        #item = self.InfotmationTable.horizontalHeaderItem(self.InfotmationTable.columnCount()-1)
        item.setText(_translate("Form", "Section%i" % (self.InfotmationTable.columnCount())))
    def Signal_StartSolve(self):
        ScheduleData=self.GetAllJobsData()

        if self.MIP.isChecked():
            res, Job_task, Machine_task = MIPSolve(ScheduleData)
            self.RunningView_MIP.CreatePlot(self.InfotmationTable.columnCount()-1,int(res),Job_task,1)
            self.RunningView_MIP.show()
        if self.GA.isChecked():
            res, Job_task, Machine_task,best,repair,process= GASolve(ScheduleData)
            self.RunningView_GA.CreatePlot(self.InfotmationTable.columnCount()-1, int(res), Job_task,1,"未修复前")
            self.RunningView_GA.show()
            res_repair = max([max(i[2]) for i in repair])
            self.RunningView_GA_repair = LineChartView()
            self.RunningView_GA_repair.CreatePlot(self.InfotmationTable.columnCount()-1, int(res_repair), repair,1,"修复后")
            self.RunningView_GA_repair.show()

            for i in process:
                i.show()
            # self.RunningProcess_GA.CreatePlot(max(best[0][1]),len(best[0][1]),best,2)
            # self.RunningProcess_GA.show()
            # best[0][0]='Genetic'
            # PlotData(best[0],':','#7cb5ec')
            self.allbest.append(best[0])
        if self.GA_improve.isChecked():
            res, Job_task, Machine_task, best = GASolve(ScheduleData,0.006,0.85,0.1)
            self.allbest.append(best[0])
            MaxTime = 0
            for k in self.allbest:
                if max(k[1]) > MaxTime:
                    MaxTime = round(max(k[1]))
            # self.RunningProcess_GAimporve.CreatePlot(MaxTime, len(best[0][1]), self.allbest, 2)
            # self.RunningProcess_GAimporve.show()
            self.RunningView_GA.CreatePlot(self.InfotmationTable.columnCount(), int(res), Job_task, 1)
            self.RunningView_GA.show()
            best[0][0] = 'Genetic with conflict repair'
            PlotData(best[0],'--','#3398DB')
        if self.FJSP.isChecked():
            res, Job_task, Machine_task, best = GASolve(ScheduleData,0.005,0.9,0.05)
            best[0][0] = 'FJSP-IV'
            self.allbest.append(best[0])
            MaxTime = 0
            for k in self.allbest:
                if max(k[1]) > MaxTime:
                    MaxTime = round(max(k[1]))
            # self.RunningProcess_FJSP.CreatePlot(MaxTime, len(best[0][1]), self.allbest, 2)
            # self.RunningProcess_FJSP.show()
            self.RunningView_FJSP.CreatePlot(self.InfotmationTable.columnCount(), int(res), Job_task, 1)
            self.RunningView_FJSP.show()
            PlotData(best[0],'-','#6495ed')
            ShowData()
    def GetAllJobsData(self):
        ScheduleData={'machinesNb':0,'jobs':[]}
        n=self.InfotmationTable.rowCount()-1
        SumOfMachine=0
        if self.IfMultiTrack:
            Tracks = [int(self.InfotmationTable.item(n,i).text()) for i in range(1,self.InfotmationTable.columnCount())]
        else:
            Tracks = [1 for i in range(1,self.InfotmationTable.columnCount())]
        for i in range(self.InfotmationTable.rowCount()-self.IfMultiTrack):
            TaskCostData=[]
            SumOfMachine=0
            if self.InfotmationTable.item(i,0).text() == "1":
                for j in range(1,self.InfotmationTable.columnCount()):
                    MachineCostData=[]
                    for k in range(Tracks[j-1]):
                        if self.InfotmationTable.item(i, j).text() != "":
                            MachineCostData.append({'processingTime':int(self.InfotmationTable.item(i,j).text()),'machine':k+SumOfMachine})
                    SumOfMachine+=Tracks[j-1]
                    if len(MachineCostData)!=0:
                        TaskCostData.append(MachineCostData)
            else:
                SumOfMachine=sum(Tracks)-1
                for j in range(self.InfotmationTable.columnCount()-1,0,-1):
                    MachineCostData=[]
                    for k in range(Tracks[j-1]):
                        if self.InfotmationTable.item(i, j).text() != "":
                            MachineCostData.append({'processingTime':int(self.InfotmationTable.item(i,j).text()),'machine':k+SumOfMachine})
                    SumOfMachine-=Tracks[j-1]
                    if len(MachineCostData)!=0:
                        TaskCostData.append(MachineCostData)
            ScheduleData['jobs'].append(TaskCostData)
        ScheduleData['machinesNb']=sum(Tracks)
        print(ScheduleData)
        return ScheduleData
    def Signal_AddMultiTrack(self):
        if self.IfMultiTrack:
            return
        self.IfMultiTrack=True
        self.InfotmationTable.insertRow(self.InfotmationTable.rowCount())
        item = QtWidgets.QTableWidgetItem()
        self.InfotmationTable.setVerticalHeaderItem(self.InfotmationTable.rowCount() - 1, item)
        item.setText(_translate("Form", "Track"))
    def Signal_CreateRandomData(self):
        for i in range(self.InfotmationTable.rowCount()):
            for j in range(self.InfotmationTable.columnCount()):
                if self.InfotmationTable.item(i,j)==None:
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(_translate("Form", str(random.randint(1,600))))
                    self.InfotmationTable.setItem(i,j,item)
                else:
                    self.InfotmationTable.item(i,j).setText(_translate("Form",str(random.randint(2,6))))
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "数据添加"))
        self.AddTrain.setText(_translate("Form", "添加列车"))
        self.AddSection.setText(_translate("Form", "添加站点"))
        self.AddMultiTrack.setText(_translate("Form", "添加多轨"))
        self.CreateRandomData.setText(_translate("Form", "随机数据"))
        self.groupBox_2.setTitle(_translate("Form", "数据显示"))
        self.RunningLinePlot.setText(_translate("Form", "列车运行图"))
        self.gantPolt.setText(_translate("Form", "甘特图"))
        self.ProcessingPlot.setText(_translate("Form", "过程曲线图"))
        self.groupBox_3.setTitle(_translate("Form", "算法选择"))
        self.GA.setText(_translate("Form", "遗传算法"))
        self.GA_improve.setText(_translate("Form", "改进遗传算法"))
        self.MIP.setText(_translate("Form", "分支定界"))
        self.FJSP.setText(_translate("Form", "FJSP"))
        self.StartSolve.setText(_translate("Form", "开始求解"))




class Drawing(QWidget):
    def __init__(self,parent=None):
        super(Drawing, self).__init__(parent)
        self.setWindowTitle('在窗口绘制文字')
        self.resize(300,200)

    def paintEvent(self,event):
        painter=QPainter()
        painter.begin(self)
        #自定义绘制方法
        self.drawLine(event,painter)
        painter.end()

    def drawLine(self,event,qp):

        #设置画笔的颜色
        qp.setPen(QColor(168,34,3))
        #设置字体
        qp.drawLine(5,3,14,16)

if __name__ == '__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    demo=Drawing()
    demo.show()
    sys.exit(app.exec_())
