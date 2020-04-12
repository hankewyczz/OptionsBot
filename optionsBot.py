# Discord specific
import discord
from discord.ext import commands
from dotenv import load_dotenv
# From project
import messageParser as mp
import generateChart as gc
# General
import os
from datetime import datetime
import json

# Loads the env file (contains the token)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


# Initializes with command prefix
bot = commands.Bot(command_prefix='!')
bot.remove_command('help') # Removes the default help command

# Changes the bot presence state
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name='!help'))

# New help command
@bot.command(name='help')
async def help(ctx):
	embed = discord.Embed(title="OptionsBot Help", description="Commands and descriptions", color=0x0000ff)

	misc = ("`!ping` : Responds 'pong'\n\n`!steven` : Checks if Steven is a simp")
	
	options = ("`!op <TICKER> <DATE><TYPE> <STRIKE>`\n`(alias: !option)` : Returns information about a specific option. The string formatting is pretty loose "
	 "(aside from the spacing). Examples: `!op $spy 6/19c 300`, `!op AAPL 4/17p $400.50`, `!op T 1/18/22C 2010.50`\n\n"
	 "`!ops <TICKER> <DATE>**`\n`(alias: !optionchain, !opc)` : Returns information about an options chain. Calling `!ops <TICKER>` will return a list of availible dates, " 
	 "and calling `!ops <TICKER> <DATE>` will return more specific information\n\n")

	charting = ("`!c <TICKER> <DATE><TYPE> <STRIKE> <DURATION>` : Returns a chart of the price and volume of an option. "
		"The formatting is identical to `!op`, with the addition of a <DURATION> field. This takes a numberical value and date type "
		"(valid options are 'd', 'm', 'y'). **NOTE**: it is unlikely that data will be availible for the option "
		"more than a month back.\n\n`!chartstock <STOCK_TICKER> <DURATION>`\n`(alias: !cs)` : Returns a chart of the price "
		"and volume of a STOCK")

	embed.add_field(name="Misc", value=misc, inline=False)
	embed.add_field(name="Options", value=options, inline=False)
	embed.add_field(name="Charting", value=charting, inline=False)
	await ctx.send(embed=embed)


# Steven
@bot.command(name='steven')
async def steven(ctx):
    await ctx.send("is a simp")



# ping
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send("pong", delete_after=1)
    await ctx.message.delete()



# Echo (don't tell steven)
@bot.command(name='ekho')
async def ekho(ctx, *args):
	msg = ' '.join(args)
	await ctx.send(msg)
	await ctx.message.delete()





# Purges a given number of messages
@bot.command(name='purge')
async def purge(ctx, number):
    await ctx.message.channel.purge(limit=int(number)+1)





# Returns information about a specific option
# Takes a ticker, date, type, and strike
@bot.command(name='option')
async def option(ctx, *args):
    return await op(ctx, *args)

# alias command
@bot.command(name='op')
async def op(ctx, *args):
	string = ' '.join(args)

	try:
		t, d, o, s, st = mp.parseContractInfo(string)
		optionInfo = mp.getOptionInfo(t, d, o, s, st)
	except:
		await ctx.send("String could not be parsed. Please check your formatting (`!help`) for more info")
		return

	# Cleans up the title string
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
	embed.add_field(name="% Change", value=round(optionInfo['percentChange'], 2))
	embed.add_field(name="IV", value=round(optionInfo['impliedVolatility'], 2))
	embed.add_field(name="Volume", value=optionInfo['volume'])
	embed.add_field(name="OI", value=round(optionInfo['openInterest'], 2))
	embed.add_field(name="Bid / Ask", value="$" + str(round(optionInfo['bid'], 2)) + " / $" + str(round(optionInfo['ask'], 2)))
	embed.add_field(name="B/A Spread", value="$" + str(round(round(optionInfo['ask'], 2) - round(optionInfo['bid'], 2), 2)))

	embed.set_footer(text="Data requested at " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)') + "\nData may not be accurate as of the time requested due to API delay")

	await ctx.send(embed=embed)


	


# Returns an option chain
# Takes a ticker and (optionally) a date
@bot.command(name='optionchain')
async def optionchain(ctx, *args):
    return await ops(ctx, *args)

# Alias command
@bot.command(name='opc')
async def opc(ctx, *args):
    return await ops(ctx, *args)

