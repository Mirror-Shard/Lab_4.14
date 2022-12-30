#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import (
    QTableView,
    QApplication,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QFrame,
    QLabel,
    QHeaderView,
    QDateEdit,
    QTabWidget,
)
from PySide2.QtCore import (
    Signal,
)
from PySide2.QtCore import QSortFilterProxyModel, Qt, QRect
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    ForeignKey,
    insert,
    select,
    delete,
)
import sys


class DateBase:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///database2.db")
        self.engine.connect()
        metadata = MetaData()
        self.Ticket = Table(
            "Ticket",
            metadata,
            Column("Код_билета", Text(), nullable=False),
            Column("Пункт_отправления", Text(), nullable=False),
            Column("Пункт_прибытия", Text(), nullable=False),
            Column("Время_в_пути", Text(), nullable=False),
        )

        self.Passenger = Table(
            "Passenger",
            metadata,
            Column("Id_рейса", Text(), primary_key=True),
            Column("ФИО", Text(), nullable=False),
            Column("Дата_рождения", Text(), nullable=False),
            Column("Номер_и_серия_паспорта", Text(), nullable=False),
        )

        self.Driver = Table(
            "Driver",
            metadata,
            Column("Id_рейса", ForeignKey(self.Passenger.c.Id_рейса)),
            Column("Имя_водителя", ForeignKey(self.Ticket.c.Код_билета)),
            Column("Дата_отправления", Text(), nullable=False),
            Column("Тип_транспорта", Text(), nullable=False),
        )
        metadata.create_all(self.engine)
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("database2.db")
        if not db.open():
            return False
        self.conn = self.engine.connect()

        if not self.table_is_empty():
            ins = insert(self.Ticket)
            r = self.conn.execute(
                ins,
                Код_билета="8d2cbab4e5ec03c99215bb6cbf619348",
                Пункт_отправления="Москва",
                Пункт_прибытия="Самара",
                Время_в_пути="3:50",
            )
            r = self.conn.execute(
                ins,
                Код_билета="d7f1748981fe83e7e33d177e7ecd8e70",
                Пункт_отправления="Самара",
                Пункт_прибытия="Вашингтон",
                Время_в_пути="8:15",
            )
            r = self.conn.execute(
                ins,
                Код_билета="adbbc672f485dc806ca03d9e7287d192",
                Пункт_отправления="Тольятти",
                Пункт_прибытия="Уфа",
                Время_в_пути="2:45",
            )
            ins = insert(self.Passenger)
            r = self.conn.execute(
                ins,
                Id_рейса="0000000021",
                ФИО="Абрамов Андрей",
                Дата_рождения="09.09.2000",
                Номер_и_серия_паспорта="0719568675",
            )
            r = self.conn.execute(
                ins,
                Id_рейса="0000000127",
                ФИО="Орлов Иван",
                Дата_рождения="08.08.2001",
                Номер_и_серия_паспорта="0399568675",
            )
            r = self.conn.execute(
                ins,
                Id_рейса="0000001439",
                ФИО="Горностай Яна",
                Дата_рождения="07.07.2002",
                Номер_и_серия_паспорта="1999568675",
            )
            ins = insert(self.Driver)
            r = self.conn.execute(
                ins,
                Id_рейса="0000000021",
                Имя_водителя="Ахмед",
                Дата_отправления="29.12.2022",
                Тип_транспорта="Поезд",
            )
            r = self.conn.execute(
                ins,
                Id_рейса="0000000127",
                Имя_водителя="Абдул-Хамид",
                Дата_отправления="30.12.2022",
                Тип_транспорта="Самолёт",
            )
            r = self.conn.execute(
                ins,
                Id_рейса="0000001439",
                Имя_водителя="Шамсудин",
                Дата_отправления="1.12.2023",
                Тип_транспорта="Автобус",
            )

    def table_is_empty(self):
        data = self.Ticket.select()
        table_data = self.conn.execute(data)
        return table_data.fetchall()


