from .cfg import prefix, DEFAULT_PORT, BOT_NAME

footer_text = {
    "en": f"{BOT_NAME} | Found bug? Have a question? Use {prefix}help to see support server link",
    "ru": f"{BOT_NAME} | Есть вопросы? Нашли баг? Ссылка на канал поддержки в {prefix}help"
}

help_links = {
    "en": ["**Get the plugin:**", "**Have a question? Found bug? Contact us here!**"],
    "ru": ["**Скачать плагин:**", "**Есть вопросы? Нашли баг? Свяжитесь с нами тут!**"]
}

help_labels = {
    "manager_commands": {
        "en": "**Manager commands:**",
        "ru": "**Администраторские команды:**"
    },
    "user_commands": {
        "en": "**User commands:**",
        "ru": "**Пользовательские команды:**"
    }
}

guide_message = {
    "name": {
        "en": "**Guide**",
        "ru": "**Инструкция**"
    },
    "value": {
        "en": f"""Syntax is `{prefix}<statistic_name>`
                There are hundrets of commands and they all cant be listed here.
                Basically you can access all the stats from Statistics tab from ingame menu.
                Just type anything after `{prefix}` and bot will try to guess what did you mean and suggest its thoughts (:

                Statistics search usage examples here -> `{prefix}example`

                Some statistics require additional argument.
                Syntax is `{prefix}<statistic_name> <entity_type/material_type>`
                Bot will try to guess second argument too. When the first argument is correct.

                To see basic commands use `{prefix}commands`""",
        "ru": f"""Синтаксис: `{prefix}<имя_статистики>`
                Всего доступно под сотню команд и просто перечислить их было бы не лучшей идеей.
                Вам доступны все ванильные статистики, которые можно найти во вкладке Статистика в меню майнкрафта.
                Просто введите имя статистики после `{prefix}` и бот подскажет вам ближайшие варианты (:

                Примеры использования системы поиска по статистикам тут -> `{prefix}example`

                Некоторые статистики требуют дополнительный аргуметн.
                Синтаксис: `{prefix}<имя_статистики> <тип_сущности/тип_материала>`
                Если бот может однозначно найти аргумент имя_статистики, он будет подсказывать второй аргумент также как и первый.

                Базовые команды тут -> `{prefix}commands`
                
                > **Важно!** Аргументы на русский не переведены."""
    }
}

