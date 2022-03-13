from cgitb import reset
from typing import List

from difflib import get_close_matches

from cfg import CUTOFF, MAX_GUESSES
from api_args.stats import stats_list
from api_args.entities import entities_list
from api_args.materials import materials_list

class StatSearcher():
    @classmethod
    def __getSearchResults(cls, search_input: str, where_to_search: List[str]) -> List[str]:
        result = get_close_matches(search_input, where_to_search, n=MAX_GUESSES, cutoff=CUTOFF)
        if len(result) > 1 and (result[0].upper() == search_input.replace(" ", "_").upper()):
            return [result[0]]
        return result

    @classmethod
    def getStatSearchResults(cls, search_input) -> List[str]:
        return cls.__getSearchResults(search_input, stats_list)

    @classmethod
    def getEntitySearchResults(cls, search_input) -> List[str]:
        return cls.__getSearchResults(search_input, entities_list)

    @classmethod
    def getMaterialSearchResults(cls, search_input) -> List[str]:
        return cls.__getSearchResults(search_input, materials_list)