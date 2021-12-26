import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

data = []


class ProductDel(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products_del.ui', self)
        self.pushButton.clicked.connect(self.deleting)
        self.data = data

    def get_info(self, info):
        self.data = info
        self.table.setColumnCount(6)  # количество столбцов
        self.table.setRowCount(0)  # строки
        for i, row in enumerate(self.data):
            self.table.setRowCount(self.table.rowCount() + 1)  # количество строк
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))  # вводим данные
        # имена столбцов
        self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)', 'Количество', 'Скидка', 'Всего'])

    def deleting(self):
        answer = QMessageBox()
        answer.setWindowTitle('Подтверждение действий')
        answer.setText('Вы подтверждаете свои дейтсвия?')
        answer.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        flag = answer.exec()
        if flag == QMessageBox.Ok:
            self.data.__delitem__(int(self.lineEdit.text()) - 1)
        self.close()


class Product(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products.ui', self)  # Вызов .ui окна
        self.data = data  # Список с покупками(имя товара, id и тд.)
        # Вызов базы данных
        self.connection = sqlite3.connect('main.sqlite')
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()
        self.pushButton.clicked.connect(self.clicked_t)  # кнопка добавить
        self.pushButton_2.clicked.connect(self.clicked_b)  # кнопка изменить

    def edit(self):
        try:
            self.pushButton.hide()  # прячем кнопку добавить
            self.pushButton_2.show()  # показываем кнопку изменить
            self.label.setText('Номер покупки:')
            if len(self.data) > 0:  # проверка на наличие данных
                self.lineEdit.setText(str(len(self.data)))
                self.lineEdit_2.setText(self.data[-1][4][:-1])
                self.lineEdit_3.setText(str(self.data[-1][3]))
            self.table.setColumnCount(6)  # количество столбцов
            self.table.setRowCount(0)  # строки
            for i, row in enumerate(self.data):
                self.table.setRowCount(self.table.rowCount() + 1)  # количество строк
                for j, elem in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(elem)))  # вводим данные
            # имена столбцов
            self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)', 'Количество', 'Скидка', 'Всего'])
        except ValueError:
            self.excep.setText('Неправильный формат ввода!')

    def select_data(self):
        self.pushButton_2.hide()  # прячем кнопку изменить
        self.pushButton.show()  # показываем кнопку добавить
        self.label.setText('id Продукта:')
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()  # Взятие данных из бд
        # Размеры таблицы
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        # Название столбцов
        self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)'])
        # Функция вывода данных в таблицу
        for i, row in enumerate(self.res):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

    def clicked_t(self):
        for i in self.res:
            try:  # Проверка на правильный ввод данных
                if str(i[0]) == self.lineEdit.text():  # Проверка на id
                    # Вычесления и добавление в список данных
                    self.data.append((str(i[0]), str(i[1]), str(i[2]),
                                      str(int(self.lineEdit_3.text())), str(self.lineEdit_2.text() + '%'),
                                      str(int(int(self.lineEdit_2.text()) * 0.01 *
                                              int(self.lineEdit_3.text()) * i[2]))))
                    self.excep.setText(i[1] + ' добавлен успешно!')  # Вывод о успешном завершение
            except ValueError:
                self.excep.setText('Неправильный формат ввода!')

    def clicked_b(self):
        try:
            # редакция данных
            self.data[int(self.lineEdit.text()) - 1] = (self.data[int(self.lineEdit.text()) - 1][0],
                                                        self.data[int(self.lineEdit.text()) - 1][1],
                                                        self.data[int(self.lineEdit.text()) - 1][2],
                                                        self.lineEdit_3.text(),
                                                        self.lineEdit_2.text() + '%',
                                                        str(int(int(self.lineEdit_2.text()) * 0.01
                                                                * int(self.lineEdit_3.text())
                                                                * int(self.data[int(self.lineEdit.text()) - 1][2]
                                                                      ))))
            # надпись о успехе
            self.excep.setText(self.data[int(self.lineEdit.text()) - 1][1] + ' добавлен успешно!')
        except ValueError:
            self.excep.setText('Неправильный формат ввода!')

    def return_data(self):
        return self.data  # Возращаем список данных


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mew = Product()  # вызов класса с produсts.ui файл
        self.mew_2 = ProductDel()
        # Вызов .ui главного окна и базы данных
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect('main.sqlite')
        # Добавление функций к кнопкам
        self.Button_add.clicked.connect(self.select_data)
        self.Button_edit.clicked.connect(self.edit)
        self.button_reload.clicked.connect(self.load)
        self.Button_delete.clicked.connect(self.delete)

    def delete(self):
        self.mew_2.get_info(self.mew.return_data())
        self.mew_2.show()

    def edit(self):
        self.mew.edit()
        self.mew.show()  # показываем окно

    def select_data(self):
        self.mew.select_data()
        self.mew.show()  # показываем окно

    def load(self):
        # Выставляем размеры окна
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        # Название столбцов
        self.table.setHorizontalHeaderLabels(['id', 'Товар', 'Цена(1шт.)', 'Количество', 'Скидка', 'Всего'])
        # Цикл с вводом данных
        a = self.mew.return_data()  # Получаем данные о добавленных продуктах
        for i, row in enumerate(a):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
