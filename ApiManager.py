from requests import get, Response, RequestException
from json import loads
from typing import Dict, List, Tuple

from Logger import Logger
from cfg import API_PATH, MAX_TOP_PLAYERS

class ApiManager():
    @classmethod
    def __sendRequest(cls, params: str, addr: str):
        try:
            resp = get(url=addr, params=params)
        except RequestException as e:
            Logger.writeApiFatalLog(f"{e}")
            return False
        if not resp.ok:
            Logger.writeApiFatalLog(f"[NOT OK] {resp.url} {resp.content}")
            return False

        return loads(resp.text.encode('utf8'))
    @classmethod
    def getComplexStats(cls, ip: str, port: str, stat_data: dict, arg_name: str, arg_data: dict, arg_val: str) -> List[Tuple[str, int]]:
        addr = f"http://{ip}:{port}{API_PATH}"
        resp: dict = cls.__sendRequest({
            'statistic': stat_data['mc_tag'],
            arg_name: arg_data['mc_tag']
        }, addr)
        if resp == False:
            return resp
        # sorting data so higher stats are on top. Also leaving only first 'MAX_TOP_PLAYERS' players
        data: List[tuple] = sorted(resp.items(), reverse=True, key=lambda item: item[1])[:MAX_TOP_PLAYERS]
        cls.__devideDataByDevideFactor(stat_data['devide_factor'], data)
        return data
        
    @classmethod
    def getRegularStats(cls, ip: str, port: str, stat_data: dict) -> List[Tuple[str, int]]:
        addr = f"http://{ip}:{port}{API_PATH}"
        resp: dict = cls.__sendRequest({
            'statistic': stat_data['mc_tag']
        }, addr)
        if resp == False:
            return resp
        # sorting data so higher stats are on top. Also leaving only first 'MAX_TOP_PLAYERS' players
        data: List[tuple] = sorted(resp.items(), reverse=True, key=lambda item: item[1])[:MAX_TOP_PLAYERS]
        cls.__devideDataByDevideFactor(stat_data['devide_factor'], data)
        return data
        
    @classmethod
    def __devideDataByDevideFactor(cls, devide_factor: int, data: List[tuple]) -> None:
        for i in range(len(data)):
            data[i] = (data[i][0], int(data[i][1] / devide_factor))

    @classmethod
    def getMcHeadApi(cls, player_name: str, size: int = 100):
        return cls.__sendRequest({}, f'https://mc-heads.net/head/{player_name}/{size}.png')