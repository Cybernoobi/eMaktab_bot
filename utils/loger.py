# DON'T WORK



# import logging
# import sys
# from datetime import datetime
#
#
# def start_loging():
#     # Создание и настройка логгера
#     logger = logging.getLogger(__name__)
#     logger.setLevel(logging.INFO)
#
#     # Формат для сообщений лога
#     formatter = logging.Formatter('[%(asctime)s]: %(message)s', datefmt='%H:%M:%S')
#
#     # Создание обработчика для записи в файл с использованием текущей даты в имени файла
#     log_filename = datetime.now().strftime("%Y-%m-%d") + '.log'
#     file_handler = logging.FileHandler(r'.\logs\\' + log_filename)
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#
#     # Перенаправление стандартного вывода и вывода ошибок в файл лога
#     sys.stdout = open(log_filename, 'a')
#     sys.stderr = open(log_filename, 'a')
