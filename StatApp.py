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
        self.manager_commands: Dict[str, Command] = {
            "start": Command("start", self.__startCommand, 
            "Start! Call this command to start using bot", f"{prefix}start"),
            "set_role": Command("set_role", self.__setRoleCommand, 
            "Sets role that is able to manage bot settings. If no role was set, everbody will be able to change bot settings!", f"{prefix}set_role <@role>"),
            "set_ip": Command("set_ip", self.__setIpCommand, 
            "Sets minecraft server ip. Bot will request player data from there", f"{prefix}set_ip <minecraft server ip>"),
            "cfg": Command("cfg", self.__cfgCommand, 
            "Shows current bot's settings", f"{prefix}cfg"),
        }
        self.user_commands: Dict[str, Command] = {
            "help": Command("help", self.__helpCommand, 
            "Shows help message", f"{prefix}help"),
            "guide": Command("guide", self.__guideCommand, 
            "Shows guide how to use statistic commands", f"{prefix}guide"),
            "example": Command("example", self.__exampleCommand, 
            "Shows example of searching statistic", f"{prefix}example"),
            "commands": Command("commands", self.__basicCommandsCommand, 
            "Shows basic commands list.", f"{prefix}commands"),
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
            if command in self.manager_commands:
                if self.__isPermitted(message):
                    guild_data = FileManager.getGuildData(message.guild.id)
                    await self.manager_commands[command].handler(message, guild_data)
                else:
                    await MessageSender.sendNotPermitted(message.channel)
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
        titels: List[str] = []
        bodies: List[str] = []

        titels.append("**User commands:**")
        bodies.append("-"*5)
        for _, cmd in self.user_commands.items():
            titels.append(f"**`{cmd.syntax}`**")
            bodies.append(f"*{cmd.description}*")

        titels.append("**Manager commands:**")
        bodies.append("-"*5)
        for _, cmd in self.manager_commands.items():
            titels.append(f"**`{cmd.syntax}`**")
            bodies.append(f"*{cmd.description}*")
        await MessageSender.sendEmbed(
            message.channel,
            [titels + ["**Get the plugin:**", "**Have a question? Found bug? Contact us here!**"],
            bodies + ["https://www.curseforge.com/minecraft/bukkit-plugins/statsmc", "https://discord.gg/Y7cnUV58Rn"]],
        )

    async def __guideCommand(self, message: Message, guild_data):
        msg = """Syntax is `st!<statistic_name>`
                There are hundrets of commands and they all cant be listed here.
                Basically you can access all the stats from Statistics tab from ingame menu.
                Just type anything and bot will try to guess what did you mean and suggest its thoughts (:

                To see usage example use `st!example`

                Some statistics require additional arguments.
                Syntax is `st!<statistic_name> <entity_type/material_type>`
                Bot will try to guess second argument too. When the first argument is correct.

                To see basic commands use `st!commands`"""
        await MessageSender.sendEmbed(
            message.channel,
            [["**Guide**"], [msg]],
        )

    async def __exampleCommand(self, message: Message, guild_data):
        first_example = """For an example, you want to see top for villager trades amount.
                            You type `st!villager_trade`. Bot responses you:
                            *I am not sure what you meant by `villager_trade`. There are 8 most likely variants:
                            `damage_taken`, `talked_to_villager`, `traded_with_villager`, ...*
                            You spot the variant you need *traded_with_villager* and type `st!traded_with_villager`
                            Voila! Bot responses you with player top.
                            """
        second_example = """You want to see top for amount of mined diamonds.
                            You type `st!mine diamond`. Bot doesnt recognise *mine* and suggests
                            *`mine_block`, `pig_one_cm`, ...*
                            You again spot *mine_block* and type `st!mine_block diamond`.
                            Voil...a?? Why do I see an empty top list?
                            """
        problems = """Thats because minecraft by default tracks even impossible stats.
                        It tracks *mine_block* with all existing items. Not only blocks. And you cant mine diamond item.
                        But you can mine diamond ore. So with `st!mine_block diamond_ore` you get your top list.
                        
                        And you realise that you have mined way more dia ores than it shows.
                        Thats because regular diamond ore is quite rare in current version.
                        You need to add to it deepslate variant. You type `st!mine_block deepslate_diamond_ore`
                        Voila! Here are your stats. 
                        *(note: if you type second argument incorrectly, bot will also suggest you correct close variants)*"""

        await MessageSender.sendEmbed(
            message.channel,
            [["**First example**", "**Second example**", "**Possible problems**"], 
            [first_example, second_example, problems]],
        )

    async def __basicCommandsCommand(self, message: Message, guild_data):
        msg = """   `st!mine_block <item_name>` - amount of specific block mined
                    `st!use_item <item_name>` - amount of specific item used. It may be
                    blocks (means blocks placed), tools, food (times eaten), fireworks, etc. Anything
                    you can use by clicking.
                    `st!craft_item <item_name>` - amount of specific item crafted
                    `st!drop <item_name>` - amount of specific item dropped
                    `st!pickup <item_name>` - amount of specific item picked up
                    `st!break_item <item_name>` - amount of tool broken
                    `st!mob_kills` - general amount of killed mobs
                    `st!kill_entity <mob_name>` - amount of specific mob killed
                    `st!entity_killed_by <mob_name>` - amount of deaths from specific mob"""
                    
        note =   """*these are just most used commands. 
                    As I said there are dozens of statistics that mc tracks. Hundrets of possible blocks, entities.
                    If you see something in stat game tab, you can find it here.
                    
                    If you have suggestions about command aliases, feel free to contact me in my discord server*"""

        await MessageSender.sendEmbed(
            message.channel,
            [["**Basic commands**", "*Note*"], 
            [msg, note]],
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