example_message = {
    "name": {
        "en": ["**First example**", "**Second example**", "**Possible problems**"],
        "ru": ["**Первый пример**", "**Второй пример**", "**Возможные проблемы**"]
    },
    "value": {
        "en": [f"""For an example, you want to see top for villager trades amount.
                    You type `{prefix}villager_trade`. Bot responses you:
                    *I am not sure what you meant by `villager_trade`. There are 8 most likely variants:
                    `damage_taken`, `talked_to_villager`, `traded_with_villager`, ...*
                    You spot the variant you need *traded_with_villager* and type `{prefix}traded_with_villager`
                    Voila! Bot responses you with player top.""", 
                f"""You want to see top for amount of mined diamonds.
                    You type `{prefix}mine diamond`. Bot doesnt recognise *mine* and suggests
                    *`mine_block`, `pig_one_cm`, ...*
                    You again spot *mine_block* and type `{prefix}mine_block diamond`.
                    Voil...a?? Why do I see an empty top list?""", 
                f"""Thats because minecraft by default tracks even impossible stats.
                    It tracks *mine_block* with all existing items. Not only blocks. And you cant mine diamond item.
                    But you can mine diamond ore. So with `{prefix}mine_block diamond_ore` you get your top list.
                    
                    And you realise that you have mined way more dia ores than it shows.
                    Thats because regular diamond ore is quite rare in current version.
                    You need to add to it deepslate variant. You type `{prefix}mine_block deepslate_diamond_ore`
                    Voila! Here are your stats. 
                    *(note: if you type second argument incorrectly, bot will also suggest you correct close variants)*"""],
        "ru": [f"""Например, вы хотите увидеть топ игроков ко количеству трейдов с жителями.
                    Вы пишете `{prefix}villager_trade`. Бот вам отвечает:
                    *Я не уверен, что вы имели ввиду под `villager_trade`. Eсть 8 наиболее вероятных варианта(ов):
                    `damage_taken`, `talked_to_villager`, `traded_with_villager`, ...*
                    Вы находите в списке подходящий вариант *traded_with_villager* и пишете`{prefix}traded_with_villager`
                    Вауля! Бот отправляет вам топ игроков""", 
                f"""Вы хотите увидеть топ игроков по добытым алмазам.
                    Вводите `{prefix}mine diamond`. Но бот не понимает *mine* и предлагает
                    *`mine_block`, `pig_one_cm`, ...*
                    Опять же вы находите *mine_block* и вводите `{prefix}mine_block diamond`.
                    Вау...ля?? Почему я вижу пустой топ?""", 
                f"""Это потому, что майнкрафт отслеживает даже невозможные статистики.
                    Он отслеживает *mine_block* со всеми предметами, не только блоками. 
                    Иии вскопать предмет алмаз нельзя, зато можно алмазную руду. 
                    Введя `{prefix}mine_block diamond_ore` вы получите свой топ.
                    
                    И тут вы понимаете, что количество вскопанных руд куда меньше, чем должно быть.
                    Это из-за того, что обычная алмазная руда очень редкая, вам нужно ещё учесть deepslate(сланцевые) вариации.
                    Вводим `{prefix}mine_block deepslate_diamond_ore`
                    Вауля! Вот ваш топ 
                    *(пометка: если вы ошибетесь во втором аргументе, бот тоже будет вам его подсказывать)*"""]
    }
}

basic_commands_message = {
    "name": {
        "en": ["**Basic commands**", "*Note*"],
        "ru": ["**Базовые команды**", "*Пометка*"]
    },
    "value": {
        "en": [f""" `{prefix}mine_block <item_name>` - amount of specific block mined
                    `{prefix}use_item <item_name>` - amount of specific item used. It may be
                    blocks (means blocks placed), tools, food (times eaten), fireworks, etc.
                    `{prefix}craft_item <item_name>` - amount of specific item crafted
                    `{prefix}drop <item_name>` - amount of specific item dropped
                    `{prefix}pickup <item_name>` - amount of specific item picked up
                    `{prefix}break_item <item_name>` - amount of tool broken
                    `{prefix}mob_kills` - general amount of killed mobs
                    `{prefix}kill_entity <entity_name>` - amount of specific mob killed
                    `{prefix}entity_killed_by <entity_name>` - amount of deaths from specific mob""",
                """*these are just most used commands. 
                    As I said there are dozens of statistics that mc tracks. Hundrets of possible blocks, entities.
                    If you see something in stat game tab, you can find it here.
                    
                    If you have suggestions about command aliases, feel free to contact me in my discord server*"""],
        "ru": [f""" `{prefix}mine_block <имя_предмета>` - количество добытого определённого блока
                    `{prefix}use_item <имя_предмета>` - количество использований определённого предмета.
                    Это могут быть блоки (сколько блоков поставлено), инструменты, еда (сколько раз съели), фейрверки, итд.
                    `{prefix}craft_item <имя_предмета>` - сколько штук скрафчено определённого предмета
                    `{prefix}drop <имя_предмета>` - сколько штук выброшено определённого предмета
                    `{prefix}pickup <имя_предмета>` - сколько штук подобрано определённого предмета
                    `{prefix}break_item <имя_предмета>` - сколько штук определённой брони, инструмента сломано
                    `{prefix}mob_kills` - количество убитых мобов (всех суммарно)
                    `{prefix}kill_entity <имя_сущности>` - сколько раз был убит определённый моб
                    `{prefix}entity_killed_by <имя_сущности>` - сколько раз определённый моб убивал игрока""",
                """*Это просто список самых популярных комманд.
                    Как было сказано ранее, доступны десятки команд, сотни предметов и мобов.
                    Всё, что можно найти во вкладке меню майнкрафта 'Статистика', доступно в боте.
                    
                    Если у вас есть предложения насчёт пседонимов комманд, статистик, присылайте в дискорд сервер поддержки*"""]
    }
}

