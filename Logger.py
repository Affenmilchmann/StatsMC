from datetime import datetime as dt
from os import path as ospath, mkdir

LOG_FOLDER = ospath.join(ospath.dirname(__file__), "logs/")
API_LOG = ospath.join(LOG_FOLDER, "api_log.txt")
API_FATAL_LOG = ospath.join(LOG_FOLDER, "api_fatal_log.txt")

class Logger():
    @classmethod
    def __getTimeStamp(cls):
        return '{:%Y-%m-%d %H:%M:%S}'.format(dt.now())
    @classmethod
    def printLog(cls, text, error=False):
        if error:
            print(f"[{cls.__getTimeStamp()}] [ERROR] {text}")
        else:
            print(f"[{cls.__getTimeStamp()}] {text}")
    @classmethod
    def writeApiLog(cls, text):
        with open(API_LOG, 'a') as f:
            f.write(f"[{cls.__getTimeStamp()}] {text}\n")
    @classmethod
    def writeApiFatalLog(cls, text):
        with open(API_FATAL_LOG, 'a') as f:
            f.write(f"[{cls.__getTimeStamp()}] {text}\n")

if not ospath.exists(LOG_FOLDER):
    try:
        mkdir(LOG_FOLDER)
    except OSError as e:
        Logger.printLog(f"Creation of the directory {LOG_FOLDER} failed")
        Logger.printLog(e)
    else:
        Logger.printLog(f"Successfully created the directory {LOG_FOLDER}")
def check_file(path):
    if not ospath.exists(path):
        with open(path, 'w') as f:
            f.write("")
            Logger.printLog(f"{path} was missiog so it was created")
check_file(API_LOG)
check_file(API_FATAL_LOG)
