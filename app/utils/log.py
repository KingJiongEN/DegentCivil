import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import shutil
import traceback
import pandas as pd


class LogManager:
    log_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    prompt_res_log = os.path.join(log_directory, 'prompt_res')
    char_attrs_log = os.path.join(log_directory, 'char_attrs.csv')
    app_log_file_path = os.path.join(log_directory, 'app.log')
    error_log_file_path = os.path.join(log_directory, 'error.log')
    record_start_marker = "@@RECORD_START@@"
    logger = None
    

    @staticmethod
    def setup_logger():
        if LogManager.logger is not None:
            return  # Logger 已被设置

        shutil.rmtree(LogManager.log_directory, ignore_errors=True) # clean the log directory
        os.makedirs(LogManager.log_directory, exist_ok=True)
        os.makedirs(LogManager.prompt_res_log,exist_ok=True)

        LogManager.logger = logging.getLogger('app_logger')
        LogManager.logger.setLevel(logging.DEBUG)

        app_handler = RotatingFileHandler(LogManager.app_log_file_path, maxBytes=10000000, backupCount=5,
                                          encoding='utf-8')
        app_handler.setLevel(logging.INFO)

        error_handler = RotatingFileHandler(LogManager.error_log_file_path, maxBytes=10000000, backupCount=5,
                                            encoding='utf-8')
        error_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        app_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        LogManager.logger.addHandler(app_handler)
        LogManager.logger.addHandler(error_handler)

    @staticmethod
    def log_debug(msg, *args, **kwargs):
        if LogManager.logger is None:
            LogManager.setup_logger()

        LogManager.logger.debug(msg, *args, **kwargs)
        print(f"\nDEBUG: {msg}", *args, **kwargs)

    @staticmethod
    def log_info(msg, *args, **kwargs):
        if LogManager.logger is None:
            LogManager.setup_logger()

        LogManager.logger.info(msg, *args, **kwargs)
        print(f"\nINFO: {msg}", *args, **kwargs)

    @staticmethod
    def log_warning(msg, *args, **kwargs):
        if LogManager.logger is None:
            LogManager.setup_logger()

        LogManager.logger.warning(msg, *args, **kwargs)
        print(f"\nWARNING: {msg}", *args, **kwargs)

    @staticmethod
    def log_error(msg, *args, **kwargs):
        if LogManager.logger is None:
            LogManager.setup_logger()

        LogManager.logger.error(msg, *args, **kwargs)
        print(f"\nERROR: {msg}", *args, **kwargs)

    @staticmethod
    def log_critical(msg, *args, **kwargs):
        if LogManager.logger is None:
            LogManager.setup_logger()

        LogManager.logger.critical(msg, *args, **kwargs)
        print(f"\nCRITICAL: {msg}", *args, **kwargs)

    @staticmethod
    def log_character(character_name, content):
        log_file_path = os.path.join(LogManager.prompt_res_log,f"{character_name}.log")
        with open(log_file_path, 'a', encoding='utf8') as log_file:
            log_file.write(content + "\n")

    @staticmethod
    def log_character_with_time(character_name, content):
        if LogManager.logger is None:
            LogManager.setup_logger()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content_with_time = f"\n\n{LogManager.record_start_marker}\n{current_time}\n{content}"
        LogManager.log_character(character_name, content_with_time)

    @staticmethod
    def log_char_attr_with_time(character_name, attr_dict:dict):
        if LogManager.logger is None:
            LogManager.setup_logger()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attr_dict.update({'realtime': current_time})
        for att in attr_dict:
            if type(attr_dict[att]) == float:
                attr_dict[att] = round(attr_dict[att], 4)
            if hasattr(attr_dict[att], 'serialize'):
                attr_dict[att] = attr_dict[att].serialize()
            else:
                attr_dict[att] = str(attr_dict[att])
        # log_file_path = os.path.join(LogManager.char_attrs_log, f"{character_name}_Attr.csv")
        log_file_path = LogManager.char_attrs_log
        df = pd.read_csv(log_file_path) if os.path.exists(log_file_path) else pd.DataFrame(columns=list(attr_dict.keys()))
        df = df[-10000000:]
        try:
            df = pd.concat([df, pd.DataFrame([attr_dict])], ignore_index=True)
        except:
            traceback.print_exc()
            __import__('ipdb').set_trace()
        df.to_csv(log_file_path, index=False)