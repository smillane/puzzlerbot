import discord
import os
import sqlite3
from discord.utils import get


def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()

conn = sqlite3.connect('completions.db')

db = conn.cursor()


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

    if message.content.startswith('!puzzlecomplete'):
        await message.channel.send('Good job {}! Adding that to the records!'.format(message.author.name))
        username = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id = message.author.id)
        if len(username) == 1:
            puzzles_completed = db.execute("SELECT puzzles_completed FROM users where username = :user_id", user_id = message.author.id)
            puzzles_completed = puzzles_completed + 1
            if roles[puzzles_completed]:
                role = get(message.server.roles, name = roles[puzzles_completed])
                await client.add_roles(message.author, role)
            db.execute("UPDATE users SET puzzles_completed = :puzzles_completed WHERE user_id = :user_id ", puzzles_completed = puzzles_completed, user_id = message.author.id)
        else:
            db.execute("INSERT INTO users (user_id) VALUES (:user_id)", user_id = message.author.id)

    if message.content.startswith('!completed'):
        username = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id = message.author.id)
        if len(username) == 1:
            puzzles_completed = db.execute("SELECT puzzles_completed FROM users where user_id = :user_id", user_id = message.author.id)
            await message.channel.send('You have completed {} puzzles!'.format(puzzles_completed))
        else:
            await message.channel.send("You haven't completed any puzzles yet!")

conn.close()

client.run(token)