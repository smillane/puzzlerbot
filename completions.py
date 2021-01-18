import discord
import os
import psycopg2
from discord.utils import get
from config import config


def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()

params = config()

conn = psycopg2.connect(**params)

db = conn.cursor()

db.execute('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, puzzles_completed INTEGER NOT NULL DEFAULT 0)''')

roles = {10:'Novice Puzzler', 50:'Apprentice Puzzler', 100:'Intermediate Puzzler', 300:'Proficient Puzzler', 600:'Expert Puzzler', 1000:'Master Puzzler'}

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send_message(f"""Welcome to the server {member.mention}""")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    userid = message.author.id

    if message.content.startswith('!puzzlecomplete'):
        await message.channel.send('Good job {}! Adding that to the records!'.format(message.author.name))
        username = db.execute("SELECT * FROM users WHERE user_id = userid")
        if len(username) == 1:
            puzzles_completed = db.execute("SELECT puzzles_completed FROM users WHERE user_id = userid")
            puzzles_completed = puzzles_completed + 1
            db.execute("UPDATE users SET puzzles_completed = :completed WHERE user_id = userid", completed = puzzles_completed)
            conn.commit()
            if roles[puzzles_completed]:
                role = get(message.server.roles, name = roles[puzzles_completed])
                await client.add_roles(message.author, role)            
            await message.channel.send('test')
        else:
            db.execute("INSERT INTO users (user_id, puzzles_completed) VALUES (user_id = userid, :puzzles_completed)", puzzles_completed = 1)
            conn.commit()
            await message.channel.send('you have been added')

    if message.content.startswith('!completed'):
        username = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id = userid)
        if len(username) == 1:
            puzzles_completed = db.execute("SELECT puzzles_completed FROM users WHERE user_id = userid")
            await message.channel.send('You have completed {} puzzles!'.format(puzzles_completed))
        else:
            await message.channel.send('You have not completed any puzzles yet!')

client.run(token)