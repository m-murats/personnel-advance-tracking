import logging
import re

class AppLogger:
    _instance = None
    def __new__(cls, log_file: str = "system_logs.log"):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("AppLogger")
            cls._instance.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            if not cls._instance.logger.handlers:
                cls._instance.logger.addHandler(handler)
        return cls._instance

    def log_info(self, msg: str): self.logger.info(msg)
    def log_error(self, msg: str): self.logger.error(msg)

class DataValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

    @staticmethod
    def is_positive_float(value: str) -> bool:
        try:
            return float(value) > 0
        except ValueError:
            return False

class SessionManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.current_user = None
        return cls._instance
    
    def login(self, user): self.current_user = user
    def logout(self): self.current_user = None
    def get_user(self): return self.current_user