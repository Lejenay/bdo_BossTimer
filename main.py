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

boss_schedule = {
    '01:29': {'月': 'クザカ/ヌーベル', '火': 'クザカ/ヌーベル', '水': 'クザカ/ヌーベル', '木': 'カランダ/クザカ', '金': 'カランダ/クザカ', '土': 'ガーモス', '日': 'ガーモス'},
    '10:59': {'月': 'クザカ/カランダ', '火': 'クザカ/ヌーベル', '水': None, '木': 'クザカ/クツム', '金': 'クザカ/ヌーベル', '土': 'クザカ/ヌーベル', '日': 'クツム/カランダ'},
    '13:59': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': 'ガーモス', '金': 'ガーモス', '土': 'オピン', '日': None},
    '15:59': {'月': 'クツム/クザカ', '火': 'クツム/クザカ', '水': 'クツム/ヌーベル', '木': 'クツム/ヌーベル', '金': 'クツム/ヌーベル', '土': 'クツム/カランダ', '日': 'クツム/カランダ'},
    '18:59': {'月': 'カランダ/ヌーベル', '火': 'クツム/ヌーベル', '水': 'カランダ/クザカ', '木': 'ガーモス', '金': 'ギュント/ムラカ', '土': 'ガーモス', '日': 'ガーモス'},
    '22:29': {'月': 'ガーモス', '火': 'ガーモス', '水': 'ガーモス', '木': None, '金': 'ガーモス', '土': None, '日': 'ギュント/ムラカ'},
    '22:59': {'月': 'クツム/カランダ', '火': 'カランダ/ヌーベル', '水': 'オピン', '木': 'ベル', '金': 'クツム/カランダ', '土': None, '日': 'オピン'},
    '10:41': {'土': 'テストボス'}
}

def find_next_boss(current_time, current_day_jp):
    sorted_schedule = sorted(boss_schedule.items())
    for i, (time, bosses) in enumerate(sorted_schedule):
        if time > current_time and bosses.get(current_day_jp):
            return bosses.get(current_day_jp)
        elif time == current_time and bosses.get(current_day_jp):
            return sorted_schedule[(i + 1) % len(sorted_schedule)][1].get(current_day_jp)
    return sorted_schedule[0][1].get(current_day_jp)

@tasks.loop(seconds=30)
async def send_message_at_time():
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).strftime('%H:%M')
    current_day = datetime.now(JST).weekday()
    current_day_jp = jp_weekday[current_day]

    try:
        if current_time in boss_schedule:
            boss_name = boss_schedule[current_time].get(current_day_jp)
            next_boss = find_next_boss(current_time, current_day_jp)
            if boss_name:
                channel = bot.get_channel(int(CHANNEL_ID))

                embed = discord.Embed(
                    title="ボス出現アラート",
                    description=f"まもなく **{boss_name}** が出現します",
                    color=0x75ffd3,
                    url="https://garmoth.com/boss-timer",
                    timestamp=datetime.now(timezone.utc)
                )
                
                if next_boss:
                    embed.add_field(name="次のボス", value=next_boss)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1159883552494735513/1160028857810821150/pngaaa.com-3957460.png?ex=65332c0f&is=6520b70f&hm=ed2a27f6e6655200a4ce62dfa80699a4789e2d46e4e6691841c76e24ee33ab30&")
                embed.set_footer(text="Powered by Lejenay",
                     icon_url="https://cdn.discordapp.com/attachments/284247077771411456/1160019204129431662/ico_lejenay_45_512x.png?ex=65332312&is=6520ae12&hm=8e0a74a9ffc6d87660acced35640a43de66584b07340fac1a6db90c7923e41fd&")

                await channel.send("@here", embed=embed)                
                await asyncio.sleep(60)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    send_message_at_time.start()

bot.run(TOKEN)