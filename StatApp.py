from json import dumps
from typing import Dict, List

from discord import Client
from discord.message import Message
from discord.guild import Guild, Member
from discord.role import Role
from discord.channel import TextChannel
from discord.errors import Forbidden

from Logger import Logger
from MessageSender import MessageSender
from Command import Command
from FileManager import FileManager, StatFileManager
from ApiManager import ApiManager
from StatSearcher import StatSearcher
from cfg import prefix, owner_id
from api_args.stats import stats, stats_list
from api_args.entities import entities, entities_list
from api_args.materials import materials, materials_list

def needs_guild_file(func):
    async def wrapped_func(self=None, message: Message=None, guild_data=None):
        if not guild_data:
            await MessageSender.sendNotSetUp(message.channel)
            return
        await func(self, message, guild_data)
    return wrapped_func

def owner_command(func):
    async def wrapped_func(self=None, message: Message=None):
        if message.author.id != owner_id:
            return
        await func(self, message)
    return wrapped_func

class StatApp():
    def __init__(self, client: Client) -> None:
        self.client: Client = client
        self.commands: Dict[str, Command] = {
            "start": Command("start", self.__startCommand, 
            "Start! Call this command to start using bot", f"{prefix}start"),
            "set_role": Command("set_role", self.__setRoleCommand, 
            "Sets role that is able to manage bot settings. If no role was set, everbody will be able to change bot settings!", f"{prefix}set_role <@role>"),
            "set_ip": Command("set_ip", self.__setIpCommand, 
            "Sets minecraft server ip. Bot will request player data from there", f"{prefix}set_ip <minecraft server ip>"),
            "cfg": Command("cfg", self.__cfgCommand, 
            "Shows current bot's settings", f"{prefix}cfg"),
            "help": Command("help", self.__helpCommand, 
            "Shows help message", f"{prefix}help"),
        }
        self.owner_commands: Dict[str, Command] = {
            "data": Command("data", self.__dataOwnerCommand, 
            "-", "-"),
            "stat": Command("stat", self.__statOwnerCommand, 
            "-", "-"),
        }
        Logger.printLog("App inited")

    async def onMessage(self, message: Message) -> None:
        if message.author.bot or not message.content.startswith(prefix):
            return
        command, _ = self.__retrieveArgsFromMessage(message)
        if not command:
            return

        if command in self.owner_commands:
            await self.owner_commands[command].handler(message)
        if type(message.channel) == TextChannel:
            Logger.writeApiLog(f"Guild {message.guild}({message.guild.id}) called '{message.content}'")
            if command in self.commands:
                if self.__isPermitted(message):
                    guild_data = FileManager.getGuildData(message.guild.id)
                    await self.commands[command].handler(message, guild_data)
                else:
                    await MessageSender.sendNotPermitted(message.channel)
            else:
                guild_data = FileManager.getGuildData(message.guild.id)
                await self.__statsCommandsHandler(message, guild_data)

    def __retrieveArgsFromMessage(self, message: Message):
        """Retrieves args from message.content. Returns tuple (command: str, args: list[str])"""
        splited: list[str] = message.content.split(maxsplit=1)
        return (splited[0].replace(prefix, ""), splited[1:])

    def __isPermitted(self, message: Message) -> bool:
        mgr_role_id = FileManager.getRole(message.guild.id)
        mgr_role: Role = message.guild.get_role(mgr_role_id)
        if not mgr_role:
            return True
        return mgr_role in message.author.roles

    @needs_guild_file
    async def __statsCommandsHandler(self, message: Message, guild_data):
        if guild_data["server_ip"] == "":
            await MessageSender.sendIpNotSetUp(message.channel)
            return

        stat, args = self.__retrieveArgsFromMessage(message)
        # amount of search results
        stat_variants = StatSearcher.getStatSearchResults(stat)
        # if not 1 variant returned, sends message about this to user and returns False
        stat = await self.__handleVariantsStates(stat_variants, stat, message.channel)
        if not stat:
            return
        # if its regular stat that needs no argument, we process it
        if not (stats[stat]["needs_entity"] or stats[stat]["needs_material"]):
            top_list = ApiManager.getRegularStats(guild_data["server_ip"], guild_data["port"], stats[stat])
            if top_list != False:
                await MessageSender.sendStats(message.channel, top_list, stat)
                StatFileManager.incCallStat(message.guild.id)
            else:
                await MessageSender.sendCantConnect(message.channel)
            return
        # check if arg is present. message about it if its not
        if stats[stat]["needs_entity"] and len(args) < 1:
            await MessageSender.sendStatRequiresArgument(message.channel, stat, "entity", entities_list)
            return
        elif stats[stat]["needs_material"] and len(args) < 1:
            await MessageSender.sendStatRequiresArgument(message.channel, stat, "material", materials_list)
            return
        # now we know that our stat needs argument and that its present
        if stats[stat]["needs_entity"]:
            arg_variants = StatSearcher.getEntitySearchResults(args[0])
        elif stats[stat]["needs_material"]:
            arg_variants = StatSearcher.getMaterialSearchResults(args[0])
        else:
            Logger.printLog(f"{stat} needs no entity or material but got to the complex stats section", error=True)
            return
        # if not 1 variant returned, sends message about this to user and returns False
        arg = await self.__handleVariantsStates(arg_variants, args[0], message.channel)
        if not arg:
            return
        if stats[stat]["needs_entity"]:
            top_list = ApiManager.getComplexStats(guild_data["server_ip"], guild_data["port"], stats[stat], "entity_type", entities[arg], arg)
        elif stats[stat]["needs_material"]:
            top_list = ApiManager.getComplexStats(guild_data["server_ip"], guild_data["port"], stats[stat], "block_type", materials[arg], arg)
        if top_list != False:
            await MessageSender.sendStats(message.channel, top_list, stat, arg)
            StatFileManager.incCallStat(message.guild.id)
        else:
            await MessageSender.sendCantConnect(message.channel)

    async def __handleVariantsStates(self, variants: List[str], target_stat: str, channel: TextChannel):
        '''If len of variants is 0 or >1, sends messages to user about this. And returns False. Else returns single variant'''
        # if no results found
        if len(variants) == 0:
            await MessageSender.sendStatArgNotFound(channel, target_stat)
            return False
        # if several results
        elif len(variants) > 1:
            await MessageSender.sendStatArgSeveralResults(channel, target_stat, variants)
            return False
        # if one result, we continue
        elif len(variants) == 1:
            return variants[0]

    async def __startCommand(self, message: Message, guild_data):
        if not guild_data:
            FileManager.createNewGuild(message.guild.id)
            await MessageSender.sendGuildInited(message.channel)
            Logger.printLog(f"{message.guild} joined!")
        else:
            await MessageSender.sendGuildAlreadyInited(message.channel)

    @needs_guild_file
    async def __setRoleCommand(self, message: Message, guild_data):
        _, raw_role_id = self.__retrieveArgsFromMessage(message)
        if len(raw_role_id) == 0:
            MessageSender.sendInvalidSyntax(message.channel, "Role argument is missing")
            return
        role_id: int = int(''.join([i for i in raw_role_id[0] if i.isdigit()]))
        role: Role = message.guild.get_role(role_id)
        if role:
            FileManager.setRole(message.guild.id, role)
            await MessageSender.sendParameterSet(message.channel, "Manager role", role.mention)
        else:
            MessageSender.sendInvalidSyntax(message.channel, "Invalid role")

    @needs_guild_file
    async def __setIpCommand(self, message: Message, guild_data):
        _, ip_str = self.__retrieveArgsFromMessage(message)
        if len(ip_str) == 0:
            await MessageSender.sendInvalidSyntax(message.channel, "Ip argument is missing")
            return
        FileManager.setServerIp(message.guild.id, ip_str[0])
        await MessageSender.sendParameterSet(message.channel, "Ip", ip_str[0])

    @needs_guild_file
    async def __cfgCommand(self, message: Message, guild_data):
        await MessageSender.sendCfg(message.channel, guild_data)

    async def __helpCommand(self, message: Message, guild_data):
        await MessageSender.sendEmbed(
            message.channel,
            [[f"**`{cmd.syntax}`**" for _, cmd in self.commands.items()] + 
            ["**Get the plugin:**", "**Have a question? Found bug? Contact us here!**"],
            [f"*{cmd.description}*" for _, cmd in self.commands.items()] + 
            ["https://www.curseforge.com/minecraft/bukkit-plugins/statsmc", "https://discord.gg/Y7cnUV58Rn"]],
        )

    @owner_command
    async def __dataOwnerCommand(self, message: Message):
        guild_ids = FileManager.getGuildsIds()
        guilds_data: List = []
        guild_names: List[str] = []
        for id_ in guild_ids:
            try:
                guild: Guild = await self.client.fetch_guild(guild_id=id_)
                if not guild:
                    guild_names.append(f"Name: *`Cant fetch guild`* Id: `{id_}`")
                else:
                    guild_names.append(f"Name: `{guild.name}` Id: `{id_}`")
            except Forbidden:
                guild_names.append(f"Name: *`Guild is forbidden`* Id: `{id_}`")

            guilds_data.append(f"```{dumps(FileManager.getGuildData(id_), indent=4)}```")
    
        await MessageSender.sendEmbed(
            message.channel,
            [guild_names, guilds_data],
            guild_footer=False
        )

    @owner_command
    async def __statOwnerCommand(self, message: Message):
        guild_ids = StatFileManager.getGuildsIds()
        guilds_data: List = []
        guild_names: List[str] = []
        for id_ in guild_ids:
            try:
                guild: Guild = await self.client.fetch_guild(guild_id=id_)
                if not guild:
                    guild_names.append(f"Name: *`Cant fetch guild`* Id: `{id_}`")
                else:
                    guild_names.append(f"Name: `{guild.name}` Id: `{id_}`")
            except Forbidden:
                guild_names.append(f"Name: *`Guild is forbidden`* Id: `{id_}`")

            guilds_data.append(f"```{dumps(StatFileManager.getStats(id_), indent=4)}```")

        await MessageSender.sendEmbed(
            message.channel,
            [guild_names, guilds_data],
            guild_footer=False
        )