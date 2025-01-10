from .config_common import CommonConfig


class DevelopmentConfig(CommonConfig):
    server_host = 'localhost'
    server_port = 8001

    debug = True
