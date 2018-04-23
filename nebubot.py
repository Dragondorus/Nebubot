#! /usr/bin/env python3

import discord, asyncio, datetime, configparser, csv, os, pytz
from discord.ext import commands


#doc api discord http://discordpy.readthedocs.io/en/latest/api.html
#doc discord.py https://discordpy.readthedocs.io/en/rewrite/index.html

bot = commands.Bot(command_prefix='.', description='help')

#on pars le fichier config pour recup les infos que l'on a besoin pour se connecter
config = configparser.ConfigParser()
config.read('config.ini')
token = config['keys']['discord_nebula']
general_channel_id = config['chan_id']['test']

class Event(object):
    dt = 0
    str = ""
    desc = ""

    def __init__(self, datetime, desc : str):
        self.dt = datetime
        self.str = datetime.strftime("%Hh%M %d/%m/%Y")
        self.desc = desc

def dele(id):
    line_nbr = int(id)
    max_line = sum(1 for line in open('dates.csv'))
    if line_nbr >= max_line:
        return
    with open("dates.csv", "r") as inp, open ("new.csv", "w", newline='') as out:
        old_csv = csv.reader(inp)
        new_csv = csv.writer(out)

        line_list = list(old_csv)
        del line_list[line_nbr]
        x = 0
        while x < (max_line - 1):
            line_list[x][0] = str(x)
            x = x + 1
        new_csv.writerows(line_list)
    os.remove('dates.csv')
    os.rename('new.csv' ,'dates.csv')
    inp.close()
    out.close()

async def check_event():
    await bot.wait_until_ready()
    today = datetime.datetime.today()
    margin = datetime.timedelta(days = 3)
    event_tab = []
    id = 0
       


    while not bot.is_closed:
        for row in csv.reader(open('dates.csv', 'r')):
            date = datetime.datetime.strptime(row[1], '%Hh%M %d/%m/%Y')
            desc = row[2]
            obj = Event(date, desc)
            if (today <= obj.dt <= today + margin):
                event_tab.append(obj)
            elif (today > obj.dt):
                id = row[0]
                dele(id)
        for item in event_tab:
            await bot.send_message(discord.Object(id=general_channel_id), "@everyone, look at this reminder !"
								   " You have a rendezvous planned at : " + item.str + "\n *" + item.desc + "*")
        await asyncio.sleep(86400) # task will run every day - 86400 sec


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def ping(*args):
    """Ping Pong"""
    await bot.say(":ping_pong: Pong!")


@bot.command(aliases=['add_rdv'])
async def new_rdv(*args):
    """To add a new Rendezvous: .new_rdv H:M d/m/Y \"Description\""""
    seq = (args[0], args[1])
    line_count = sum(1 for line in open('dates.csv'))
    try:
        d = (datetime.datetime.strptime(' '.join(seq), '%H:%M %d/%m/%Y'))
        with open('dates.csv', 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            if len(args)>2:
                spamwriter.writerow([str(line_count)] + [d.strftime("%Hh%M %d/%m/%Y")] + [args[2]])
            else:
                spamwriter.writerow([str(line_count)] + [d.strftime("%Hh%M %d/%m/%Y")] + ["No description was given for this Rendezvous"])
        await bot.say("The new Rendezvous was correctly added to the list.\n")
        csvfile.close()
    except ValueError:
        await bot.say("Error: The date format you entered is invalid\n")

@bot.command(aliases=['modify_rdv'])
async def mod_rdv():
    """To modify a Rendezvous: .mod_rdv ID"""
    await bot.say("lol")

@bot.command(aliases=['list_rdv', 'all_rdv', 'see_rdv', 'look_rdv'])
async def check_rdv():
    """To check the list of Rendezvous: .check_rdv"""
    with open('dates.csv', 'r') as liste_rdv, open('temp.txt', 'a') as tempf:
        liste_csv = csv.reader(liste_rdv)
        for row in liste_csv:
            tempf.write("ID: " + row[0] + " | Date: " + row[1] + " | Description: " + row[2] + "\n")
    tempf.close()
    with open('temp.txt', 'r') as tempf:         
        await bot.say(tempf.read())
    os.remove('temp.txt')
    liste_rdv.close()

@bot.command(aliases=['delete_rdv', 'remove_rdv'])
async def del_rdv(*args):
    """"To delete a Rendezvous: .del_rdv ID"""
    line_nbr = int(args[0])
    max_line = sum(1 for line in open('dates.csv'))
    await bot.say("Deleting Rendezvous number " + args[0] + "\n...\n")
    if line_nbr >= max_line:
        await bot.say("There is no Rendezvous with this ID. Use /check_rdv to see the list of Rendezvous and their ID\n")
        return
    with open("dates.csv", "r") as inp, open ("new.csv", "w", newline='') as out:
        old_csv = csv.reader(inp)
        new_csv = csv.writer(out)

        line_list = list(old_csv)
        del line_list[line_nbr]
        x = 0
        while x < (max_line - 1):
            line_list[x][0] = str(x)
            x = x + 1
        new_csv.writerows(line_list)
    os.remove('dates.csv')
    os.rename('new.csv' ,'dates.csv')
    inp.close()
    out.close()
    await bot.say("Done !\n")

@bot.command()
async def time():
    """To see the different timezones of each member: .time"""
    k = 0
    utc_time = datetime.datetime.utcnow()
    tz_paris = pytz.timezone('Europe/Paris')
    tz_xian = pytz.timezone('Asia/Shanghai')
    tz_tomsk = pytz.timezone('Asia/Novosibirsk')
    tz_incheon = pytz.timezone('Asia/Seoul')
    Paris = pytz.utc.localize(utc_time, is_dst=None).astimezone(tz_paris)
    Tomsk = pytz.utc.localize(utc_time, is_dst=None).astimezone(tz_tomsk)
    Xian = pytz.utc.localize(utc_time, is_dst=None).astimezone(tz_xian)
    Incheon = pytz.utc.localize(utc_time, is_dst=None).astimezone(tz_incheon)
    tab = [Paris, Tomsk, Xian, Incheon]
    tab2 = ["Paris", "Tomsk", "Xian", "Incheon"]
    
    while (k <= 3):
        if (tab2[k] == "Paris"):
            tmp = tab[k].strftime("Paris / Bruxelles / Hot / Stockholm:  %Hh %Mm %Ss\n")
        else:
            tmp = tmp + tab[k].strftime(tab2[k] + ": %Hh %Mm %Ss\n")
        k += 1
    await bot.say(tmp)

bot.loop.create_task(check_event())
bot.run(token)
#await bot.change_presence(game=discord.Game(name='Nebula'))