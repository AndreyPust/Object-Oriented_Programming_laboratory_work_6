#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List


class UnknownCommandError(Exception):
    """
    Класс пользовательского исключения в случае,
    если введенная команда является недопустимой.
    Сообщения об этой ошибке записываются в журнал (лог-файл) "trains.log".
    """

    def __init__(self, command: str, message: str = "Неизвестная команда") -> None:
        """
        Конструктор класса пользовательского исключения.
        При создании экземпляра исключения возможна запись в лог
        для сохранения информации об ошибочной команде.

        :param command: Неверная команда;
        :param message: Сообщение об ошибке.
        """
        self.command = command
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """
        Метод вывода сообщения об ошибке (магический метод).

        :return: Неверная команда и сообщение об ошибке.
        """
        return f"{self.command} -> {self.message}"


@dataclass
class Train:
    """
    Датакласс, описывающий информацию о поезде.
    """

    departure_point: str
    number_train: str
    time_departure: str
    destination: str


class TrainManager:
    """
    Класс для управления списком поездов. Предоставляет методы для:
    - добавления поезда (add_train),
    - отображения всех поездов (list_trains),
    - выборки поездов по пункту назначения (select_trains),
    - загрузки поездов из XML (load_from_xml),
    - сохранения поездов в XML (save_to_xml).

    Все основные действия (добавление, загрузка, сохранение) сопровождаются записью
    в журнал (лог-файл) "trains.log".
    """

    def __init__(self) -> None:
        """
        Инициализировать пустой список поездов.
        """
        self.trains: List[Train] = field(default_factory=list)
        # Прямое присвоение, поскольку dataclasses.field() нельзя просто так
        # использовать внутри __init__ без дополнительных приёмов:
        self.trains = []

    def add_train(self, departure_point: str, number_train: str, time_departure: str, destination: str) -> None:
        """
        Добавить информацию о поезде в список.
        Добавленный поезд — это объект dataclass Train:
          departure_point, number_train, time_departure, destination.

        После добавления список поездов упорядочивается по времени отправления.

        :param departure_point: Пункт отправления;
        :param number_train: Номер поезда;
        :param time_departure: Время отправления;
        :param destination: Пункт назначения.

        После успешного добавления поезда информация вносится в лог-файл.
        """

        new_train = Train(
            departure_point=departure_point,
            number_train=number_train,
            time_departure=time_departure,
            destination=destination,
        )
        self.trains.append(new_train)
        self.trains.sort(key=lambda t: t.time_departure)
        logging.info(
            f"Добавлен поезд: пункт отправления={departure_point}, "
            f"№={number_train}, время={time_departure}, "
            f"пункт назначения={destination}"
        )

    def list_trains(self) -> List[Train]:
        """
        Вернуть текущий список поездов.

        :return: Список поездов.
        """
        return self.trains

    def select_trains(self, point_user: str) -> List[Train]:
        """
        Выбрать поезда, пункт назначения которых совпадает с point_user.
        Результат выборки логгируется (указывается, сколько найдено поездов).

        :param point_user: Пункт назначения (введенный пользователем).
        :return: Список таких поездов (может быть пустым).
        """
        point_user_lower = point_user.lower()
        selected = [train for train in self.trains if train.destination.lower() == point_user_lower]
        logging.info(
            f"Выполнен поиск поездов по пункту назначения='{point_user}'. " f"Найдено {len(selected)} поезд(а)."
        )
        return selected

    def load_from_xml(self, filename: str) -> None:
        """
        Загрузить список поездов из указанного файла в формате XML.
        Если файл отсутствует, список остаётся пустым или прежним.
        При успешной загрузке записывается соответствующее сообщение в лог.
        Если файл не существует, в лог также добавляется предупреждение.

        :param filename: Имя файла для загрузки.
        """
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                xml_data = f.read()

            parser = ET.XMLParser(encoding="utf-8")
            root = ET.fromstring(xml_data, parser=parser)

            self.trains = []
            for train_element in root.findall("train"):
                dp_el = train_element.find("departure_point")
                nt_el = train_element.find("number_train")
                td_el = train_element.find("time_departure")
                ds_el = train_element.find("destination")

                if not (dp_el and nt_el and td_el and ds_el):
                    continue

                new_train = Train(
                    departure_point=dp_el.text if dp_el.text else "",
                    number_train=nt_el.text if nt_el.text else "",
                    time_departure=td_el.text if td_el.text else "",
                    destination=ds_el.text if ds_el.text else "",
                )
                self.trains.append(new_train)

            logging.info(f"Данные успешно загружены из файла: {filename}.")
        else:
            logging.warning(f"Файл {filename} не найден. Загрузка не выполнена.")

    def save_to_xml(self, filename: str) -> None:
        """
        Сохранить текущий список поездов в указанный файл в формате XML.
        Если файл отсутствует, создается новый с таким же именем.
        При успешном сохранении выполняется запись в лог-файл.

        :param filename: Имя файла для сохранения.
        """
        # Если расширение не .xml, то добавим.
        if not filename.endswith(".xml"):
            filename += ".xml"

        root = ET.Element("trains")
        for train in self.trains:
            train_el = ET.SubElement(root, "train")

            dp_el = ET.SubElement(train_el, "departure_point")
            dp_el.text = train.departure_point

            nt_el = ET.SubElement(train_el, "number_train")
            nt_el.text = train.number_train

            td_el = ET.SubElement(train_el, "time_departure")
            td_el.text = train.time_departure

            ds_el = ET.SubElement(train_el, "destination")
            ds_el.text = train.destination

        tree = ET.ElementTree(root)
        with open(filename, "wb") as fout:
            tree.write(fout, encoding="utf-8", xml_declaration=True)

        logging.info(f"Данные сохранены в файл: {filename}.")