lang_switched_msg = {
    "en": "**Swithed to english!**",
    "ru": "**Переключено на русский!**"
}

command_descriptions = {
    "start": {
        "en": "Start! Call this command to start using bot",
        "ru": "Начать! Вызовите это команду для начала работы с ботом"
    },
    "set_role": {
        "en": "Sets role that is able to manage bot settings. If no role was set, everbody will be able to change bot settings!",
        "ru": "Задать роль администратора, администраторы способны изменять настройки бота. Внимание! Если роль не задана, кто угодно может хоть поменять айпи, хоть удалить сообщение!"
    },
    "set_ip": {
        "en": "Sets minecraft server ip. Bot will request player data from there",
        "ru": "Задать айпи вашего майнкрафт сервера. Бот будет запрашивать оттуда список онлайн игроков"
    },
    "cfg": {
        "en": "Shows current bot's settings",
        "ru": "Показать текущие настройки"
    },
    "help": {
        "en": "Shows help message",
        "ru": "Показать сообщение-справку"
    },
    "guide": {
        "en": "Shows guide how to use statistic commands",
        "ru": "Показать инструкцию пользования командами статистики"
    },
    "example": {
        "en": "Shows example of searching statistic",
        "ru": "Показать примеры использования и поиска команд статистики"
    },
    "commands": {
        "en": "Shows basic commands list.",
        "ru": "Показать базовые комманды статистики"
    },
    "ru": {
        "en": "Переключить язык бота на русский",
        "ru": "Переключить язык бота на русский"
    },
    "en": {
        "en": "Switch bot's language to english",
        "ru": "Switch bot's language to english"
    },
}

