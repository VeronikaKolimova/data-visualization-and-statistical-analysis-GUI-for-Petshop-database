# ui_db_gui.py
from PyQt6 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)

        self.list_tables = QtWidgets.QComboBox(parent=self.centralwidget)
        self.list_tables.setGeometry(QtCore.QRect(80, 20, 86, 26))

        self.Show_Button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Show_Button.setGeometry(QtCore.QRect(190, 20, 101, 26))
        self.Show_Button.setText("Show")

        self.data_here = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.data_here.setGeometry(QtCore.QRect(70, 140, 631, 361))

        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(80, 60, 113, 26))

        self.Add_text_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Add_text_btn.setGeometry(QtCore.QRect(220, 60, 88, 26))
        self.Add_text_btn.setText("Add")

        self.Del_Button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Del_Button.setGeometry(QtCore.QRect(80, 110, 88, 26))
        self.Del_Button.setText("Delete")

        self.column_selector = QtWidgets.QComboBox(parent=self.centralwidget)
        self.column_selector.setGeometry(QtCore.QRect(500, 20, 140, 26))
        self.column_selector.hide()

        self.histogram_plot_Button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.histogram_plot_Button.setGeometry(QtCore.QRect(350, 20, 120, 26))
        self.histogram_plot_Button.setText("Histogram")

        self.qq_plot_Button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.qq_plot_Button.setGeometry(QtCore.QRect(350, 60, 160, 26))
        self.qq_plot_Button.setText("Q-Q Plot")

        self.correlation_matrix_Button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.correlation_matrix_Button.setGeometry(QtCore.QRect(350, 100, 180, 26))
        self.correlation_matrix_Button.setText("Correlation Matrix")

        MainWindow.setCentralWidget(self.centralwidget)

