import discord
import socket
import struct
import random
import yaml
import os
import json
from audio import AudioManager
from permissions_manager import PermissionsManager
from urllib import parse

address = 'localhost'
port = 25565
key = 'default_pwds'
token = 'token'

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus.dll')


def load_config():
    config = None
    with open("config/config.yml", 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    global address
    global port
    global key
    global token
    address = config['address']
    port = config['port']
    key = config['key']
    token = config['token']

class Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.starter = None
        self.player = None
        self.current = None
        self.audio = AudioManager(self, 'test name')
        self.permissions = PermissionsManager()
        self.database_connection = None

    def connect_to_database(self):
        return 1

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == self.user:
            return

        words = message.content.split(' ')

        if message.channel.is_private == 0:
            if message.channel.name == "asay":
                ping_message = bytes("asay={0}&admin={1}&key={2}".format(message.content, message.author.name, key), "utf-8")
                ping_server(ping_message)
        if words[0][0] == "!":
            if message.content.startswith('!ooc'):
                msg = 'Successfully sent OOC message.'
                if not self.permissions.has_permissions(message.author, 'ooc'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                ping_message = bytes("ooc={0}&admin={1}&key={2}".format(' '.join(words[1:]), message.author.name, key), "utf-8")
                ping_server(ping_message)
                await self.send_message(message.channel, msg)
                return
            if words[0] == "!reboot":
                if not self.permissions.has_permissions(message.author, 'reboot'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                if len(words) == 1:
                    await self.send_message(message.channel, "Available Reboot Options:\n    `!reboot soft` - Tells the server to restart.\n    `!reboot hard` - Forces the server to reboot by killing the daemon(Daemon must have a restart script for this to work).")
                    return
                if words[1] == "soft":
                    ping_server(bytes("reboot=1&key={0}".format(key), "utf-8"))
                    await self.send_message(message.channel, 'Soft reboot started.')
                    return
                if words[1] == "hard":
                    os.system('taskkill /F /IM dreamdaemon.exe')
                    await self.send_message(message.channel, 'Hard reboot started.')
                    return
                await self.send_message(message.channel, "I did not recognize that option. Try using `!reboot` to see the available options.")
            if words[0] == "!ticket":
                ping_message = None
                if not self.permissions.has_permissions(message.author, 'ticket'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                if len(words) == 1:
                    await self.send_message(message.channel, "Available Ticket Commands:\n    `!ticket list` - Lists current tickets.\n    `!ticket log (ticket_id)` - shows the log for the chosen ticket id.\n    `!ticket reply (ticket_id) (reply message)` - Sends a reply to the ticket.")
                    return
                if words[1] == "list":
                    ping_message = bytes("ticket=1&action=list&key={0}".format(key), "utf-8")
                if words[1] == "log":
                    if len(words) < 3:
                        await self.send_message(message.channel, "You must specify a ticket as a NUMBER.")
                        return
                    ping_message = bytes("ticket=1&action=log&id={0}&key={1}".format(words[2], key), "utf-8")
                if words[1] == 'reply':
                    if len(words) < 4:
                        await self.send_message(message.channel, "You must specify a ticket as a NUMBER and give a reply message.")
                        return
                    ping_message = bytes("ticket=1&action=reply&id={0}&admin={1}&response={2}&key={3}".format(words[2], message.author.name, ' '.join(words[3:]), key), "utf-8")
                if ping_message is None:
                    await self.send_message(message.channel, "Sorry, I did not recognize that ticket command. Try using `!ticket` to see the available ticket commands.")
                    return
                ping_message = ping_server(ping_message)
                await self.send_message(message.channel, ping_message)
                return
            if message.content.startswith('!adminwho'):
                if not self.permissions.has_permissions(message.author, 'adminwho'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                ping_count = ping_server(b"adminwho")
                if ping_count == -1:
                    await self.send_message(message.channel, 'Failed to ping the server.')
                    return
                await self.send_message(message.channel, ping_count)
                return
            if message.content.startswith('!who'):
                msg = 'Feature not done yet.'.format(message)
                await self.send_message(message.channel, msg)
                return
            if message.content.startswith('!ping'):
                if not self.permissions.has_permissions(message.author, 'ping'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                ping_count = ping_server(b"ping")
                if ping_count == -1:
                    await self.send_message(message.channel, 'Failed to ping the server.')
                    return
                await self.send_message(message.channel, "Sighs! Theres " + str(ping_count-1) + " players online!")
                return
            if message.content.startswith('!fox'):
                if not self.permissions.has_permissions(message.author, 'fox'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                line = random.choice(open('config/foxes.txt', 'r').readlines())
                await self.send_message(message.channel, line)
                return
            if message.content.startswith('!hardy'):
                if not self.permissions.has_permissions(message.author, 'hardy'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                line = random.choice(open('config/hardy.txt', 'r').readlines())
                await self.send_message(message.channel, line)
                return
            if message.content.startswith('!corgi'):
                if not self.permissions.has_permissions(message.author, 'corgi'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                line = random.choice(open('config/corgi.txt', 'r').readlines())
                await self.send_message(message.channel, line)
                return
            if message.content.startswith('!wolf'):
                if not self.permissions.has_permissions(message.author, 'wolf'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                line = random.choice(open('config/foxes.txt', 'r').readlines())
                await self.send_message(message.channel, "Wolves are nice. But foxes are better")
                await self.send_message(message.channel, line)
                return
            if message.content.startswith('!meme'):
                if not self.permissions.has_permissions(message.author, 'meme'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                line = random.choice(open('config/memes.txt', 'r').readlines())
                await self.audio.connect_to_channel(message.channel.name, message)
                await self.audio.play("config/wavs/" + line.rstrip("\n") + '.wav')
                return
            if message.content.startswith('!vox'):
                if not self.permissions.has_permissions(message.author, 'vox'):
                    await self.send_message(message.channel, 'You dont have permissions to do that.')
                    return
                await self.audio.play_vox(message)
                return
            if message.content.startswith('!help'):
                msg = 'Available commands:'
                msg += "\n    `!adminwho` - Displays current admins in-game"
                msg += "\n    `!ping` - Displays a nice message."
                msg += "\n    `!fox` - Displays cute pictures."
                msg += "\n    `!meme` - Warning. Incredibly lame. Only works in General Voice channel."
                msg += "\n    `!vox` - Works like the ais announcement system. Currently only works in public voice channel."
                msg += "\nAdmin Commands:"
                msg += "\n    `!ooc` - Sends a OOC message."
                msg += "\n    `!reboot` - Trigger a server reboot. Use at your own risk."
                msg += "\n    `!ticket` - Ticket commands for viewing and answering tickets."
                msg += "\nSending a message in the #asay channel will broadcast it in-game"
                msg = msg.format(message)
                await self.send_message(message.channel, msg)
                return
            await self.send_message(message.channel, "I did not recognize that command. Try using !help to see the available commands.")
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def on_socket_closed(self):
        self.run(token)

def decode_packet(packet):
    print(str(packet))
    print(packet)
    if packet != "":
        if b"\x00" in packet[0:2] or b"\x83" in packet[0:2]:
            sizebytes = struct.unpack('>H', packet[2:4])  # array size of the type identifier and content # ROB: Big-endian!
            size = sizebytes[0] - 1  # size of the string/floating-point (minus the size of the identifier byte)
            if b'\x2a' in packet[4:5]:  # 4-byte big-endian floating-point
                unpackint = struct.unpack('f', packet[5:9])  # 4 possible bytes: add them up together, unpack them as a floating-point

                return int(unpackint[0])
            elif b'\x06' in packet[4:5]:  # ASCII string
                unpackstr = ''  # result string
                index = 5  # string index
                indexend = index + size

                string = packet[5:indexend].decode("Windows-1252")
                string = string.replace('\x00', '')

                return string
    return None


def ping_server(question):
    try:
        query = b'\x00\x83'
        query += struct.pack('>H', len(question) + 6)
        query += b'\x00\x00\x00\x00\x00'
        query += question
        query += b'\x00'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
        s.settimeout(30)

        if s == None:
            return None

        s.sendall(query)

        data = b''
        while True:
            buf = s.recv(1024)
            data += buf
            szbuf = len(buf)
            if szbuf < 1024:
                break

        s.close()

        response = decode_packet(bytes(data))

        return response
    except socket.timeout:
        return None
    except socket.error:
        return None

def is_admin_channel(channel):
    if channel.is_private == 0:
        if channel.name == "admin" or channel.name == "important-admin":
            return 1
    return 0

load_config()

bot = Bot()

try:
    bot.run(token)
except Exception:
    os.system('taskkill /F /PID %d' % os.getpid())
