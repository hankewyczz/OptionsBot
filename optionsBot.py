import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import messageParser as mp
import generateChart as gc
from datetime import datetime
import urllib.request
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='steven', help='he is a simp no doubt about it')
async def steven(ctx):
    await ctx.send("is a simp")

@bot.command(name='ekho')
async def ekho(ctx, *args):
	msg = ' '.join(args)
	await ctx.send(msg)
	await ctx.message.delete()

@bot.command(name='purge')
async def purge(ctx, number):
    await ctx.message.channel.purge(limit=int(number)+1)

@bot.command(name='op')
async def op(ctx, *args):
	string = ' '.join(args)
	optionInfo = mp.getOptionInfo(string)

	t, d, o, s, st = mp.stringParse(string)
	cleanOp = "$" + str(t) + " " + d.strftime('%m/%d') + o + " $" + s

	change = round(optionInfo['change'], 2)
	if change < 0:
		change *= -1
		change = "-$" + str(change)
		color = 0xff0000
	else:
		change = "+$" + str(change)
		color = 0x00ff00

	embed = discord.Embed(title=cleanOp, description=optionInfo['contractSymbol'], color=color)
	embed.add_field(name="Last Price", value="$" + str(round(optionInfo['lastPrice'], 2)))
	embed.add_field(name="Change", value=change)
	pChange = round(optionInfo['percentChange'], 2)
	if pChange < 0:
		pChange = str(pChange) + "%"
	else:
		pChange = "+" + str(pChange) + "%"
	embed.add_field(name="% Change", value=pChange)
	embed.add_field(name="IV", value=round(optionInfo['impliedVolatility'], 2))
	embed.add_field(name="Volume", value=optionInfo['volume'])
	embed.add_field(name="OI", value=round(optionInfo['openInterest'], 2))
	embed.add_field(name="Bid / Ask", value="$" + str(round(optionInfo['bid'], 2)) + " / $" + str(round(optionInfo['ask'], 2)))
	embed.add_field(name="B/A Spread", value="$" + str(round(round(optionInfo['ask'], 2) - round(optionInfo['bid'], 2), 2)))
	embed.set_footer(text="Data requested at " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)') + "\nData may not be accurate as of the time requested due to API delay")


	await ctx.send(embed=embed)
	


@bot.command(name='ops')
async def ops(ctx, *args):
	string = ' '.join(args)
	ticker, date, optionType = mp.getAllOptions(string)

	embed = discord.Embed(title=string.upper(), color=0x0000ff,)

	url = mp.baseURL + ticker
	if date == None:
		with urllib.request.urlopen(url) as thisUrl:
			data = json.loads(thisUrl.read().decode())
			data = data['optionChain']['result'][0]['expirationDates']

		result = ""
		for datum in data:
			date = datetime.utcfromtimestamp(datum)
			if date.year == 2020:
				date = date.strftime('%m/%d')
			else:
				date = date.strftime('%m/%d/%y')
			result += str(date) + ", "

		embed.add_field(name="Availible Dates", value=result)
		embed.add_field(name="More Info", value="To search more specifically, use `!ops ticker date`", inline=False)

	elif optionType == None:
		results = mp.getAllOptionsAtDate(ticker, int(date.timestamp()))
		for i in range(0, 20):
			result = results[i]
			date = datetime.utcfromtimestamp(result['expiration'])
			if date.year == 2020:
				date = date.strftime('%m/%d')
			else:
				date = date.strftime('%m/%d/%y')

			optionType = str(result['contractSymbol'][-9:-8])

			if "bid" in result:
				bid = result['bid']
			else:
				bid = 0.0

			ba = str(bid) + " / " + str(result['ask'])

			name = date + " " + {"C": "CALL", "P": "PUT"}[optionType] + " $" + str(result['strike'])


			result = "**Last price:** " + str(result['lastPrice']) + ", **Change:** " + str(result['change']) + "/" + str(result['percentChange']) + "%"
			embed.add_field(name=name, value=result)
	else:
		return getAllOptionsAtDate(ticker, int(date.timestamp()), option=optionType)


	
	'''
	for option in optionsInfo:
		t, d, o, s = mp.contractStringToInfo(option['contractSymbol'])
		cleanOp = "$" + str(t) + " " + d.strftime('%m/%d') + o + " $" + s
		info = "Last Price: $" + str(option['lastPrice']), "Change: " + str(option['change'])

		embed.add_field(name=cleanOp, value=info)
	'''

	embed.set_footer(text="Data requested " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)'))
	await ctx.send(embed=embed)

@bot.command(name='c')
async def c(ctx, *args):
	string = ' '.join(args)
	length, optionInfo = mp.getChartInfo(string)
	file = discord.File(gc.generateChart(string, optionInfo['contractSymbol'], length))
	await ctx.message.channel.send("Change in Price (and Volume)", file=file)


bot.run(TOKEN)
print("Connected")