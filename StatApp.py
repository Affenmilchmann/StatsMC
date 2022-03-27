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
from cfg import DEFAULT_LANG, prefix, owner_id
from messages_cfg import help_links, command_descriptions, help_labels, guide_message, example_message, basic_commands_message
from api_args.stats import stats, stats_list
from api_args.entities import entities, entities_list
from api_args.materials import materials, materials_list

def needs_guild_file(func):
    async def wrapped_func(self=None, message: Message=None, guild_data=None):
        if not guild_data:
            await MessageSender.sendNotSetUp(message.channel, DEFAULT_LANG)
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
        self.manager_commands: Dict[str, Command] = {
            "start": Command("start", self.__startCommand, f"{prefix}start"),
            "set_role": Command("set_role", self.__setRoleCommand, f"{prefix}set_role <@role>"),
            "set_ip": Command("set_ip", self.__setIpCommand, f"{prefix}set_ip <minecraft server ip>"),
            "cfg": Command("cfg", self.__cfgCommand, f"{prefix}cfg"),
            "ru": Command("ru", self.__setLangRuCommand, f"{prefix}ru"),
            "en": Command("en", self.__setLangEnCommand, f"{prefix}en"),
        }
        self.user_commands: Dict[str, Command] = {
            "help": Command("help", self.__helpCommand,f"{prefix}help"),
            "guide": Command("guide", self.__guideCommand, f"{prefix}guide"),
            "example": Command("example", self.__exampleCommand, f"{prefix}example"),
            "commands": Command("commands", self.__basicCommandsCommand, f"{prefix}commands"),
        }
        self.owner_commands: Dict[str, Command] = {
            "data": Command("data", self.__dataOwnerCommand, "-"),
            "stat": Command("stat", self.__statOwnerCommand, "-"),
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
            StatFileManager.incCallStat(message.guild.id)
            if command in self.manager_commands:
                guild_data = FileManager.getGuildData(message.guild.id)
                if self.__isPermitted(message):
                    await self.manager_commands[command].handler(message, guild_data)
                else:
                    await MessageSender.sendNotPermitted(message.channel, guild_data["lang"])
            elif command in self.user_commands:
                guild_data = FileManager.getGuildData(message.guild.id)
                await self.user_commands[command].handler(message, guild_data)
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
            await MessageSender.sendIpNotSetUp(message.channel, guild_data["lang"])
            return

        stat, args = self.__retrieveArgsFromMessage(message)
        # amount of search results
        stat_variants = StatSearcher.getStatSearchResults(stat)
        # if not 1 variant returned, sends message about this to user and returns False
        stat = await self.__handleVariantsStates(stat_variants, stat, message.channel, guild_data["lang"])
        if not stat:
            return
        # if its regular stat that needs no argument, we process it
        if not (stats[stat]["needs_entity"] or stats[stat]["needs_material"]):
            top_list = ApiManager.getRegularStats(guild_data["server_ip"], guild_data["port"], stats[stat])
            if top_list != False:
                await MessageSender.sendStats(message.channel, top_list, stat, guild_data["lang"])
            else:
                await MessageSender.sendCantConnect(message.channel, guild_data["lang"])
            return
        # check if arg is present. message about it if its not
        if stats[stat]["needs_entity"] and len(args) < 1:
            await MessageSender.sendStatRequiresArgument(message.channel, stat, "entity", guild_data["lang"], entities_list)
            return
        elif stats[stat]["needs_material"] and len(args) < 1:
            await MessageSender.sendStatRequiresArgument(message.channel, stat, "material", guild_data["lang"], materials_list)
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
        arg = await self.__handleVariantsStates(arg_variants, args[0], message.channel, guild_data["lang"])
        if not arg:
            return
        if stats[stat]["needs_entity"]:
            top_list = ApiManager.getComplexStats(guild_data["server_ip"], guild_data["port"], stats[stat], "entity_type", entities[arg], arg)
        elif stats[stat]["needs_material"]:
            top_list = ApiManager.getComplexStats(guild_data["server_ip"], guild_data["port"], stats[stat], "block_type", materials[arg], arg)
        if top_list != False:
            await MessageSender.sendStats(message.channel, top_list, stat, guild_data["lang"], arg)
        else:
            await MessageSender.sendCantConnect(message.channel, guild_data["lang"])

    async def __handleVariantsStates(self, variants: List[str], target_stat: str, channel: TextChannel, lang: str):
        '''If len of variants is 0 or >1, sends messages to user about this. And returns False. Else returns single variant'''
        # if no results found
        if len(variants) == 0:
            await MessageSender.sendStatArgNotFound(channel, target_stat, lang)
            return False
        # if several results
        elif len(variants) > 1:
            await MessageSender.sendStatArgSeveralResults(channel, target_stat, variants, lang)
            return False
        # if one result, we continue
        elif len(variants) == 1:
            return variants[0]

    async def __startCommand(self, message: Message, guild_data):
        if not guild_data:
            FileManager.createNewGuild(message.guild.id)
            await MessageSender.sendGuildInited(message.channel, DEFAULT_LANG)
            Logger.printLog(f"{message.guild} joined!")
        else:
            await MessageSender.sendGuildAlreadyInited(message.channel, guild_data["lang"])

    @needs_guild_file
    async def __setRoleCommand(self, message: Message, guild_data):
        _, raw_role_id = self.__retrieveArgsFromMessage(message)
        if len(raw_role_id) == 0:
            await MessageSender.sendInvalidSyntax(message.channel, "role_arg_missing", guild_data["lang"])
            return
        try:
            role_id: int = int(''.join([i for i in raw_role_id[0] if i.isdigit()]))
        except ValueError:
            await MessageSender.sendInvalidSyntax(message.channel, "invalid_role", guild_data["lang"])
            return
        role: Role = message.guild.get_role(role_id)
        if role:
            FileManager.setRole(message.guild.id, role)
            await MessageSender.sendParameterSet(message.channel, "manager_role", role.mention, guild_data["lang"])
        else:
            await MessageSender.sendInvalidSyntax(message.channel, "invalid_role", guild_data["lang"])

    @needs_guild_file
    async def __setIpCommand(self, message: Message, guild_data):
        _, ip_str = self.__retrieveArgsFromMessage(message)
        if len(ip_str) == 0:
            await MessageSender.sendInvalidSyntax(message.channel, "ip_arg_missing", guild_data["lang"])
            return
        if ":" in ip_str[0]:
            await MessageSender.sendInvalidSyntax(message.channel, "ip_with_port", guild_data["lang"])
            return
        FileManager.setServerIp(message.guild.id, ip_str[0])
        await MessageSender.sendParameterSet(message.channel, "ip", ip_str[0], guild_data["lang"])

    @needs_guild_file
    async def __cfgCommand(self, message: Message, guild_data):
        await MessageSender.sendCfg(message.channel, guild_data, guild_data["lang"])

    async def __helpCommand(self, message: Message, guild_data):
        if not guild_data:
            lang = DEFAULT_LANG
        else:
            lang = guild_data["lang"]
            
        titels: List[str] = []
        bodies: List[str] = []

        titels.append(help_labels["user_commands"][lang])
        bodies.append("-"*5)
        for _, cmd in self.user_commands.items():
            titels.append(f"**`{cmd.syntax}`**")
            bodies.append(f"*{command_descriptions[cmd.command][lang]}*")

        titels.append(help_labels["manager_commands"][lang])
        bodies.append("-"*5)
        for _, cmd in self.manager_commands.items():
            titels.append(f"**`{cmd.syntax}`**")
            bodies.append(f"*{command_descriptions[cmd.command][lang]}*")
        await MessageSender.sendEmbed(
            message.channel,
            [titels + help_links[lang],
            bodies + ["https://www.curseforge.com/minecraft/bukkit-plugins/statsmc", "https://discord.gg/Y7cnUV58Rn"]],
            lang
        )

    @needs_guild_file
    async def __guideCommand(self, message: Message, guild_data):
        await MessageSender.sendEmbed(
            message.channel,
            [[guide_message["name"][guild_data["lang"]]], 
            [guide_message["value"][guild_data["lang"]]]], 
            guild_data["lang"]
        )

    @needs_guild_file
    async def __exampleCommand(self, message: Message, guild_data):
        await MessageSender.sendEmbed(
            message.channel,
            [example_message["name"][guild_data["lang"]],
            example_message["value"][guild_data["lang"]]], 
            guild_data["lang"]
        )

    @needs_guild_file
    async def __basicCommandsCommand(self, message: Message, guild_data):
        await MessageSender.sendEmbed(
            message.channel,
            [basic_commands_message["name"][guild_data["lang"]],
            basic_commands_message["value"][guild_data["lang"]]], 
            guild_data["lang"]
        )

    @needs_guild_file
    async def __setLangRuCommand(self, message: Message, guild_data):
        FileManager.setLangRu(message.guild.id)
        guild_data = FileManager.getGuildData(message.guild.id)
        await MessageSender.sendLangSwitched(message.channel, guild_data["lang"])

    @needs_guild_file
    async def __setLangEnCommand(self, message: Message, guild_data):
        FileManager.setLangEn(message.guild.id)
        guild_data = FileManager.getGuildData(message.guild.id)
        await MessageSender.sendLangSwitched(message.channel, guild_data["lang"])

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
            DEFAULT_LANG,
            guild_footer=False,
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
            DEFAULT_LANG,
            guild_footer=False
        )