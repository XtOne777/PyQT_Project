import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class Product(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products.ui', self)
        self.data = []
        self.connection = sqlite3.connect('main.sqlite')
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()
        self.pushButton.clicked.connect(self.clicked_t)
        self.select_data()

    def select_data(self):
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)'])
        for i, row in enumerate(self.res):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

    def clicked_t(self):
        for i in self.res:
            try:
                if str(i[0]) == self.lineEdit.text():
                    self.data.append((str(i[0]), str(i[1]), str(i[2]),
                                      str(int(self.lineEdit_3.text())), str(self.lineEdit_2.text() + '%'),
                                      str(int(int(self.lineEdit_2.text()) * 0.01 *
                                              int(self.lineEdit_3.text()) * i[2]))))
                    self.excep.setText(i[1] + ' добавлен успешно!')
            except Exception as e:
                print(e)
                self.excep.setText('Неправильный формат ввода!')

    def return_data(self):
        return self.data


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mew = Product()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect('main.sqlite')
        self.Button_add.clicked.connect(self.select_data)
        self.button_reload.clicked.connect(self.load)

    def select_data(self):
        self.mew.show()

    def load(self):
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)', 'Количество', 'Скидка', 'Всего'])
        a = self.mew.return_data()
        for i, row in enumerate(a):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
