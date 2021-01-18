import discord
import os
import sqlite3
from discord.utils import get

conn = sqlite3.connect('completions.db')

db = conn.cursor()


roles = {10:'Novice Puzzler', 50:'Apprentice Puzzler', 100:'Intermediate Puzzler', 300:'Proficient Puzzler', 600:'Expert Puzzler', 1000:'Master Puzzler'}

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$!puzzlecomplete'):
        await message.channel.send('Good job {0.mention}! Adding that to the records!'.format(message.author.id))
        puzzles_completed = db.execute("SELECT puzzles_completed FROM users where username = :user_id", user_id = message.author.id)
        puzzles_completed = puzzles_completed + 1
        if roles[puzzles_completed]:
            role = get(message.server.roles, name = roles[puzzles_completed])
            await client.add_roles(message.author, role)
        db.execute("UPDATE users SET puzzles_completed = :puzzles_completed WHERE user_id = :user_id ", puzzles_completed = puzzles_completed, user_id = message.author.id)

    if message.content.startswith('$!completed'):
        puzzles_completed = db.execute("SELECT puzzles_completed FROM users where username = :user_id", user_id = message.author.id)
        await message.channel.send('You have completed {} puzzles!')

conn.close()

client.run(os.getenv('TOKEN'))