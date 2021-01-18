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

db.execute("""CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, user_id BIGINT NOT NULL, puzzles_completed INTEGER NOT NULL DEFAULT 0)""")

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
        db.execute("""SELECT * FROM users WHERE user_id = %s""", (userid,))
        if db.fetchone():
            db.execute("""UPDATE users SET puzzles_completed + 1 WHERE user_id = %s;""", (userid,))
            conn.commit()
            db.execute("""SELECT puzzles_completed FROM users WHERE user_id = %s""", (userid,))
            puzzles_completed = db.fetchone()
            if roles[puzzles_completed]:
                role = get(message.server.roles, name=roles[puzzles_completed])
                await userid.add_roles(role)
            await message.channel.send('plus 1!!')
        else:
            db.execute("""INSERT INTO users (puzzles_completed, user_id) VALUES (%s, %s);""", (1, userid))
            conn.commit()
            await message.channel.send('you have been added')

    if message.content.startswith('!completed'):
        db.execute("""SELECT puzzles_completed FROM users WHERE user_id = %s""", (userid,))
        puzzles_completed = db.fetchone()
        if puzzles_completed > 0:
            puzzles_completed = db.fetchone()
            await message.channel.send('You have completed {} puzzles!'.format(puzzles_completed))
        else:
            await message.channel.send('You have not completed any puzzles yet!')

client.run(token)