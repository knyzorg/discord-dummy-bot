import discord
import signal
import os
from multiprocessing import Process
import time

DISCORD_TOKENS = list()

if "DISCORD_TOKENS" in os.environ:
    DISCORD_TOKENS = os.environ['DISCORD_TOKENS'].split(" ")


class DummyClient(discord.Client):

    def __init__(self, name, intents=None):
        super().__init__(intents=intents)
        self.name = name

    async def on_message(self, message):
        if message.channel.type == discord.channel.ChannelType.text:
            args = message.content.strip().split(' ')
            if args[0] in ("<@!{0}>".format(self.user.id), "<@{0}>".format(self.user.id)):
                if len(args) > 1:
                    # Command to force the bot to join your channel
                    if args[1] == "join":
                        channel = None
                        for channel in message.guild.channels:
                            if isinstance(channel, discord.VoiceChannel):
                                for member in channel.members:
                                    if member.id == message.author.id:
                                        for voice_channel in self.voice_clients:
                                            if message.guild.id == voice_channel.guild.id:
                                                await voice_channel.disconnect(force=True)
                                                break
                                        await channel.connect()
                                        break
                    if args[1] == "leave":
                        for voice_channel in self.voice_clients:
                            await voice_channel.disconnect(force=True)
                            break

    async def on_ready(self):
        print(f"[{self.name}] Discord client loaded")

    async def on_connect(self):
        print(f"[{self.name}] connected to Discord")

    async def on_disconnected(self):
        print(f"[{self.name}] disconnected from Discord")

    def stop(self):
        self.close()
        exit()


def connect(token, number):
    intents = discord.Intents.default()
    intents.members = True
    client = DummyClient(f"DUMMYBOT #{number}", intents=intents)
    reconnectDelay = 10
    while True:
        try:
            client.run(token)
        except RuntimeError:
            print(f"[DUMMYBOT #{number}] Shutting down...")
            break
        except Exception as e:
            print(
                f"[DUMMYBOT #{number}] Failed to connect due to {type(e).__name__} exception")
            print(f"Waiting {reconnectDelay} seconds and reconnecting...")
            time.sleep(reconnectDelay)
            reconnectDelay = reconnectDelay * 2


# MAIN ------------------------------------------
if __name__ == "__main__":
    print("[DUMMYBOT] Discord started")

    processes = list()
    counter = 0
    for t in DISCORD_TOKENS:
        counter = counter + 1
        # Discord bot intents
        p = Process(target=connect, args=(t, counter))
        processes.append(p)
        p.start()

    print(f"[DUMMYBOT] Created {counter} bots")

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("[DUMMYBOT] Shutting down")

    print("[DUMMYBOT] terminated")
