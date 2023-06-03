from discord import Client, Intents

from app.StatApp import StatApp
from aftoken import af_token
from app.src.Logger import Logger

class AfClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app: StatApp = False

    def initApp(self):
        self.app = StatApp(self)

    async def on_message(self, message):
        if not self.app:
            self.initApp()
        await self.app.onMessage(message)

intents = Intents.default()
intents.message_content = True

client = AfClient(intents = intents)

client.run(af_token)