def print_trains(trains: List[Train]) -> None:
    """
    Напечатать таблицу поездов в табличном формате.
    Если список пуст, выводится сообщение о пустом списке.

    :param trains: Список поездов.
    """

    if not trains:
        print("Список поездов пуст или ничего не найдено.")
        return

    line = "+-{}-+-{}-+-{}-+-{}-+-{}-+".format("-" * 4, "-" * 20, "-" * 13, "-" * 18, "-" * 20)
    print(line)
    print(
        "| {:^4} | {:^20} | {:^13} | {:^18} | {:^20} |".format(
            "№", "Пункт отправления", "№ поезда", "Время отправления", "Пункт назначения"
        )
    )
    print(line)
    for idx, train in enumerate(trains, 1):
        print(
            "| {:>4} | {:<20} | {:<13} | {:>18} | {:<20} |".format(
                idx,
                train.departure_point,
                train.number_train,
                train.time_departure,
                train.destination,
            )
        )
        print(line)


def main() -> None:
    """
    Главная функция, организующая цикл взаимодействия с пользователем.
    Также решается проблема `теневых имен` (одинаковые имена в основном коде и методах).
    Все введённые пользователем команды, а также возникшие ошибки,
    регистрируются в лог-файле "trains.log".
    """

    logging.basicConfig(
        filename="trains.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    manager = TrainManager()
    logging.info("Программа запущена.")

    while True:
        try:
            command = input(">>> ").strip().lower()
            logging.info(f"Введена команда: '{command}'")

            if command == "exit":
                logging.info("Программа завершена по команде 'exit'.")
                print("Программа завершена.")
                break

            elif command == "add":
                departure_point = input("Пункт отправления? ")
                number_train = input("Номер поезда? ")
                time_departure = input("Время отправления? ")
                destination = input("Пункт назначения? ")
                manager.add_train(departure_point, number_train, time_departure, destination)
                print("Поезд добавлен.")

            elif command == "list":
                trains_list = manager.list_trains()
                print_trains(trains_list)
                logging.info(f"Выведен список из {len(trains_list)} поезд(ов).")

            elif command.startswith("select "):
                parts = command.split(maxsplit=1)
                point_user = parts[1]
                selected = manager.select_trains(point_user)
                print_trains(selected)

            elif command.startswith("load "):
                parts = command.split(maxsplit=1)
                filename = parts[1]
                # Теперь грузим из XML.
                manager.load_from_xml(filename)
                print(f"Данные загружены из файла {filename}.")

            elif command.startswith("save "):
                parts = command.split(maxsplit=1)
                filename = parts[1]
                # Теперь сохраняем в XML.
                manager.save_to_xml(filename)
                print(f"Данные сохранены в файл {filename}.")

            elif command == "help":
                print("Список доступных команд:")
                print("add  - добавить поезд;")
                print("list - вывести список всех поездов;")
                print("select <пункт_назначения> - вывести поезда по пункту назначения;")
                print("load <имя_файла> - загрузить данные из файла XML;")
                print("save <имя_файла> - сохранить данные в файл XML;")
                print("help - показать справку;")
                print("exit - завершить работу.")

            else:
                raise UnknownCommandError(command)

        except Exception as exc:
            logging.error(f"Произошла ошибка: {exc}")
            print(f"Ошибка: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
