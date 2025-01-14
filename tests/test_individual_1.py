#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from src.individual_1 import TrainManager, UnknownCommandError


class TestTrainManager(unittest.TestCase):
    def test_add_and_list_trains(self):
        """
        Проверяем, что поезда добавляются в список
        и упорядочиваются по времени отправления.
        """

        manager = TrainManager()

        # Добавляем три поезда с разным временем отправления.
        manager.add_train("Moscow", "100A", "09:30", "Kazan")
        manager.add_train("Sochi", "200B", "06:50", "Adler")
        manager.add_train("Tver", "300C", "06:00", "Moscow")

        # Получаем список добавленных поездов (объектов Train).
        trains = manager.list_trains()

        # Убеждаемся, что все три поезда в списке.
        self.assertEqual(len(trains), 3)

        # Проверяем порядок по времени отправления:
        # "06:00", "06:50", "09:30".
        self.assertEqual(trains[0].time_departure, "06:00")
        self.assertEqual(trains[1].time_departure, "06:50")
        self.assertEqual(trains[2].time_departure, "09:30")

    def test_select_trains(self):
        """
        Проверяем корректность выборки поездов по пункту назначения.
        """

        manager = TrainManager()
        # Добавим несколько поездов с разными пунктами назначения.
        manager.add_train("Moscow", "100A", "09:30", "Kazan")
        manager.add_train("Sochi", "200B", "06:50", "Adler")
        manager.add_train("Tver", "300C", "11:00", "Kazan")

        # Выберем поезда, идущие в Казань (Kazan).
        selected = manager.select_trains("Kazan")

        # Ожидаем 2 поезда: с №100A и №300C.
        self.assertEqual(len(selected), 2)
        # Проверим, что пункт назначения действительно "Kazan".
        for train in selected:
            self.assertEqual(train.destination, "Kazan")

        # Проверим выборку по несуществующему направлению.
        none_selected = manager.select_trains("NonExistentCity")
        self.assertEqual(len(none_selected), 0)

    def test_unknown_command_error(self):
        """
        Проверяем, что исключение UnknownCommandError
        корректно формируется и содержит верное сообщение.
        """

        with self.assertRaises(UnknownCommandError) as context:
            raise UnknownCommandError("invalid_command")

        # Проверяем содержание сообщения об ошибке.
        self.assertIn("invalid_command", str(context.exception))
        self.assertIn("Неизвестная команда", str(context.exception))


if __name__ == "__main__":
    unittest.main()
