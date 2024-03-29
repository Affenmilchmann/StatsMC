from os import path as ospath, mkdir
from json import dump
from ..Logger import Logger

from discord.colour import Colour

ROOT_DIR = ospath.join(ospath.dirname(__file__), "..", "..", "..")

DATA_FOLDER = ospath.join(ROOT_DIR, "data/")
STAT_DATA_FOLDER = ospath.join(ROOT_DIR, "statistics/")
WEEK_NUMBER_FILE = ospath.join(STAT_DATA_FOLDER, "week_number.json")
def check_dir(dir: str):
    if not ospath.exists(dir):
        try:
            mkdir(dir)
        except OSError as e:
            Logger.printLog(f"Creation of the directory {dir} failed")
            Logger.printLog(e)
        else:
            Logger.printLog(f"Successfully created the directory {dir} ")
check_dir(DATA_FOLDER)
check_dir(STAT_DATA_FOLDER)
if not ospath.exists(WEEK_NUMBER_FILE):
    with open(WEEK_NUMBER_FILE, 'w') as f:
        dump(0, f)
        Logger.printLog(f"{WEEK_NUMBER_FILE} was missiog so it was created")

BOT_NAME = "StatsMC"
prefix = "st!"
default_embeds_colour = Colour.green()
API_PATH = "/mcstats/all_players"
DEFAULT_PORT = "11236"
TIME_OUT = 5 #seconds

LANGS = {
    "russian" : "ru",
    "english": "en"
}
DEFAULT_LANG = LANGS["english"]

CUTOFF = 0.4
MAX_GUESSES = 10
MAX_TOP_PLAYERS = 10

owner_id = 360440725923430440