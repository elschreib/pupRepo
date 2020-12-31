from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd


class FileOpenTab(QtWidgets.QWidget):
    headersChanged = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(FileOpenTab, self).__init__(parent)

        excel_load_button = QtWidgets.QPushButton("Open Excel File", clicked=self.load_file)
        self.excel_table = QtWidgets.QTableWidget()

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(excel_load_button)
        lay.addWidget(self.excel_table)

    @QtCore.pyqtSlot()
    def load_file(self):
        filter_excel_only = "Excel Files (*.xlsx)"
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Excel File", "", filter_excel_only
        )
        if filename:
            df = pd.read_excel(filename, na_filter=False)
            self.fill_table(df)

    def fill_table(self, dataframe):
        row_count, column_count = dataframe.shape
        self.excel_table.setColumnCount(column_count)
        self.excel_table.setRowCount(row_count)
        headers = list(dataframe.columns)
        self.excel_table.setHorizontalHeaderLabels(headers)
        self.headersChanged.emit(headers)


class RowRemoveRulesTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RowRemoveRulesTab, self).__init__(parent)

        self.rule_select = QtWidgets.QComboBox()
        group_box = QtWidgets.QGroupBox("Rule 1:")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.rule_select)
        group_box.setLayout(vbox)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(group_box)

    @QtCore.pyqtSlot(list)
    def update_items(self, items):
        self.rule_select.clear()
        self.rule_select.addItems(items)


class BOMAppWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(BOMAppWindow, self).__init__(parent)

        file_open_tab = FileOpenTab()
        row_remove_rules_tab = RowRemoveRulesTab()

        file_open_tab.headersChanged.connect(row_remove_rules_tab.update_items)

        mainTabWidget = QtWidgets.QTabWidget()
        mainTabWidget.addTab(file_open_tab, "File Open")
        mainTabWidget.addTab(row_remove_rules_tab, "Row Delete Rules")

        self.setCentralWidget(mainTabWidget)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = BOMAppWindow()
    w.show()
    sys.exit(app.exec_())