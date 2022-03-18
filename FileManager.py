from datetime import datetime
from os import listdir
from os.path import isfile, join
from json import load, dump
from typing import List

from discord.guild import Guild
from discord.role import Role
from discord.channel import TextChannel
from discord.message import Message

from cfg import DATA_FOLDER, DEFAULT_PORT, LANGS, STAT_DATA_FOLDER, WEEK_NUMBER_FILE, DEFAULT_LANG
from Logger import Logger

class StatFileManager():
    @classmethod
    def __getFileList(cls) -> List[str]:
        return [f for f in listdir(STAT_DATA_FOLDER) if isfile(join(STAT_DATA_FOLDER, f))]

    @classmethod
    def getGuildsIds(cls) -> List[int]:
        rtrn = []
        for file in cls.__getFileList():
            try:
                if not WEEK_NUMBER_FILE.endswith(file):
                    rtrn.append(int(file.replace(".json", "")))
            except ValueError:
                Logger.printLog(f"{file} had invalid name. Its ignored in statistics")
        return rtrn

    @classmethod
    def createStats(cls, guild_id: int, val: int = 0):
        with open(f"{STAT_DATA_FOLDER}{guild_id}.json", 'w') as f:
            dump({
                "total_calls": val,
                "calls_this_week": val
            }, f)

    @classmethod
    def getStats(cls, guild_id: int):
        try:
            with open(f"{STAT_DATA_FOLDER}{guild_id}.json", 'r') as f:
                return load(f)
        except FileNotFoundError:
            return False

    @classmethod
    def __setStats(cls, guild_id: int, total_calls: int, calls_this_week: int):
        with open(f"{STAT_DATA_FOLDER}{guild_id}.json", 'w') as f:
            dump({
                "total_calls": total_calls,
                "calls_this_week": calls_this_week
            }, f)

    @classmethod
    def setWeekCalls(cls, guild_id: int, calls_this_week: int):
        data = cls.getStats(guild_id)
        if not data:
            return False
        cls.__setStats(guild_id, data["total_calls"], calls_this_week)

    @classmethod
    def __checkIfWeekPassed(cls):
        with open(WEEK_NUMBER_FILE, 'r') as f:
            saved_week_number = load(f)
        current_week_number = datetime.now().isocalendar()[1]
        if current_week_number != saved_week_number:
            Logger.printLog(f"New week number {current_week_number}. Weekly stats reset")
            with open(WEEK_NUMBER_FILE, 'w') as f:
                dump(current_week_number, f)
            for guild_id in cls.getGuildsIds():
                cls.setWeekCalls(guild_id, 0)

    @classmethod
    def incCallStat(cls, guild_id: int):
        cls.__checkIfWeekPassed()
        stats = cls.getStats(guild_id)
        if not stats:
            cls.createStats(guild_id, 1)
            return
        cls.__setStats(guild_id, stats["total_calls"] + 1, stats["calls_this_week"] + 1)

class FileManager():
    @classmethod
    def __getFileList(cls):
        return [f for f in listdir(DATA_FOLDER) if isfile(join(DATA_FOLDER, f))]

    @classmethod
    def getGuildsIds(cls) -> List[int]:
        rtrn = []
        for file in cls.__getFileList():
            try:
                rtrn.append(int(file.replace(".json", "")))
            except ValueError:
                Logger.printLog(f"{file} had invalid name. Its ignored in statistics")
        return rtrn

    @classmethod
    def getRole(cls, guild_id: int) -> int:
        data = cls.getGuildData(guild_id)
        if data:
            return data["mgr_role"]
        else:
            return False

    @classmethod
    def createNewGuild(cls, guild_id: int):
        """Creates new guild file with default empty values"""
        cls.setGuildData(
            guild_id=guild_id,
            manager_role_id=-1,
            server_ip="",
            port=DEFAULT_PORT,
            lang=DEFAULT_LANG
        )
        StatFileManager.createStats(guild_id)

    @classmethod
    def setGuildData(cls, guild_id: int, manager_role_id: int, server_ip: str, port: str, lang: str):
        """Saves dict {'server_ip': server_ip, 'port': port} in file <id>.json"""
        with open(f"{DATA_FOLDER}{guild_id}.json", 'w') as f:
            dump({
                "mgr_role": manager_role_id,
                "server_ip": server_ip,
                "port": port,
                "lang": lang
            }, f)

    @classmethod
    def getGuildData(cls, guild_id: int):
        """Returns guild data. If file is not present returns False"""
        try:
            with open(f"{DATA_FOLDER}{guild_id}.json", 'r') as f:
                return load(f)
        except FileNotFoundError:
            return False

    @classmethod
    def setRole(cls, guild_id: int, new_manager_role: Role):
        """Sets manager role for guild. Returns False if file is not present"""
        data = cls.getGuildData(guild_id)
        if not data:
            return False
        cls.setGuildData(guild_id, new_manager_role.id, data["server_ip"], data["port"], data["lang"])

    @classmethod
    def setServerIp(cls, guild_id: int, new_ip: str):
        """Sets channel for guild. Returns False if file is not present"""
        data = cls.getGuildData(guild_id)
        if not data:
            return False
        cls.setGuildData(guild_id, data["mgr_role"], new_ip, data["port"], data["lang"])

    @classmethod
    def setPort(cls, guild_id: int, new_port: str):
        """Sets channel for guild. Returns False if file is not present"""
        data = cls.getGuildData(guild_id)
        if not data:
            return False
        cls.setGuildData(guild_id, data["mgr_role"], data["server_ip"], new_port, data["lang"])

    @classmethod
    def setLangRu(cls, guild_id: int):
        """Sets channel for guild. Returns False if file is not present"""
        data = cls.getGuildData(guild_id)
        if not data:
            return False
        cls.setGuildData(guild_id, data["mgr_role"], data["server_ip"], data["port"], LANGS["russian"])

    @classmethod
    def setLangEn(cls, guild_id: int):
        """Sets channel for guild. Returns False if file is not present"""
        data = cls.getGuildData(guild_id)
        if not data:
            return False
        cls.setGuildData(guild_id, data["mgr_role"], data["server_ip"], data["port"], LANGS["english"])