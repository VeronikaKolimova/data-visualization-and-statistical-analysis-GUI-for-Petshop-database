import sys
import sqlite3
import traceback
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem, QComboBox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats

from ui_db_gui import Ui_MainWindow


def trace_errors_show_error(method):
    def wrapper(self, *args, **kwargs):

        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            self.show_error(f"Ошибка в {method.__name__}:\n{str(e)}\n\n{tb}")
    return wrapper


class AnalyzerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db_file = "petshop.db"
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in self.cursor.fetchall():
            self.ui.list_tables.addItem(table[0])

        self.ui.list_tables.currentTextChanged.connect(self.update_column_selector)
        self.ui.Show_Button.clicked.connect(self.show_table)
        self.ui.Add_text_btn.clicked.connect(self.add_record)
        self.ui.Del_Button.clicked.connect(self.delete_record)

        self.ui.histogram_plot_Button.clicked.connect(self.show_histogram)
        self.ui.qq_plot_Button.clicked.connect(self.show_qq_plot)
        self.ui.correlation_matrix_Button.clicked.connect(self.show_correlation_matrix)

        if self.ui.list_tables.count() > 0:
            self.update_column_selector(self.ui.list_tables.currentText())

    def show_error(self, message):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Ошибка")
        error_dialog.exec()

    @trace_errors_show_error
    def update_column_selector(self, table_name):
        self.ui.column_selector.clear()
        if not table_name:
            return

        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 1", self.conn)
        numeric_cols = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) and 'id' not in col.lower():
                numeric_cols.append(col)

        self.ui.column_selector.addItems(numeric_cols)
        self.ui.column_selector.setVisible(len(numeric_cols) > 0)

    @trace_errors_show_error
    def show_table(self, checked=None):
        table = self.ui.list_tables.currentText()
        if not table:
            return

        df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)

        self.ui.data_here.setRowCount(len(df))
        self.ui.data_here.setColumnCount(len(df.columns))
        self.ui.data_here.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                self.ui.data_here.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

    @trace_errors_show_error
    def add_record(self, checked=None):
        table = self.ui.list_tables.currentText()
        values = self.ui.lineEdit.text().strip()
        if not table or not values:
            return

        self.cursor.execute(f"PRAGMA table_info({table})")
        columns_info = self.cursor.fetchall()

        columns = [col[1] for col in columns_info if col[1].lower() != 'id']

        if len(values.split(',')) != len(columns):
            QtWidgets.QMessageBox.warning(self, "Ошибка",
                                          f"Нужно ввести {len(columns)} значений: {', '.join(columns)}")
            return

        placeholders = ','.join(['?'] * len(columns))
        columns_str = ','.join(columns)

        self.cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})",
                            values.split(','))
        self.conn.commit()
        self.show_table()
        self.ui.lineEdit.clear()

    @trace_errors_show_error
    def delete_record(self, checked=None):
        if not self.ui.data_here.currentItem():
            return

        table = self.ui.list_tables.currentText()
        row = self.ui.data_here.currentRow()
        id_value = self.ui.data_here.item(row, 0).text()
        self.cursor.execute(f"PRAGMA table_info({table})")
        id_column = self.cursor.fetchone()[1]

        self.cursor.execute(f"DELETE FROM {table} WHERE {id_column} = ?", (id_value,))
        self.conn.commit()
        self.show_table()

    @trace_errors_show_error
    def show_histogram(self, checked=None):
        if self.ui.column_selector.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Нет числовых столбцов для анализа")
            return

        table = self.ui.list_tables.currentText()
        column = self.ui.column_selector.currentText()

        df = pd.read_sql_query(f"SELECT {column} FROM {table}",
                               self.conn)
        data = pd.to_numeric(df[column],
                             errors='coerce').dropna()

        if len(data) == 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка",f"Столбец '{column}' не содержит числовых данных")
            return

        plt.figure(figsize=(10, 6))

        plt.hist(data, bins=15, density=True, alpha=0.7, color='green', edgecolor='black',
                 label='Гистограмма')

        mu, sigma = data.mean(), data.std()

        x = np.linspace(data.min(), data.max(),100)
        y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
        plt.plot(x, y, 'r-', linewidth=2,
                 label=f'Показатели нормального распределения\n(μ={mu:.2f}, σ={sigma:.2f})')

        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)

        is_normal = abs(skewness) < 1 and abs(kurtosis) < 1

        normality_status = "✓ Близко к нормальному" if is_normal else "✗ Отклоняется от нормального"
        plt.axvline(mu, color='k', linestyle='--', linewidth=1,
                    label=f'Среднее: {mu:.2f}\nАсимметрия: {skewness:.2f}\nЭксцесс: {kurtosis:.2f}\n{normality_status}')

        plt.title(f"Гистограмма: {column}", fontsize=14, fontweight='bold')
        plt.xlabel(f"Значения ({column})", fontsize=12)
        plt.ylabel("Плотность вероятности", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show(block=False)

    @trace_errors_show_error
    def show_qq_plot(self, checked=None):
        table = self.ui.list_tables.currentText()
        if not table:
            return

        df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
        numeric_df = df.select_dtypes(include='number')
        numeric_cols = [col for col in numeric_df.columns if
                        'id' not in col.lower()]

        if len(numeric_cols) == 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Нет числовых столбцов для анализа")
            return

        if len(numeric_cols) == 1:
            fig, ax = plt.subplots(figsize=(5, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(1, len(numeric_cols), figsize=(5 * len(numeric_cols), 4))

        for col, ax in zip(numeric_cols, axes):
            data_clean = df[col].dropna()
            shapiro_test = stats.shapiro(data_clean)
            p_value = shapiro_test.pvalue
            skewness = stats.skew(data_clean)
            kurtosis = stats.kurtosis(data_clean)
            is_normal = p_value > 0.05
            normality_status = "✓ Нормальное" if is_normal else "✗ Не нормальное"

            stats.probplot(data_clean, dist="norm", plot=ax)
            stats.probplot(data_clean, dist="norm", plot=ax)
            ax.set_ylabel("Выборочные квантили")
            ax.set_xlabel("Теоретические квантили")

            stats_text = (f"Тест Шапиро-Уилка:\n"  
                          f"p-value = {p_value:.4f}\n"
                          f"Статус: {normality_status}\n"
                          f"Асимметрия: {skewness:.2f}\n"
                          f"Эксцесс: {kurtosis:.2f}")
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title(f"Q-Q Plot: {col}", fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.show(block=False)

    @trace_errors_show_error
    def show_correlation_matrix(self, checked=None):
        table = self.ui.list_tables.currentText()
        if not table:
            return

        df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)

        numeric_df = df.select_dtypes(include='number')
        numeric_cols = [col for col in numeric_df.columns if 'id' not in col.lower()]
        numeric_df = numeric_df[numeric_cols]

        if numeric_df.shape[1] < 2:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Нужно как минимум 2 числовых столбца")
            return

        plt.figure(figsize=(8, 6))
        sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap='coolwarm')
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.show(block=False)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = AnalyzerApp()
    window.show()
    sys.exit(app.exec())