info_msgs = {
    "stat_arg_not_found": {
        "name": {
            "en": "I dont recognise `{user_input}`",
            "ru": "Я не знаю, что такое `{user_input}`"
        },
        "value": {
            "en": "Keep in mind that I provide only vanilla statistics. So only statistics that can be found in *Statistics* tab in minecraft menu",
            "ru": "Напоминаем, что бот предоставляет только ванильную статистику майнкрафта. Только то, что есть во вкладке *Статистика* меню майнкрафта"
        }
    },
    "stat_several_results": {
        "name": {
            "en": "I am not sure what you meant by `{user_input}`!",
            "ru": "Я не уверен, что вы имели ввиду под `{user_input}`"
        },
        "value": {
            "en": "There are **{amount}** most likely variants:\n",
            "ru": "Eсть **{amount}** наиболее вероятных варианта(ов)\n"
        }
    },
    "stat_requires_argument": {
        "name": {
            "en": "{stat} requires {argument_type} argument!",
            "ru": "{stat} требует аргумент {argument_type}!"
        },
        "value": {
            "en": "Example: `{stat} {arg}`",
            "ru": "Пример: `{stat} {arg}`"
        }
    },
    "guild_not_set_up": {
        "name": {
            "en": "**Server is not set up!**",
            "ru": "**Ваш сервер не настроен!**"
        },
        "value": {
            "en": f"Use `{prefix}start` first.",
            "ru": f"Сначала привяжите свой дискорд сервер с помощью `{prefix}start`."
        }
    },
    "guild_inited": {
        "name": {
            "en": ["**Your server was linked!**", "*Friendly reminder:*"],
            "ru": ["**Ваш сервер успешно привязан!**", "*Важное напоминание:*"]
        },
        "value": {
            "en": [ "Before calling statistic commands consider setting manager role and minecraft server ip.",
                   f"*This bot requires {BOT_NAME} plugin running on the server. Link can be found in `{prefix}help`*"],
            "ru": [ "Прежде чем вызывать комманды статистики убедитесь, что вы задали роль андинистратора и айпи майнкрафт сервера",
                   f"*Для работы этого бота вам необходимо установить плагин {BOT_NAME} на сервер. Ссылка на плагин есть в `{prefix}help`*"]
        }
    },
    "guild_alr_inited": {
        "name": {
            "en": "**Oops!**",
            "ru": "**Упс!**"
        },
        "value": {
            "en": "Your server is already linked",
            "ru": "Ваш сервер уже и так привязан!"
        }
    },
    "success": {
        "en": "**Success!**",
        "ru": "**Успех!**"
    },
    "parameter_set": {
        "en": "`{name}` was set to {val}",
        "ru": "Параметру `{name}` было задано значение {val}"
    },
    "parameters": {
        "manager_role": {
            "en": "Manager role",
            "ru": "Роль администратора"
        },
        "ip": {
            "en": "Ip",
            "ru": "айпи"
        }
    },
    "not_permitted": {
        "en": "**You are not permitted to use this command!**",
        "ru": "**У вас нет прав использовать эту комманду!**"
    },
    "invalid_syntax": {
        "en": "**Invalid syntax**",
        "ru": "**Неправильный синтаксис**"
    },
    "invalid_syntax_comments": {
        "ip_arg_missing": {
            "en": "`Ip` argument is missing",
            "ru": "Отсутствует аргумент `айпи`"
        },
        "role_arg_missing": {
            "en": "`Role` argument is missing",
            "ru": "Отсутствует аргумент `роль`"
        },
        "ip_with_port": {
            "en": "Provide us your server's ip without port, please. (Without ':' and digits after it) \n \
                    If your input was *0.0.0.0:0000* for example, then you should replace it with *0.0.0.0*",
            "ru": "Предоставьте, пожалуйста, айпи вашего сервера без порта. (Без ':' и цифр после) \n \
                    Если вы ввели, для примера, *0.0.0.0:0000*, тогда замените это на *0.0.0.0*"
        },
        "invalid_role": {
            "en": "Invalid role",
            "ru": "Несуществующая роль"
        }
    },
    "cant_connect": {
        "name": {
            "en": "**Failed to connect to minecraft server**",
            "ru": "**Не удалось подключиться к майнкрафт серверу.**"
        },
        "value": {
            "en": f"Make sure you have\n \
                    - Installed {BOT_NAME} plugin (Link can be found in `{prefix}help`)\n \
                    - Server IP is correct. Without port (without ':' and digits after) (Ссылка в `{prefix}help`)\n \
                    - Port {DEFAULT_PORT} opened on your server",
            "ru": f"Убедитесь, что вы\n \
                    - Установили плагин {BOT_NAME} (Ссылка в `{prefix}help`)\n \
                    - Айпи сервера указан корректно. Без порта, то есть без двоеточия и цифр после него\n \
                    - Порт {DEFAULT_PORT} открыт в настройках вашего сервера (уточните у хостинга, как это сделать, если не понимаете, о чём речь)"
        }
    },
    "ip_not_set": {
        "name": {
            "en": "**Set up your minecraft server's ip first!**",
            "ru": "**Сначала задайте айпи своего майнкрафт сервера!**"
        },
        "value": {
            "en": f"You need to provide me your minecraft server's ip with `{prefix}set_ip <your ip>`. Your server must have {BOT_NAME} plugin installed",
            "ru": f"Вам необходимо предоставить мне айпи вашего майнкрафт сервера с помощью `{prefix}set_ip <ваш айпи>`. На сервере должен быть установлен плагин {BOT_NAME}"
        }
    }
}

cfg_msg = {
    "mgr_field_name": {
        "en": "**Manager role**",
        "ru": "**Роль администратора**"
    },
    "ip_field_name": {
        "en": "**Server IP**",
        "ru": "**Айпи сервера**"
    },
    "missing_value": {
        "en": "Missing",
        "ru": "> Отсутствует"
    },
    "present_value": {
        "en": "Present",
        "ru": "> Присутствует"
    },
}

short_numbers = {
    "million": {
        "en": "M",
        "ru": "млн"
    },
    "thausand": {
        "en": "K",
        "ru": "тыс"
    }
}