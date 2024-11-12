import os
import logging
from logging.handlers import TimedRotatingFileHandler
from .. import app

def create_log_file(log_file_name):
    # if it does not exist then make a log folder
    if not os.path.exists(app.config['LOG_PATH']):
        os.makedirs(app.config['LOG_PATH'])

    log = logging.getLogger(log_file_name)
    log.setLevel(app.config['LOG_LEVEL'])
    loggerStreamHandler = logging.StreamHandler()
    loggerStreamHandler.setLevel(app.config['LOG_LEVEL'])

    logFormatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(filename)-'
        '16s:%(lineno)-3d %(levelname)-8s %(message)s')
    loggerStreamHandler.setFormatter(logFormatter)
    log.addHandler(loggerStreamHandler)

    loggerfileHandler = TimedRotatingFileHandler(
        filename='{0}{1}.txt'.format(app.config['LOG_PATH'],log_file_name),
        when='midnight',
        interval=1,
        backupCount=app.config['LOG_BACKUP_COUNT'])

    loggerfileHandler.suffix = '%Y%m%d.txt'
    loggerfileHandler.mode = 'a'
    loggerfileHandler.setFormatter(logFormatter)
    log.addHandler(loggerfileHandler)

    return log