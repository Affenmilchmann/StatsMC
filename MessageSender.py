from datetime import datetime, timedelta
from time import mktime
from typing import List, Tuple
from random import choice

from discord.message import Message
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.colour import Colour
from discord.guild import Member, Guild

from cfg import default_embeds_colour, prefix, DEFAULT_PORT
from Logger import Logger

from api_args.stats import stats
from api_args.entities import entities
from api_args.materials import materials

class MessageSender():
    @classmethod
    def __getDiscordNowTime(cls):
        return f"<t:{int(mktime(datetime.now().timetuple()))}>"

    @classmethod
    def __shortenLargeNums(cls, number: int) -> str:
        d = {
            1000000: "M",
            1000: "K",
        }

        for k, v in d.items():
            if number > k:
                return f"**{str(round(number / k, 2))}**" + v

        return f"**{str(number)}**"

    @classmethod
    async def sendEmbed(cls, channel: TextChannel, fields: List[List[str]], thumbnail_url="", colour: Colour=default_embeds_colour, guild_thumbnail: bool=False, guild_footer=True, delete_after=-1, author: Member=None, title: str=None):
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

        if guild_footer and guild_icon_url:
            embed_.set_footer(text=f"StatsMC | Found bug? Have a question? Use {prefix}help to see support server link", icon_url=guild_icon_url)

        if author:
            embed_.set_author(name=str(author.name)+'#'+str(author.discriminator), icon_url=author.avatar_url)

        if delete_after > 0:
            return await channel.send(embed=embed_, delete_after=delete_after)
        else:
            return await channel.send(embed=embed_)

    @classmethod
    async def sendStats(cls, channel: TextChannel, player_data: List[Tuple[str, int]], stat: str, arg: str = None):
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
            player_stats.append(f"> {cls.__shortenLargeNums(player_data[i][1])}")
        # processing rest of the players
        for i in range(len(player_data[3:])):
            player_names.append(f"**`{i+4} |`** {player_data[i+3][0]}")
            player_stats.append(f"{cls.__shortenLargeNums(player_data[i+3][1])}")
        await cls.sendEmbed(
            channel,
            fields=[player_names, player_stats],
            title=title
        )

    @classmethod
    async def sendStatArgNotFound(cls, channel: TextChannel, user_input):
        await cls.sendEmbed(
            channel,
            fields=[[f"I dont recognise `{user_input}`"],
            ["Keep in mind that I provide only vanilla statistics. So only statistics that can be found in *Statistics* tab in minecraft menu"]],
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendStatArgSeveralResults(cls, channel: TextChannel, user_input: str, results: List[str]):
        variants_str = f"There are **{len(results)}** most likely variants:\n"
        for result in results[:-1]:
            variants_str += f"`{result}`,"
        variants_str += f"`{results[-1]}`."
        await cls.sendEmbed(
            channel,
            fields=[[f"I am not sure what you meant by `{user_input}`!"],
            [variants_str]],
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendStatRequiresArgument(cls, channel: TextChannel, stat: str, argument_type: str, example_grop: List[str] = ["argument"]):
        await cls.sendEmbed(
            channel,
            fields=[[f"{stat} requires {argument_type} argument!"],
            [f"Example: `{prefix}{stat} {choice(example_grop)}`"]],
            colour=Colour.light_gray()
        )

    @classmethod
    async def sendNotSetUp(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**Server is not set up!**"],
            [f"Use `{prefix}start` first. Install StatsMC plugin on your server (Link can be found in help message) and then make sure you set up your server's ip with `{prefix}set_ip`"]],
            colour=Colour.red()
        )

    @classmethod
    async def sendGuildInited(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**Your server was linked!**", "*Friendly reminder:*"],
            ["Before using bot consider setting manager role and minecraft server ip.",
            "*This bot requires StatsMC plugin running on the server. Link can be found in help message*"]],
            guild_thumbnail=True
        )

    @classmethod
    async def sendGuildAlreadyInited(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**Oops!**"],
            ["Your server is already linked"]],
        )

    @classmethod
    async def sendParameterSet(cls, channel: TextChannel, parameter_name: str, parameter_val: str):
        await cls.sendEmbed(
            channel,
            [["**Success!**"],
            [f"{parameter_name} was set to {parameter_val}"]],
        )

    @classmethod
    async def sendCfg(cls, channel: TextChannel, cfg_data: dict):
        titels = []
        values = []
        titels.append("**Manager role**")
        values.append("> Missing" if cfg_data["mgr_role"] == -1 else f"> <@&{cfg_data['mgr_role']}>")
        titels.append("**Server IP**")
        values.append(f"> {cfg_data['server_ip']}")
        await cls.sendEmbed(
            channel,
            [titels, values],
        )

    @classmethod
    async def sendNotPermitted(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**You are not permitted to use this command!**"],
            [f"-"]],
            colour=Colour.red()
        )

    @classmethod
    async def sendInvalidSyntax(cls, channel: TextChannel, message: str):
        await cls.sendEmbed(
            channel,
            [["**Invalid syntax**"],
            [message]],
            colour=Colour.red()
        )

    @classmethod
    async def sendCantConnect(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**Cant connect to minecraft server!**"],
            [f"Make sure you have StatsMC plugin installed on your server and port {DEFAULT_PORT} is opened"]],
            colour=Colour.red()
        )

    @classmethod
    async def sendIpNotSetUp(cls, channel: TextChannel):
        await cls.sendEmbed(
            channel,
            [["**Set up your ip first!**"],
            [f"You need to provide me your minecraft server's ip with `{prefix}set_ip <your ip>`. Your server must have StatMC plugin installed."]],
            colour=Colour.red()
        )