# Alias command
@bot.command(name='ops')
async def ops(ctx, *args):
	string = ' '.join(args)

	# Tries to parse the string
	try:
		ticker, date = mp.parseChainInfo(string)
	except:
		await ctx.send("No data found. Please check the formatting and the ticker spelling")
		return

	# Initializes the embed
	embed = discord.Embed(title=string.upper(), description=("When a date is specified, 5 options above/below "
		"the current price will be returned\nFormat: `Strike Price`\nCall Option\nPut Option"), color=0x0000ff)

	# Makes the URL	
	url = mp.baseURL + ticker

	# If we're not given a date:
	if date == None:
		data = mp.loadFrom(url)['optionChain']['result'][0]['expirationDates']

		result = ""
		for datum in data:
			date = datetime.utcfromtimestamp(datum)
			if date.year == 2020:
				date = date.strftime('%b %d')
			else:
				date = date.strftime('%m/%d/%y')
			result += str(date) + ", "

		embed.add_field(name="Availible Dates", value=result)
		embed.add_field(name="More Info", value="To search more specifically, use `!ops ticker date`", inline=False)
	else:
		# We have a date : try to get the info
		try:
			calls, puts = mp.parseChainInfoAtDate(ticker, int(date.timestamp()))
		except:
			await ctx.send("No data found. Please check the formatting, ticker spelling, and date")
			return

		for i in range(0, len(calls)-1):

			# Formats the information displayed for each option
			strike = "Strike: {}".format(calls[i]['strike'])

			value = ""
			for type in [calls, puts]:
				price = "**__Price__**: ${0}".format(round(type[i]['lastPrice'], 2))
				change = "{0}%".format(round(type[i]['percentChange'], 2))
				vol = "**__Vol / OI__**: {0} / {1}".format(type[i]['volume'], type[i]['openInterest'])

				string = "{0} ({1}),  {2}\n".format(price, change, vol)
				value += string

			embed.add_field(name=strike, value=value, inline=False)

	embed.set_footer(text="Data requested " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)'))
	await ctx.send(embed=embed)





# Charts an options contract
@bot.command(name='chart')
async def chart(ctx, *args):
    return await c(ctx, *args)

# Alias command
@bot.command(name='c')
async def c(ctx, *args):
	string = ' '.join(args)

	try:
		await ctx.send("Compiling data....", delete_after=1.0)
		length, optionInfo = mp.getChartInfo(string)
		file = discord.File(gc.generateChart(string, optionInfo['contractSymbol'], length))
		await ctx.message.channel.send("Change in Price (and Volume)", file=file)
	except:
		await ctx.send("No data was found. This has two main causes:\n"
			"Check if the option exists using `!op`. It might just exist. Alternativly, it might be a formatting issue\n"
			"Otherwise, try adjusting the duration. Note: "
			"it is **very** unlikely for any contract to have data for more than a month back")






# Charts a stock
# Takes a ticker and a duration
@bot.command(name='chartstock')
async def chartstock(ctx, ticker, duration):
    return await cs(ctx, ticker, duration)
# Alias command
@bot.command(name='cs')
async def cs(ctx, ticker, duration):

	# Tries to calculate the length of the chart
	try:
		length = mp.getDurationInfo(duration.upper(), maxDur=(365*3))
		if length < 10:
			interval = "5m"
		elif length < 30:
			interval = "15m"
		elif length < 100:
			interval = "60m"
		else:
			interval = "1d"
	except:
		await ctx.send("Invalid duration format (Format: XY, where X is a number and Y is one of : d, m, y)\neg. 5d, 13d, 3m, 1y")
	
	# Tries generating the chart
	try:
		await ctx.send("Compiling data....", delete_after=1.0)
		chart = gc.generateChart(ticker, ticker.upper(), length, interval=interval)
		file = discord.File(chart)
		# Sends the chart (if sucessful)
		await ctx.message.channel.send("Price and Volume Changes", file=file)
	except:
		await ctx.send("No data found. Is the ticker spelled correctly?\nThis may happen due to interval lengths - "
			"the specified interval may be too small (for example, if you call 1D over the weekend, the day would not have"
			"any trading data). More commonly, the interval might be too large")

# Execute #
bot.run(TOKEN)