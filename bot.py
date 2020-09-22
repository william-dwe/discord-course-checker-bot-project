import discord
from discord.ext import commands
import pandas as pd
from datetime import datetime
import time
import os
import pytz

df = pd.read_csv("schedule_sem_5.csv", sep= ";")
bot = commands.Bot(command_prefix=">")

#check bot status
@bot.event
async def on_ready():
	print("Bot is ready")

#in case of error
@bot.event
async def on_command_error(ctx, error):
	if isinstance (error, commands.MissingPermissions):
		await ctx.send("You don't have the permission")
		await ctx.message.delete()
	elif isinstance (error, commands.MissingRequiredArgument):
		await ctx.send("Please enter the required argument")
		await ctx.message.delete()
	else:
		await ctx.send("There's an error")	

#command-list
@bot.command(aliases = ['hi', 'helo', 'halo'])
async def hello(ctx):
	await ctx.send("halo uga")

@bot.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=2):
	await ctx.channel.purge(limit = amount)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx,member : discord.Member,*,reason = "No reason provided"):
	await member.send("You have been kicked from Drunken Inn, Because: "+reason)
	await member.kick(reason=reason)

@bot.command()
@commands.has_permissions(kick_members=True)
async def whois(ctx, member: discord.Member):
	embed = discord.Embed(title = ("Who is " + member.name + " ?"), description = member.mention, color = discord.Colour.blue())
	embed.add_field(name = "ID", value = member.id, inline = True)
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = "Requested by " + ctx.author.name)
	await ctx.send(embed=embed)

#check jadwal kelas
@bot.command()
async def kelas(ctx,*, jurusan):

	#Time Declaration
	t = datetime.now(pytz.timezone("Asia/Jakarta"))
	jam_now = t.strftime("%H:%M:%S")
	hari_now = t.isoweekday()
	#Kondisi Saat ini
	TodaySchedule = df.loc[(df["jurusan"] == jurusan) & (df["hari"] == hari_now)]
	kelas = TodaySchedule.loc[(TodaySchedule["start"] < jam_now) & (TodaySchedule["finish"] > jam_now), "kelas"]
	jam_kelas = TodaySchedule.loc[(TodaySchedule["start"] < jam_now) & (TodaySchedule["finish"] > jam_now), "finish"]
	if (kelas.empty):
		condition = "<Currently Kelas Kosong>"
	else:
		condition = "<" + str(kelas.values[0]) + " until " + str(jam_kelas.values[0]) + ">"

	#Kondisi Kedepan
	next_nama_kelas = TodaySchedule.loc[(TodaySchedule["start"] > jam_now, "kelas")]
	if next_nama_kelas.empty:
		bool_kelas = False
	else: #next_kelas masih ada
		bool_kelas = True


	#Embed Output curent class
	em = discord.Embed(title = "<< Class Checker 101 >>", description= ("Last updated: "+ jam_now), color = discord.Colour.green())
	if jurusan in ("ti", "Ti", "TI", "teknik industri", "Teknik Industri", "Teknik industri"):
		em.add_field(name = "Teknik Industri (TI)", value = condition, inline = False)
		em.set_thumbnail(url = "https://mti.fti.itb.ac.id/wp-content/uploads/2019/02/mti_logo.png")
	elif jurusan in ("tk", "Tk", "TK", "tekim", "Tekim", "teknik kimia", "Teknik Kimia", "Teknik kimia"):
		em.add_field(name = "Teknik Kimia (TK)", value = condition, inline = False)
		em.set_thumbnail(url = "https://miro.medium.com/fit/c/336/336/2*9-Qy26rzW04fNe9nGXEJzw.jpeg")

	#embed output next class
	if bool_kelas == True:
		for i in range(len(next_nama_kelas)):
			next_condition = next_nama_kelas.values[i]
			next_start_kelas = TodaySchedule.loc[(TodaySchedule["start"] > jam_now, "start")].values[i]
			next_finish_kelas = TodaySchedule.loc[(TodaySchedule["start"] > jam_now, "finish")].values[i]
			em.add_field(name = (next_condition), value = ("" + (next_start_kelas)+ " - " + next_finish_kelas), inline=False)

	#footer & send
	em.set_footer(icon_url = ctx.author.avatar_url, text = "Requested by " + ctx.author.name)
	await ctx.send(embed=em)

bot.run(os.environ['DISCORD_TOKEN'])
