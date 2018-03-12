#! /usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
import datetime
import configparser

bot = commands.Bot(command_prefix='$', description='h')

config = configparser.ConfigParser()
config.read('config.ini')
token = config['keys']['discord']
general_channel_id = config['chan_id']['general']

class Event(object):
    dt = 0
    str = ""
    desc = ""

    def __init__(self, datetime, desc : str):
        self.dt = datetime
        self.str = datetime.strftime("%Hh%M %d/%m/%Y")
        self.desc = desc


async def check_event():
    await bot.wait_until_ready()
    channel = discord.Object(general_channel_id)
    today = datetime.datetime.today()
    margin = datetime.timedelta(days = 3)
    event_tab = []
    for line in open('dates'):
        data = line.split("###")
        date = datetime.datetime.strptime(data[0], '%H:%M %d/%m/%Y')
        desc = data[1].rstrip('\n')
        obj = Event(date, desc)
        if (today <= obj.dt <= today + margin):
            event_tab.append(obj)
    while not bot.is_closed:
        for item in event_tab:
            await bot.send_message(channel, "You have a rendez-vous planned at : " + item.str + "\n \"" + item.desc + "\"")
        await bot.send_message(channel, "@everyone, look at this reminder !")
        await asyncio.sleep(86400) # task will run every day - 86400 sec

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def new_rdv(*args):
    d = datetime.datetime.strptime(' '.join(args), '%H:%M %d/%m/%Y')
    e = Event(d, "Haha la desc")
    with open('dates', 'a') as file:
        file.write(e.str + '###' + e.desc + '\n')
    await bot.say("New Rendezvous is set at : " + e.str + "\n \"" + e.desc + "\"")

bot.loop.create_task(check_event())
bot.run(token)
