from .config_common import CommonConfig


class ProductionConfig(CommonConfig):
    server_host = '0.0.0.0'
    server_port = 8001
    update_interval = 10
