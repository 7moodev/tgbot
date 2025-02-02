import logging


class LogService:
    def __init__(self, name: str = "DEFAULT"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s]:[%(name)s] - %(message)s"
        )

        self.file_handler = logging.FileHandler("logs/tgbot.log")
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)

    def log(self, message: str, *args):
        message = message + " " + " ".join(map(str, args))
        self.logger.debug(message.strip())
        print(message)

    def error(self, message: str, *args):
        message = message + " " + " ".join(map(str, args))
        self.logger.error(message.strip())
        print(message)


if __name__ == "__main__":
    logger = LogService()
    logger.log("test", "another", 1)
