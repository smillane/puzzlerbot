import discord
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

db.execute("""CREATE TABLE IF NOT EXISTS users (user_id BIGINT NOT NULL UNIQUE, puzzles_completed INTEGER NOT NULL DEFAULT 1);""")

roles = {5:'Novice Puzzler', 10:'Apprentice Puzzler', 15:'Intermediate Puzzler', 20:'Proficient Puzzler', 25:'Expert Puzzler', 30:'Master Puzzler'}

client = discord.Client())

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
        
        db.execute("""
        INSERT INTO users (user_id, puzzles_completed) 
        VALUES (%s, 1) 
        ON CONFLICT (user_id) DO 
        UPDATE SET puzzles_completed = users.puzzles_completed + 1;""", (userid,))
        conn.commit()
        await message.channel.send('Good job {}! Adding that to the records!'.format(message.author.name))
        db.execute("""SELECT puzzles_completed FROM users WHERE user_id = %s""", (userid,))
        puzzles_completed = db.fetchone()[0]
        if puzzles_completed in roles:
            name = roles[puzzles_completed]
            role = discord.utils.get(message.guild.roles, name=name)
            await message.author.add_role(role)
            await message.channel.send('Congrats on the new role!!!')

    if message.content.startswith('!completed'):
        db.execute("""SELECT * FROM users WHERE user_id = %s""", (userid,))
        if db.fetchone():
            db.execute("""SELECT puzzles_completed FROM users WHERE user_id = %s""", (userid,))
            puzzles_completed = db.fetchone()[0]
            await message.channel.send('You have completed {} puzzles!'.format(puzzles_completed))
        else:
            await message.channel.send('You have not completed any puzzles yet!')

client.run(token)