from datetime import datetime, timedelta
from time import mktime
from typing import List, Tuple
from random import choice

from discord.message import Message
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.colour import Colour
from discord.guild import Member, Guild
from discord.errors import Forbidden

from .config.cfg import BOT_NAME, default_embeds_colour, prefix, DEFAULT_PORT
from .config.messages_cfg import short_numbers, info_msgs, cfg_msg, footer_text, lang_switched_msg

from .ApiManager import ApiManager
from .Logger import Logger

from .api_args.stats import stats
from .api_args.entities import entities
from .api_args.materials import materials

class MessageSender():
    @classmethod
    def __getDiscordNowTime(cls):
        return f"<t:{int(mktime(datetime.now().timetuple()))}>"

    @classmethod
    def __shortenLargeNums(cls, number: int, lang: str) -> str:
        d = {
            1000000: short_numbers["million"][lang],
            1000: short_numbers["thausand"][lang],
        }

        for k, v in d.items():
            if number > k:
                return f"**{str(round(number / k, 2))}**" + v

        return f"**{str(number)}**"

    @classmethod
    async def sendEmbed(cls, channel: TextChannel, fields: List[List[str]], lang: str, thumbnail_url="", colour: Colour=default_embeds_colour, guild_thumbnail: bool=False, guild_footer=True, delete_after=-1, author: Member=None, title: str=None):
        if title:
            embed_ = Embed(title=title, colour=colour)
        else:
            embed_ = Embed(colour=colour)
        if len(fields) != 2:
            raise ValueError(f"fields argument have to have len of 2. Len of fields is {len(fields)}")
        if type(fields[0]) != list or type(fields[1]) != list:
            raise ValueError(f"fields argument have to be list of lists. Got [{type(fields[0])}, {type(fields[1])}]")
        if len(fields[0]) != len(fields[1]):
            raise ValueError(f"'fields's inner lists must be same size. Sizes are {len(fields[0])} and {len(fields[1])}")
        if len(fields[0]) == 0:
            raise ValueError(f"'fields's inner lists must be not empty. Sizes are {len(fields[0])} and {len(fields[1])}")

        for i in range(len(fields[0])):
            embed_.add_field(name=str(fields[0][i]), value=str(fields[1][i]), inline=False)

        try:
            guild_icon_url = channel.guild.icon_url
        except AttributeError:
            guild_icon_url = None

        if guild_thumbnail and guild_icon_url:
            embed_.set_thumbnail(url=guild_icon_url)
        if thumbnail_url != "":
            embed_.set_thumbnail(url=thumbnail_url)

        if guild_footer:
            if guild_icon_url:
                embed_.set_footer(text=footer_text[lang], icon_url=guild_icon_url)
            else:
                embed_.set_footer(text=footer_text[lang])

        if author:
            embed_.set_author(name=str(author.name)+'#'+str(author.discriminator), icon_url=author.avatar_url)

        try:
            if delete_after > 0:
                return await channel.send(embed=embed_, delete_after=delete_after)
            else:
                return await channel.send(embed=embed_)
        except Forbidden as e:
            Logger.printLog("Cant send message. Forbidden. Check logs", error=True)
            Logger.writeApiFatalLog(f"Forbidden. Guild: name:{channel.guild} id:{channel.guild.id}. Channel: name:{channel.name} id: {channel.id}")
            
    @classmethod
    async def sendStats(cls, channel: TextChannel, player_data: List[Tuple[str, int]], stat: str, lang: str, arg: str = None):
        title = f"{stats[stat]['description']}"
        if arg:
            # time complexity O(1) for dicts so its fine
            if arg in entities:
                title += f" {entities[arg]['description']}"
            elif arg in materials:
                title += f" {materials[arg]['description']}"
        player_names = []
        player_stats = []
        # processing top 3 players
        for i in range(len(player_data[:3])):
            player_names.append(f"**`{i+1} | {player_data[i][0]} `**")
            player_stats.append(f"> {cls.__shortenLargeNums(player_data[i][1], lang)}")
        # processing rest of the players
        for i in range(len(player_data[3:])):
            player_names.append(f"**`{i+4} |`** {player_data[i+3][0]}")
            player_stats.append(f"{cls.__shortenLargeNums(player_data[i+3][1], lang)}")

        if len(player_names) > 0:
            # getting skin avatar for the top leader
            mchead_api_return = ApiManager.getMcHeadApiLink(player_data[0][0])

        await cls.sendEmbed(
            channel,
            [player_names, player_stats],
            lang,
            title=title,
            thumbnail_url=mchead_api_return if mchead_api_return else ""
        )

    @classmethod
    async def sendStatArgNotFound(cls, channel: TextChannel, user_input, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["stat_arg_not_found"]["name"][lang].format(user_input=user_input)],
            [info_msgs["stat_arg_not_found"]["value"][lang]]],
            lang,
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendStatArgSeveralResults(cls, channel: TextChannel, user_input: str, results: List[str], lang: str):
        variants_str = info_msgs["stat_several_results"]["value"][lang].format(amount=len(results))
        for result in results[:-1]:
            variants_str += f"`{result}`,"
        variants_str += f"`{results[-1]}`."
        await cls.sendEmbed(
            channel,
            [[info_msgs["stat_several_results"]["name"][lang].format(user_input=user_input)],
            [variants_str]],
            lang,
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendStatRequiresArgument(cls, channel: TextChannel, stat: str, argument_type: str, lang: str, example_grop: List[str] = ["argument"]):
        await cls.sendEmbed(
            channel,
            [[info_msgs["stat_requires_argument"]["name"][lang].format(stat=stat, argument_type=argument_type)],
            [info_msgs["stat_requires_argument"]["value"][lang].format(stat=prefix+stat, arg=choice(example_grop))]],
            lang,
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendNotSetUp(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["guild_not_set_up"]["name"][lang]],
            [info_msgs["guild_not_set_up"]["value"][lang]]],
            lang,
            colour=Colour.red()
        )

    @classmethod
    async def sendGuildInited(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [info_msgs["guild_inited"]["name"][lang],
            info_msgs["guild_inited"]["value"][lang]],
            lang,
            guild_thumbnail=True
        )

    @classmethod
    async def sendGuildAlreadyInited(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["guild_alr_inited"]["name"][lang]],
            [info_msgs["guild_alr_inited"]["value"][lang]]],
            lang,
        )

    @classmethod
    async def sendParameterSet(cls, channel: TextChannel, parameter_name: str, parameter_val: str, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["success"][lang]],
            [info_msgs["parameter_set"][lang].format(name=info_msgs["parameters"][parameter_name][lang], val=parameter_val)]],
            lang,
        )

    @classmethod
    async def sendLangSwitched(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[lang_switched_msg[lang]],
            [f"-"]],
            lang,
            colour=Colour.green()
        )

    @classmethod
    async def sendCfg(cls, channel: TextChannel, cfg_data: dict, lang: str):
        titels = []
        values = []
        titels.append(cfg_msg["mgr_field_name"][lang])
        values.append(cfg_msg["missing_value"][lang] if cfg_data["mgr_role"] == -1 else f"> <@&{cfg_data['mgr_role']}>")
        titels.append(cfg_msg["ip_field_name"][lang])
        values.append(cfg_msg["missing_value"][lang] if cfg_data["server_ip"] == "" else f"> {cfg_data['server_ip']}")
        await cls.sendEmbed(
            channel,
            [titels, values],
            lang,
        )

    @classmethod
    async def sendNotPermitted(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["not_permitted"][lang]],
            [f"-"]],
            lang,
            colour=Colour.red()
        )

    @classmethod
    async def sendInvalidSyntax(cls, channel: TextChannel, error_type: str, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["invalid_syntax"][lang]],
            [info_msgs["invalid_syntax_comments"][error_type][lang]]],
            lang,
            colour=Colour.red()
        )

    @classmethod   
    async def sendCantConnect(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["cant_connect"]["name"][lang]],
            [info_msgs["cant_connect"]["value"][lang]]],
            lang,
            colour=Colour.red()
        )

    @classmethod
    async def sendIpNotSetUp(cls, channel: TextChannel, lang: str):
        await cls.sendEmbed(
            channel,
            [[info_msgs["ip_not_set"]["name"][lang]],
            [info_msgs["ip_not_set"]["value"][lang]]],
            lang,
            colour=Colour.red()
        )