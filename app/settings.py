import os
from sys import modules

self = modules[__name__]

# prefer environment variables for database settings
env_names = {
    'host': '13.55.96.122',
    'port': '3306',
    'user': 'dev',
    'password': 'Pandai_dev_123',
    'database_name': 'game',
}

for setting_name, env_name in env_names.items():
    setattr(self, setting_name, env_name)
    # if env_name:
        # print('Setting %s with environment variable %s' % (setting_name,
        #                                                    env_name))
        # setattr(self, setting_name, os.environ[env_name])
    # else:
    #     raise EnvironmentError("You must send additional environment variables to this app from docker-config.",env_name, setting_name)


self.db_connection_string = f"mysql+pymysql://{env_names['user']}:{env_names['password']}@{env_names['host']}:{env_names['port']}/{env_names['database_name']}"
# set up the database connection string
# self.db_connection_string = ('mysql+pymysql://%s:%s@%s:%s/%s' %
#                              (self.user, self.password,
#                               self.host, self.port,
#                               self.database_name))

# for setting_name, env_name in env_names.items():
#     if env_name in os.environ:
#         print('Setting %s with environment variable %s' % (setting_name,
#                                                            env_name))
#         setattr(self, setting_name, os.environ[env_name])
#     else:
#         raise EnvironmentError("You must send additional environment variables to this app from docker-config.")