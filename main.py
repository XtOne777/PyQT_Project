import sqlite3
import sys
import csv
import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
# Глобальные переменные с данными о покупателе и продавце и покупками
buyer = tuple()
seller = tuple()
data = []


class ProductBD(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products_bd.ui', self)  # Загрузка .ui файла
        self.setWindowTitle('Редактирование базы данных с продуктами')  # Задаем название
        self.connection = sqlite3.connect('main.sqlite')  # Загрузка базы данных
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()  # Взятие данных из бд
        self.reload_data()  # Перезагрузка таблицы
        # Проверки на взаимодействия с кнопками/строками
        self.spinBox.valueChanged.connect(self.edit_reload)
        self.spinBox_2.valueChanged.connect(self.delete_reload)
        self.Button_edit.clicked.connect(self.edit_data)
        self.Button_delete.clicked.connect(self.delete_data)
        self.Button_add.clicked.connect(self.adding_data)

    def delete_reload(self):
        value = self.spinBox_2.value()  # Значение строчки
        # Задаём ограничения
        if value > len(self.res):
            self.spinBox_2.setValue(self.res[-1][0])
        if value == 0:
            self.spinBox_2.setValue(1)

    def adding_data(self):
        cur = self.connection.cursor()
        cur.execute(f"INSERT INTO Товары (Товар, [Цена(1шт.)])"
                    f" VALUES ('{self.lineEdit_2.text()}', {self.lineEdit_3.text()})")  # Добавляем новые данные
        self.connection.commit()  # Сохраняем
        self.reload_data()  # Перезагрузка таблицы

    def delete_data(self):
        # Потверждение действий
        answer = QMessageBox()
        answer.setWindowTitle('Подтверждение действий')
        answer.setText('Вы подтверждаете свои дейтсвия?')
        answer.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        flag = answer.exec()
        if flag == QMessageBox.Ok:
            # Удаление данных из бд
            cur = self.connection.cursor()
            cur.execute(f"DELETE FROM Товары WHERE id = {self.spinBox_2.value()}")
            self.connection.commit()
            self.reload_data()  # Перезагрузка таблицы

    def edit_data(self):
        cur = self.connection.cursor()
        cur.execute(f"UPDATE Товары SET Товар = '{self.lineEdit_5.text()}',"
                    f"[Цена(1шт.)] = {self.lineEdit_4.text()} WHERE id = {self.spinBox.value()}")  # Изменение данных
        self.connection.commit()  # Сохраняем
        self.reload_data()  # Перезагрузка таблицы

    def reload_data(self):
        self.res = self.connection.cursor().execute('SELECT * FROM Товары').fetchall()  # Берём данные из таблицы
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

    def edit_reload(self):
        value = self.spinBox.value()  # Получаем значение строки
        # Создаём ограничение значений
        if value > len(self.res):
            self.spinBox.setValue(self.res[-1][0])
        if value == 0:
            self.spinBox.setValue(1)
        # Поиск данного айди
        for i in self.res:
            if i[0] == value:
                # Изменение значений в строках
                self.lineEdit_5.setText(str(i[1]))
                self.lineEdit_4.setText(str(i[2]))
                break


class ProductDel(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products_del.ui', self)  # Загружаем .ui файл
        self.setWindowTitle('Удаление продуктов')  # Задаём название
        self.pushButton.clicked.connect(self.deleting)  # Задаём функции кнопкам
        self.data = data  # Берём данные из глобальной переменной

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
        # Потверждения действиям
        answer = QMessageBox()
        answer.setWindowTitle('Подтверждение действий')
        answer.setText('Вы подтверждаете свои дейтсвия?')
        answer.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        flag = answer.exec()
        if flag == QMessageBox.Ok:
            self.data.__delitem__(int(self.lineEdit.text()) - 1)  # Удаляем покупку
        self.close()  # Закрываем окно


class Product(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('products.ui', self)  # Вызов .ui окна
        self.setWindowTitle('Редактирование списка покупки')
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
        self.data_reload()
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
        self.data_reload()
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
        self.data_reload()
        return self.data  # Возращаем список данных

    def data_reload(self):
        self.data = data


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mew = Product()  # вызов класса с produсts.ui файл
        self.mew_2 = ProductDel()  # вызов класса с product_del.ui файл
        # Вызов .ui главного окна и базы данных
        uic.loadUi('main.ui', self)
        self.setWindowTitle('Работа со списком покупок')
        self.connection = sqlite3.connect('main.sqlite')
        self.bd_editing = ProductBD()  # вызов класса с product_bd.ui файл
        # Добавление функций к кнопкам
        self.Button_add.clicked.connect(self.select_data)
        self.Button_edit.clicked.connect(self.edit)
        self.button_reload.clicked.connect(self.load)
        self.Button_delete.clicked.connect(self.delete)
        self.Button_save.clicked.connect(self.save_data)
        self.Button_load.clicked.connect(self.load_data)
        self.Button_bd.clicked.connect(self.bd_edit)

    def bd_edit(self):
        self.bd_editing.show()  # Показываем окно

    def load(self):
        global data
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
        # Загрузка вычислений
        if data:
            b = list()  # Вспомогательная переменная
            summary = float()  # Сумма
            for i in data:
                k = int(i[2]) * int(i[3]) * float(i[4][:-1]) / 100
                summary += k
                b.append(f'{i[2]} * {i[3]} * {i[4]}')
            # Выводим вычисления покупки
            self.label_7.setText(' + '.join(b) + ' = ' + str(summary))
            self.Summary.setText(str(summary))

    def load_data(self):
        try:
            # Открываем .csv файл и задам значения глобальным переменным
            with open(QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Файлы данных (*.csv)')[0],
                      encoding='utf-8') as csvfile:
                global buyer, seller, data
                data = []
                text = csv.reader(csvfile, delimiter=';', quotechar='"')
                for i, k in enumerate(text):
                    if i == 0:
                        buyer = k
                    elif i == 2:
                        seller = k
                    elif i > 2:
                        if k:
                            data.append(k)
            # Ввод значений в строки
            self.line_number.setText(buyer[0])
            self.line_card.setText(buyer[1])
            self.line_name.setText(seller[0])
            self.line_id.setText(seller[1])
            self.load()
        except Exception as e:
            print(e)

    def save_data(self):
        try:
            # Сохраняем все данные в .csv файл
            with open(QFileDialog.getSaveFileName(self, "Save audio file",
                                                  datetime.datetime.now().strftime('%d.%m.%Y %H.%M'),
                                                  "Файлы с данными (*.csv)")[0], 'w+', encoding='utf8') as csvfile:
                text = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                text.writerows([[self.line_number.text(), self.line_card.text()],
                                [self.line_name.text(), self.line_id.text()],
                                *data])
        except Exception as e:
            print(e)

    def delete(self):
        self.mew_2.get_info(self.mew.return_data())  # Выдаём значения классу
        self.mew_2.show()  # Показываем окно

    def edit(self):
        self.mew.edit()  # Вызываем функцию редакции данных
        self.mew.show()  # показываем окно

    def select_data(self):
        self.mew.select_data()  # Вызываем функию добавления данных
        self.mew.show()  # показываем окно


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
