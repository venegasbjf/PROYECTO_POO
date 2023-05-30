from __future__ import annotations

import logging

class Logger:

    def __init__(self, log_file: str) -> None:
        self.__logger = self.__create_logger(log_file)

    def __create_logger(self, log_file: str) -> logging.Logger:

        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)

        return logger
    
    def info(self, message: str) -> None:
        self.__logger.info(message)
        
    def warning(self, message: str) -> None:
        self.__logger.warning(message)
        
    def error(self, message: str) -> None:
        self.__logger.error(message)
        
    def critical(self, message: str) -> None:
        self.__logger.critical(message)

logger = Logger("app.log")