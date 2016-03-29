import discord
from discord.ext import commands
import socket
import struct
import random

client = discord.Client()
address = 'localhost'
port = 25565
key = 'password'
email = 'canttouchthis@nahnahnah.nah'
password = 'canttouchthis'

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    words = message.content.split(' ')

    if message.channel.is_private == 0:
        if message.channel.name == "asay":
            ping_message = bytes("asay={0}&admin={1}&key={2}".format(message.content, message.author.name, key), "utf-8")
            ping_server(ping_message)
    if words[0][0] == "!":
        if message.content.startswith('!ooc'):
            if message.channel.name == "admin":
                await client.send_message(message.channel, "TODO")
            else:
                msg = ('This command may only be used on the admin channel. You are on ' + message.channel.name).format(message)
            await client.send_message(message.channel, msg)
            return
        if message.content.startswith('!adminwho'):
            ping_count = ping_server(b"adminwho")
            if ping_count == -1:
                await client.send_message(message.channel, 'Failed to ping the server.')
                return
            await client.send_message(message.channel, ping_count)
            return
        if message.content.startswith('!who'):
            msg = 'Feature not done yet.'.format(message)
            await client.send_message(message.channel, msg)
            return
        if message.content.startswith('!ping'):
            ping_count = ping_server(b"ping")
            if ping_count == -1:
                await client.send_message(message.channel, 'Failed to ping the server.')
                return
            await client.send_message(message.channel, "Pong! Theres " + str(ping_count-1) + " players online!")
            return
        if message.content.startswith('!admincheck'):
            if message.channel.name == "admin":
                msg = 'You are on the admin channel.'.format(message)
            else:
                msg = ('You are not on the admin channel. You are on ' + message.channel.name).format(message)
            await client.send_message(message.channel, msg)
            return
        if message.content.startswith('!fox'):
            line = random.choice(open('config/foxes.txt', 'r').readlines())
            await client.send_message(message.channel, line)
            return
        if message.content.startswith('!help'):
            msg = 'Available commands:'
            msg += "\n    !adminwho - Displays current admins in-game"
            msg += "\n    !ping - Displays a nice message."
            msg += "\nAdmin Commands(Must be used in the admin channel. Ill setup a better system later <-- Oisin.):"
            msg += "\n    !ooc - Sends a OOC message."
            msg += "\nSending a message in the #asay channel will broadcast it in-game"
            msg = msg.format(message)
            await client.send_message(message.channel, msg)
            return
        await client.send_message(message.channel, "I did not recognize that command. Try using !help to see the available commands.")
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

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

                string = packet[5:indexend].decode("utf-8")
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
        s.connect(('localhost', 25565))
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

        if response != None:
            if isinstance(response, int) == True or (response.find('&') + response.find('=') == -2):
                return response
            else:
                parsed_response = {}
                for chunk in response.split('&'):
                    chunk = chunk.replace("+", " ")
                    dat = chunk.split('=')
                    parsed_response[dat[0]] = ''
                    if len(dat) == 2:
                        parsed_response[dat[0]] = parse.unquote(dat[1])

                    return parsed_response
        else:
            return None
    except socket.timeout:
        return None
    except socket.error:
        return None

client.run(email, password)
