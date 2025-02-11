import logging


class Log:
    def __init__(self):
        self.logger = logging.getLogger('logger')
        self.logger.setLevel(logging.DEBUG)

        self.file_handler = logging.FileHandler('run.log')
        self.file_handler.setLevel(logging.DEBUG)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.console_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)