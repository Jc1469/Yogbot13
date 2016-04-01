import discord
import queue
import os.path
from threading import Thread
import time

class AudioManager:

    def __init__(self, bot, name):
        self.bot = bot
        self.name = name
        self.player = None
        self.playlist = queue.Queue(maxsize=10)
        self.looping = False

        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus.dll')
        thread = Thread(target=self.loop, args=())
        thread.start()

    def loop(self):
        if self.looping:
            return
        while True:
            if not self.bot.is_voice_connected():
                continue

            if self.playlist.qsize() == 0:
                continue
            if self.is_playing():
                continue
            got = self.playlist.get()
            self.play(got)

    async def connect_to_channel(self, channel_name, message):
        if self.bot.is_voice_connected():
            self.disconnect_from_channel()
            return
        check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
        channel = discord.utils.find(check, message.server.channels)
        if channel is None:
            return
        else:
            await self.bot.join_voice_channel(channel)
           # self.starter = message.author

    def disconnect_from_channel(self):
        if self.bot.is_voice_connected():
           # await bot.send_message(message.channel, 'Already disconnected from a voice channel')
            return
        self.bot.voice.disconnect()

    def play(self, filename):

        if(self.is_playing()):
            return
        self.player = self.bot.voice.create_ffmpeg_player(filename)
        self.player.start()

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    async def play_vox(self, message):
        await self.connect_to_channel(message.channel.name, message)
        words = message.content.split(' ')[1:]
        unrecognized_vox_sounds = list()
        for word in words:
            print("config/wavs/vox/" + word + ".ass")
            if os.path.exists("config/wavs/vox/" + word + ".ogg") == False:
                unrecognized_vox_sounds.append(word)
                print(unrecognized_vox_sounds)

        if len(unrecognized_vox_sounds) >= 1:
            msg = "I did not understand the following words: "
            msg += ", ".join(unrecognized_vox_sounds)
            await self.bot.send_message(message.channel, msg)
            return

        #words.reverse()
        for word in words:
            self.playlist.put("config/wavs/vox/" + word + ".ogg")