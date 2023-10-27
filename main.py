import asyncio

import discord
from discord.ext import tasks, commands
from datetime import datetime, timezone, timedelta

TOKEN = 'TOKEN'
CHANNEL_ID = 'CHANNEL_ID'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

jp_weekday = ["月", "火", "水", "木", "金", "土", "日"]

# ** Normal Schedule **
# boss_schedule = {
#     '01:29': {'月': 'クザカ/ヌーベル', '火': 'クザカ/ヌーベル', '水': 'クザカ/ヌーベル', '木': 'カランダ/クザカ', '金': 'カランダ/クザカ', '土': 'ガーモス', '日': 'ガーモス'},
#     '10:59': {'月': 'クザカ/カランダ', '火': 'クザカ/ヌーベル', '水': None, '木': 'クザカ/クツム', '金': 'クザカ/ヌーベル', '土': 'クザカ/ヌーベル', '日': 'クツム/カランダ'},
#     '13:59': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': 'ガーモス', '金': 'ガーモス', '土': 'オピン', '日': 'ベル'},
#     '15:59': {'月': 'クツム/クザカ', '火': 'クツム/クザカ', '水': 'クツム/ヌーベル', '木': 'クツム/ヌーベル', '金': 'クツム/ヌーベル', '土': 'クツム/カランダ', '日': 'クツム/カランダ'},
#     '18:59': {'月': 'カランダ/ヌーベル', '火': 'クツム/ヌーベル', '水': 'カランダ/クザカ', '木': 'ガーモス', '金': 'ギュント/ムラカ', '土': 'ガーモス', '日': 'ガーモス'},
#     '22:29': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': None, '金': 'ガーモス', '土': None, '日': 'ギュント/ムラカ'},
#     '22:59': {'月': 'クツム/カランダ', '火': 'カランダ/ヌーベル', '水': 'オピン', '木': 'ベル', '金': 'クツム/カランダ', '土': None, '日': 'オピン'},
#     '15:48': {'土': 'テストボス'}
# }

# ** Spooky Schedule **
boss_schedule = {
    '00:29': {'月': '童心12号', '火': 'イザベラ', '水': '童心12号', '木': 'イザベラ', '金': '童心12号' ,'土': 'イザベラ', '日': '童心12号'},
    '01:29': {'月': 'クザカ/ヌーベル', '火': 'クザカ/ヌーベル', '水': 'クザカ/ヌーベル', '木': 'カランダ/クザカ', '金': 'カランダ/クザカ', '土': 'ガーモス', '日': 'ガーモス'},
    '10:59': {'月': 'クザカ/カランダ', '火': 'クザカ/ヌーベル', '水': None, '木': 'クザカ/クツム', '金': 'クザカ/ヌーベル', '土': 'クザカ/ヌーベル', '日': 'クツム/カランダ'},
    '13:59': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': 'ガーモス', '金': 'ガーモス', '土': 'オピン', '日': 'ベル'},
    '14:39': {'月': None, '火': None, '水': None, '木': None, '金': None, '土': '童心12号', '日': None},
    '14:59': {'月': 'イザベラ', '火': '童心12号', '水': 'イザベラ', '木': '童心12号', '金': 'イザベラ' ,'土': None, '日': 'イザベラ'},
    '15:59': {'月': 'クツム/クザカ', '火': 'クツム/クザカ', '水': 'クツム/ヌーベル', '木': 'クツム/ヌーベル', '金': 'クツム/ヌーベル', '土': 'クツム/カランダ', '日': 'クツム/カランダ'},
    '17:59': {'月': '童心12号', '火': 'イザベラ', '水': '童心12号', '木': 'イザベラ', '金': '童心12号' ,'土': 'イザベラ', '日': '童心12号'},
    '18:59': {'月': 'カランダ/ヌーベル', '火': 'クツム/ヌーベル', '水': 'カランダ/クザカ', '木': 'ガーモス', '金': 'ギュント/ムラカ', '土': 'ガーモス', '日': 'ガーモス'},
    '22:29': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': None, '金': 'ガーモス', '土': None, '日': 'ギュント/ムラカ'},
    '22:59': {'月': 'クツム/カランダ', '火': 'カランダ/ヌーベル', '水': 'オピン', '木': 'ベル', '金': 'クツム/カランダ', '土': None, '日': 'オピン'},
    '23:29': {'月': 'イザベラ', '火': '童心12号', '水': 'イザベラ', '木': '童心12号', '金': 'イザベラ' ,'土': None, '日': 'イザベラ'},
}

def add_one_minute(time_str):
    """
    plus one minute to string formatted time
    """

    time_format = '%H:%M'
    dt_obj = datetime.strptime(time_str, time_format)
    dt_obj += timedelta(minutes=1)
    return dt_obj.strftime(time_format)


def find_next_boss(current_time, current_day_jp):
    """
    find next boss name and the spawn time of it
    
    Parameters
    ----------
    current_time : str 
        datetime.now(JST).strftime('%H:%M') ex: '23:21'
    current_day_jp : str
        day name in Ja

    returns
    -------
    next_boss_name : str
        the name of a boss spawn next in Ja
    next_boss_time : str
        the spawn time of upcoming boss
    """

    sorted_schedule = sorted(boss_schedule.items())

    for i, (time, bosses) in enumerate(sorted_schedule):

        if time > current_time and bosses.get(current_day_jp):
            return bosses.get(current_day_jp), add_one_minute(time)
        
        elif time == current_time and bosses.get(current_day_jp):
            if current_time == '18:59' and current_day_jp == '土':
                return 'ガーモス', '01:30'
            elif sorted_schedule[(i + 1) % len(sorted_schedule)][1].get(current_day_jp) == None:
                return sorted_schedule[(i + 2) % len(sorted_schedule)][1].get(current_day_jp), add_one_minute(sorted_schedule[(i + 2) % len(sorted_schedule)][0])
            return sorted_schedule[(i + 1) % len(sorted_schedule)][1].get(current_day_jp), add_one_minute(sorted_schedule[(i + 1) % len(sorted_schedule)][0])
        
    return sorted_schedule[0][1].get(current_day_jp), add_one_minute([k for k, v in boss_schedule.items()][0])

@tasks.loop(seconds=30)
async def send_message_at_time():
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).strftime('%H:%M')
    current_day = datetime.now(JST).weekday()
    current_day_jp = jp_weekday[current_day]

    try:
        if current_time in boss_schedule:
            boss_name = boss_schedule[current_time].get(current_day_jp)
            next_boss, next_boss_time = find_next_boss(current_time, current_day_jp)
            if boss_name:
                channel = bot.get_channel(int(CHANNEL_ID))

                embed = discord.Embed(
                    title="ボス出現アラート",
                    description=f"⚡\nまもなく **{boss_name}** が出現します",
                    color=0x00bf5c,
                    url="https://garmoth.com/boss-timer",
                    timestamp=datetime.now(timezone.utc)
                )
                
                if next_boss:
                    embed.add_field(name="次のボス", value=next_boss)
                    embed.add_field(name="時間", value=next_boss_time)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1159883552494735513/1160028857810821150/pngaaa.com-3957460.png?ex=65332c0f&is=6520b70f&hm=ed2a27f6e6655200a4ce62dfa80699a4789e2d46e4e6691841c76e24ee33ab30&")

                await channel.send(embed=embed)                
                await asyncio.sleep(60)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    send_message_at_time.start()

bot.run(TOKEN)