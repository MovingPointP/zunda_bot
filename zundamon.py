import discord
from requests.api import options
import yaml
import asyncio
from voicebox import generate_wav

with open('option.yaml', encoding='utf-8') as file:
    option = yaml.safe_load(file)

token = option['token']
client = discord.Client()
emoji = '\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}'

async def leave(voice_client):
    #botが接続しているか
    if voice_client is None:
        return

    #切断する
    await voice_client.disconnect()

class LeaveClass:
    def __init__(self, guild):
        self.running_flag = False
        self.stop_flag = False
        self.count = 0
        self.guild = guild

    #タイムアウト処理
    async def count_for_leave(self):
        self.running_flag = True
        max_count = option['timeout'] - 1
        while True:
            await asyncio.sleep(1)
            self.count += 1
            print(self.count)
            if self.stop_flag or self.count > max_count:
                break
        
        await leave(self.guild.voice_client)
        self.running_flag = False
        self.stop_flag = False
        self.count = 0

    def count_reset(self):
        self.count = 0

    def stop_task(self):
        self.stop_flag = True

    def check_running(self):
        return self.running_flag

@client.event
async def on_message(message):
    
    #botは無視
    if message.author.bot:
        return

    user = message.author

    #インスタンス生成
    if 'leave_class' not in globals():
        global leave_class
        leave_class = LeaveClass(message.guild)
    
    #contentの先頭を調べる
    contents = message.content.split()

    #入室処理
    if contents[0] in option['join']:

        #userがボイスチャンネルにいるか
        if user.voice is None:
            return

        #botが接続しているか
        if message.guild.voice_client is None:
            #ボイスチャンネルに接続
            channel = user.voice.channel
            await channel.connect()

        #ずんだもんのタイムアウト処理
        if leave_class.check_running():
            leave_class.count_reset()
        else:
            asyncio.ensure_future(leave_class.count_for_leave())

        #textはあるか
        if len(contents) > 1:

            #リアクション
            await message.add_reaction(emoji)

            text = ' '.join(contents[1:])
            text = user.nick + ' ' + text
            #40文字以下にカット
            if len(text) > 40:
                text = text[:40]

            #音声を再生
            generate_wav(text)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("audio.wav"), volume=0.5)
            message.guild.voice_client.play(source)

            #リアクション取り消し
            await message.remove_reaction(emoji, client.user)
    
    #切断処理
    elif contents[0] == option['leave']:
        leave_class.stop_task()

@client.event
async def on_ready():
    print('Botでログインしました')

    #アクティビティの変更
    activity = discord.Activity(
        name=option['join'][0] + ' ', type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)

client.run(token)
