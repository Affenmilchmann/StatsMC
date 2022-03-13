from discord import Client

from StatApp import StatApp
from aftoken import af_token
from Logger import Logger

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

client = AfClient()

try:
    client.run(af_token)
except Exception as e:
    Logger.printLog(f"Crashed. Error: {e}", error=True)