class TableView:
    tabBarClicked = Signal(int)

    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.SetupUI()
        self.current_tab = "Ticket"
        self.tab_id = "Код_билета"

    def SetupUI(self):
        self.parent.setGeometry(400, 500, 1000, 650)
        self.parent.setWindowTitle("Продажа билетов")
        self.main_conteiner = QGridLayout()
        self.frame1 = QFrame()
        self.frame2 = QFrame()
        self.frame2.setVisible(False)
        self.main_conteiner.addWidget(self.frame1, 0, 0)
        self.main_conteiner.addWidget(self.frame2, 0, 0)
        self.frame1.setStyleSheet(
            """
            font: bold;
            font-size: 15px;
            """
        )
        self.frame2.setStyleSheet(
            """
            font: bold;
            font-size: 15px;
            """
        )
        self.table_view = QTableView()
        self.table_view.setModel(self.tableTicket())
        self.table_view2 = QTableView()
        self.table_view2.setModel(self.tablePassenger())
        self.table_view3 = QTableView()
        self.table_view3.setModel(self.tableDriver())
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.layout_main = QGridLayout(self.frame1)
        self.layh = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить")
        self.layh.addWidget(self.btn_add)
        self.layh.addWidget(self.btn_del)
        self.tab_conteiner = QTabWidget()
        self.tab_conteiner.setTabShape(QTabWidget.Triangular)
        self.tab_conteiner.addTab(self.table_view, "Билеты")
        self.tab_conteiner.addTab(self.table_view2, "Пассажиры")
        self.tab_conteiner.addTab(self.table_view3, "Водители")
        self.layout_main.addWidget(self.tab_conteiner, 0, 0)
        self.layout_main.addLayout(self.layh, 1, 0)
        self.parent.setLayout(self.main_conteiner)
        self.btn_del.clicked.connect(self.delete)
        self.btn_add.clicked.connect(self.add)
        self.layout_grid = QGridLayout(self.frame2)
        self.btn_add2 = QPushButton("Добавить данные")
        self.btn_add2.setFixedWidth(300)
        self.btn_otmena = QPushButton("Отмена")
        self.line_name = QLineEdit()
        self.name = QLabel("ФИО: ")
        self.doc_num_line = QLineEdit()
        self.doc_num = QLabel("Id рейса: ")
        self.color_line = QLineEdit()
        self.color = QLabel("Время_в_пути: ")
        self.dateb_line = QDateEdit()
        self.dateb_line.setCalendarPopup(True)
        self.dateb_line.setTimeSpec(Qt.LocalTime)
        self.dateb_line.setGeometry(QRect(220, 31, 133, 20))
        self.dateb = QLabel("Дата рождения: ")
        self.line_pasport = QLineEdit()
        self.pasport = QLabel("Номер и серия паспорта: ")
        self.Код_билета_line = QLineEdit()
        self.Код_билета = QLabel("Код_билета: ")
        self.marka_line = QLineEdit()
        self.marka = QLabel("Пункт_отправления: ")
        self.model_line = QLineEdit()
        self.models = QLabel("Пункт_прибытия: ")
        self.Driver_reg = QLabel("Дата отправления: ")
        self.Driver_reg_line = QDateEdit()
        self.Driver_reg_line.setCalendarPopup(True)
        self.Driver_reg_line.setTimeSpec(Qt.LocalTime)
        self.Driver_reg_line.setGeometry(QRect(220, 31, 133, 20))
        self.cate_line = QLineEdit()
        self.cate = QLabel("Код транспорта: ")
        self.layout_grid.addWidget(self.line_name, 0, 1)
        self.layout_grid.addWidget(self.name, 0, 0)
        self.layout_grid.addWidget(self.doc_num, 1, 0)
        self.layout_grid.addWidget(self.doc_num_line, 1, 1)
        self.layout_grid.addWidget(self.dateb, 2, 0)
        self.layout_grid.addWidget(self.dateb_line, 2, 1)
        self.layout_grid.addWidget(self.marka_line, 3, 1)
        self.layout_grid.addWidget(self.marka, 3, 0)
        self.layout_grid.addWidget(self.model_line, 4, 1)
        self.layout_grid.addWidget(self.models, 4, 0)
        self.layout_grid.addWidget(self.line_pasport, 5, 1)
        self.layout_grid.addWidget(self.pasport, 5, 0)
        self.layout_grid.addWidget(self.Код_билета_line, 6, 1)
        self.layout_grid.addWidget(self.Код_билета, 6, 0)
        self.layout_grid.addWidget(self.color_line, 7, 1)
        self.layout_grid.addWidget(self.color, 7, 0)
        self.layout_grid.addWidget(self.Driver_reg_line, 8, 1)
        self.layout_grid.addWidget(self.Driver_reg, 8, 0)
        self.layout_grid.addWidget(self.cate, 9, 0)
        self.layout_grid.addWidget(self.cate_line, 9, 1)
        self.layout_grid.addWidget(self.btn_add2, 10, 1)
        self.layout_grid.addWidget(self.btn_otmena, 10, 0)
        self.btn_otmena.clicked.connect(self.back)
        self.btn_add2.clicked.connect(self.add_data)
        self.tab_conteiner.tabBarClicked.connect(self.handle_tabbar_clicked)

    def tableTicket(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Ticket.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Ticket"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tablePassenger(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Passenger.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Passenger"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tableDriver(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Driver.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Driver"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def add(self):
        self.frame1.setVisible(False)
        self.frame2.setVisible(True)

    def back(self):
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def update(self):
        self.table_view.setModel(self.tableTicket())
        self.table_view2.setModel(self.tablePassenger())
        self.table_view3.setModel(self.tableDriver())

    def add_data(self):
        ins = insert(self.db.Ticket)
        r = self.db.conn.execute(
            ins,
            Код_билета=self.Код_билета_line.text(),
            Пункт_отправления=self.marka_line.text(),
            Пункт_прибытия=self.model_line.text(),
            Время_в_пути=self.color_line.text(),
        )
        ins = insert(self.db.Passenger)
        r = self.db.conn.execute(
            ins,
            Id_рейса=self.doc_num_line.text(),
            ФИО=self.line_name.text(),
            Дата_рождения=self.dateb_line.text(),
            Номер_и_серия_паспорта=self.line_pasport.text(),
        )
        ins = insert(self.db.Driver)
        r = self.db.conn.execute(
            ins,
            Id_рейса=self.doc_num_line.text(),
            Код_билета=self.Код_билета_line.text(),
            Дата_отправления=self.Driver_reg_line.text(),
            Тип_транспорта=self.cate_line.text(),
        )
        self.update()
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def cell_click(self):
        if self.current_tab == "Ticket":
            return self.table_view.model().data(self.table_view.currentIndex())
        if self.current_tab == "Driver":
            return self.table_view3.model().data(self.table_view3.currentIndex())
        if self.current_tab == "Passenger":
            return self.table_view2.model().data(self.table_view2.currentIndex())

    def delete(self):
        if self.current_tab == "Ticket":
            del_item = delete(self.db.Ticket).where(
                self.db.Ticket.c.Код_билета.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Driver":
            del_item = delete(self.db.Driver).where(
                self.db.Driver.c.Id_рейса.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Passenger":
            del_item = delete(self.db.Passenger).where(
                self.db.Passenger.c.Id_рейса.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        self.update()

    def handle_tabbar_clicked(self, index):
        if index == 0:
            self.current_tab = "Ticket"
            self.tab_id = "Код_билета"
        elif index == 1:
            self.current_tab = "Passenger"
            self.tab_id = "Id_рейса"
        else:
            self.tab_id = "Id_рейса"
            self.current_tab = "Driver"


class MainWindow(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        my_datebase = DateBase()
        self.main_view = TableView(self, my_datebase)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
