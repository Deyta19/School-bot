import discord
from discord.ext import commands
import asyncio
import database
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# SISTEM CEK ROLE GURU

def is_guru():
    async def predicate(ctx):
        return discord.utils.get(ctx.author.roles, name="Guru") is not None
    return commands.check(predicate)

# VIEW UNTUK SISWA MELIHAT JADWAL

class HariView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Senin", style=discord.ButtonStyle.secondary)
    async def senin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kirim_jadwal(interaction, "Senin")

    @discord.ui.button(label="Selasa", style=discord.ButtonStyle.secondary)
    async def selasa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kirim_jadwal(interaction, "Selasa")

    @discord.ui.button(label="Rabu", style=discord.ButtonStyle.secondary)
    async def rabu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kirim_jadwal(interaction, "Rabu")

    @discord.ui.button(label="Kamis", style=discord.ButtonStyle.secondary)
    async def kamis(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kirim_jadwal(interaction, "Kamis")

    @discord.ui.button(label="Jumat", style=discord.ButtonStyle.secondary)
    async def jumat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kirim_jadwal(interaction, "Jumat")


async def kirim_jadwal(interaction, hari):
    data = database.ambil_jadwal(hari)

    if data:
        teks = f"📚 Jadwal hari {hari}:\n"
        for row in data:
            teks += f"- {row[0]}\n"
    else:
        teks = f"Tidak ada jadwal untuk hari {hari}."

    await interaction.response.send_message(teks)

@bot.command()
async def jadwal(ctx):
    await ctx.send(
        "📚 Pilih hari untuk melihat jadwal:",
        view=HariView()
    )

@bot.command()
async def list_ulangan(ctx):
    data = database.ambil_ulangan()

    if not data:
        await ctx.send("Tidak ada ulangan yang terdaftar.")
        return

    teks = "📚 Daftar Ulangan:\n"

    for row in data:
        teks += f"ID {row[0]} | {row[1]} | {row[2]} | {row[3]}\n"

    await ctx.send(teks)

@bot.command()
async def bantuan(ctx):
    await ctx.send(
        """
Berikut adalah perintah-perintah yang bisa digunakan semua orang:
    **!jadwal** => untuk melihat jadwal yang sudah ada
    **!list_ulangan** => untuk melihat ulangan-ulangan yang dijadwalkan
        
Lalu untuk perintah-perintah khusus Guru:
    **!tambah <hari> <mata_pelajaran>** => untuk menambahkan pelajaran ke jadwal, contohnya: !tambah Senin Matematika
    **!hapus <hari> <mata_pelajaran>** => untuk menghapus pelajaran dari jadwal, contohnya: !hapus Senin Matematika
    **!tambah_ulangan <tanggal> <mapel> <deskripsi>** => untuk menjadwalkan ulangan, contohnya: !tambah_ulangan 2026-03-20 Matematika Bab Trigonometri (format tanggalnya adalah Tahun-bulan-hari)
    **!hapus_ulangan <id>** => untuk menghapus ulangan sesuai urutannya di tabell, contohnya: !hapus_ulangan 1
    untuk pengingat ulangan, akan berjalan otomatis
        """
    )

# COMMAND UNTUK GURU

@bot.command()
@is_guru()
async def tambah(ctx, hari: str, *, mapel: str):
    database.tambah_jadwal(hari, mapel)
    await ctx.send(f"✅ Jadwal {mapel} berhasil ditambahkan ke hari {hari}.")

@bot.command()
@is_guru()
async def hapus(ctx, hari: str, *, mapel: str):
    database.hapus_jadwal(hari, mapel)
    await ctx.send(f"❌ Jadwal {mapel} berhasil dihapus dari hari {hari}.")

@bot.command()
@is_guru()
async def tambah_ulangan(ctx, tanggal: str, mapel: str, *, deskripsi: str):
    database.tambah_ulangan(tanggal, mapel, deskripsi)

    await ctx.send(
        f"📢 Ulangan berhasil ditambahkan\n"
        f"Tanggal: {tanggal}\n"
        f"Mapel: {mapel}\n"
        f"Materi: {deskripsi}"
    )

@bot.command()
@is_guru()
async def hapus_ulangan(ctx, id_ulangan: int):
    database.hapus_ulangan(id_ulangan)
    await ctx.send("Ulangan berhasil dihapus.")

# EVENT SAAT BOT ONLINE

@bot.event
async def on_ready():
    print(f"Bot aktif sebagai {bot.user}")

    # Kirim tombol ke channel pertama yang bisa dikirim pesan
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Halo! Klik tombol di bawah untuk melihat jadwal sekolah.",
                    view=HariView()
                )
                break
        break

# REMINDER LOOP 

async def reminder_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(3600)

async def reminder_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        data = database.ambil_ulangan()
        sekarang = datetime.date.today()

        for row in data:
            tanggal_ulangan = datetime.datetime.strptime(row[1], "%Y-%m-%d").date()

            selisih = (tanggal_ulangan - sekarang).days

            if selisih == 1:
                for guild in bot.guilds:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            await channel.send(
                                f"📢 Pengingat!\n"
                                f"Besok ada ulangan {row[2]}.\n"
                                f"Materi: {row[3]}"
                            )
                            break

        await asyncio.sleep(3600)

@bot.event
async def on_ready():
    print(f"Bot aktif sebagai {bot.user}")

    bot.loop.create_task(reminder_loop())

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Halo! Klik tombol di bawah untuk melihat jadwal sekolah.",
                    view=HariView()
                )
                break
        break

bot.run("TOKEN")