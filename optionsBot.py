# Discord specific
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
# From project
import messageParser as mp
import generateChart as gc
import optionsUtil as ou
from pyson import pyson
# General
import os
from datetime import datetime
import json

# Loads the env file (contains the token)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ADMIN_ID = os.getenv('BOT_ADMIN')


def initialize():
	# Initializes with command prefix
	bot = commands.Bot(command_prefix='!')
	client = discord.Client()
	bot.remove_command('help') # Removes the default help command

	return bot, client



# Initialize the bot
bot, client = initialize()




# Changes the bot presence state
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name='!help'))





## Checks if the user sending the message is an approved member
def is_approved(ctx):
	return str(BOT_ADMIN_ID) == str(ctx.message.author.id)





# For putting someone in timeout
MOVE_BACK = False
MEMBER_TO_MOVE = []
TIMEOUT_CHANNEL = int(os.getenv("TIMEOUT_CHANNEL"))
UNSIMPABLE = [str(BOT_ADMIN_ID), "201503408652419073", "285480424904327179"]



@bot.command(name='simp')
async def simp(ctx, member:discord.Member=None):
	guild = ctx.message.guild
	global TIMEOUT_CHANNEL

	print(member.id)
	if str(member.id) in UNSIMPABLE:
		return

	channel = guild.get_channel(TIMEOUT_CHANNEL)

	if channel == None:
		await guild.create_voice_channel(name="Steven's Simp Spot")

		for c in guild.voice_channels:
		    if c.name == "Steven's Simp Spot":
		        channel = c
		        TIMEOUT_CHANNEL = c.id
		        os.environ['TIMEOUT_CHANNEL'] = str(TIMEOUT_CHANNEL)


	try:
		await member.move_to(channel)
		global MOVE_BACK
		global MEMBER_TO_MOVE 
		MOVE_BACK = True
		MEMBER_TO_MOVE.append(member)
	except:
		raise ValueExveption("Ssdfs")
		await ctx.send("that simp {} isn't in a voice channel".format(member))



## If they try leaving, move them back
@bot.event
async def on_voice_state_update(member, before, after):
	global TIMEOUT_CHANNEL

	if MOVE_BACK == True:
		if member in MEMBER_TO_MOVE:
			if after.channel != None:
				if after.channel.id != TIMEOUT_CHANNEL:
					guild = member.guild
					channel = guild.get_channel(TIMEOUT_CHANNEL)
					if channel == None:
						await guild.create_voice_channel(name="Steven's Simp Spot")

						for c in guild.voice_channels:
						    if c.name == "Steven's Simp Spot":
						        channel = c
						        TIMEOUT_CHANNEL = c.id
					await member.move_to(channel)
		else:
			if after.channel != None:
				if after.channel.id == TIMEOUT_CHANNEL:
					await member.move_to(before.channel)





## Ends the timeout
@bot.command(name='endtimeout')
async def endtimeout(ctx, member:discord.Member=None):
	global MOVE_BACK
	global MEMBER_TO_MOVE
	if str(member.id) not in MEMBER_TO_MOVE:
		MOVE_BACK = False
		MEMBER_TO_MOVE.remove(member)








# New help command
@bot.command(name='help')
async def help(ctx):
	embed = discord.Embed(title="OptionsBot Help", description="Commands and descriptions", color=0x0000ff)

	misc = ("`!ping` : Responds 'pong'\n\n`!steven` : Checks if Steven is a simp\n\n")
	
	options = ("`!op <TICKER> <DATE><TYPE> <STRIKE>`\n`(alias: !option)` : Returns information about a specific option. The string formatting is pretty loose "
	 "(aside from the spacing). Examples: `!op $spy 6/19c 300`, `!op AAPL 4/17p $400.50`, `!op T 1/18/22C 2010.50`\n\n"
	 "`!ops <TICKER> <DATE>**`\n`(alias: !optionchain, !opc)` : Returns information about an options chain. Calling `!ops <TICKER>` will return a list of availible dates, " 
	 "and calling `!ops <TICKER> <DATE>` will return more specific information\n\n")

	charting = ("`!c <TICKER> <DATE><TYPE> <STRIKE> <DURATION>` : Returns a chart of the price and volume of an option. "
		"The formatting is identical to `!op`, with the addition of a <DURATION> field. This takes a numberical value and date type "
		"(valid options are 'd', 'm', 'y'). **NOTE**: it is unlikely that data will be availible for the option "
		"more than a month back.\n\n`!chartstock <STOCK_TICKER> <DURATION>`\n`(alias: !cs)` : Returns a chart of the price "
		"and volume of a STOCK\n\n")

	trading = ("`!buy (<TICKER> OR <TICKER> <DATE><TYPE> <STRIKE>) <N>` : Buys *N* contracts/shares of the given option or stock\n\n"
		"`!portfolio` :  Returns the value of your portfolio (broken down into categories)\n\n"
		"`!leaderboard` : Returns everyone's standings on the leaderboard")

	embed.add_field(name="Misc", value=misc, inline=False)
	embed.add_field(name="Options", value=options, inline=False)
	embed.add_field(name="Charting", value=charting, inline=False)
	embed.add_field(name="Trading", value=trading, inline=False)
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
@bot.command(name='echo')
@commands.check(is_approved)
async def echo(ctx, *args):
	msg = ' '.join(args)
	await ctx.send(msg)
	await ctx.message.delete()





# Purges a given number of messages
@bot.command(name='purge')
async def purge(ctx, number):
	await ctx.message.channel.purge(limit=int(number)+1)





# Returns information about a specific option
# Takes a ticker, date, type, and strike
@bot.command(aliases=['option'])
async def op(ctx, *args):
	string = ' '.join(args)

	try:
		t, d, o, s, st = mp.parseContractInfo(string)
		optionInfo = ou.getOptionInfo(t, d, o, s, st)
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
@bot.command(aliases=["opc", "optionchain"])
async def ops(ctx, *args):
	string = ' '.join(args)

	try: # Tries parsing the stirng
		ticker, date = mp.parseChainInfo(string)
	except:
		await ctx.send("Please check the formatting and the ticker spelling")
		raise ValueError("Improperly formatted input")

	# Initializes the embed
	embed = discord.Embed(title=string.upper(), description=("When a date is specified, 5 options above/below "
		"the current price will be returned\nFormat: `Strike Price`\nCall Option\nPut Option"), color=0x0000ff)

	# If we're not given a date:
	if date == None:
		embed.add_field(name="Availible Dates", value = ou.getChainDates(ticker))
		embed.add_field(name="More Info", value="To search more specifically, use `!ops ticker date`", inline=False)
	# Else, we have a date : try to get the info
	else:
		try:
			embed = ou.printChain(ticker, int(date.timestamp()), embed)
		except:
			await ctx.send("No data found. Please check the formatting, ticker spelling, and date")
			raise ValueError("No data found for input")
	embed.set_footer(text="Data requested " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)'))
	await ctx.send(embed=embed)


# Charts an options contract
@bot.command(aliases=['chart'])
async def c(ctx, *args):
	string = ' '.join(args)

	try:
		await ctx.send("Compiling data....", delete_after=1.0)
		length, optionInfo = ou.getChartInfo(string)
		file = discord.File(gc.generateChart(string, optionInfo['contractSymbol'], length))
		await ctx.message.channel.send("Change in Price (and Volume)", file=file)
	except:
		await ctx.send("No data was found. This has two main causes:\n"
			"Check if the option exists using `!op`. It might just exist. Alternativly, it might be a formatting issue\n"
			"Otherwise, try adjusting the duration. Note: "
			"it is **very** unlikely for any contract to have data for more than a month back")






# Charts a stock
# Takes a ticker and a duration
@bot.command(aliases=['chartstock'])
async def cs(ctx, ticker, duration):

	# Tries to calculate the length of the chart
	try:
		length = mp.parseDurationInfo(duration.upper(), maxDur=(365*3))
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

		currency.data[ID]



#############
## ECONOMY ##
#############

currency=pyson('currency')
if 'name' not in currency.data:
	currency.data['name']='USD'




# Initializes a person's portfolio
def check_id(ID):
	ID = str(ID)
	if ID not in currency.data:
		currency.data[ID] = {}
		currency.data[ID]['currency'] = 0
		currency.data[ID]['symbols'] = []
		currency.data[ID]['stocks'] = []
		currency.save() 



# Admin use only:
# Adds a given number of dollars to a user's account
@commands.check(is_approved)
@bot.command(pass_context=True)
async def add(ctx,amount:int=0,member:discord.Member=None):
	ID = str(member.id)
	check_id(ID)
	currency.data[ID]['currency'] += amount
	currency.save()
	await ctx.send("The Fed just gave {1} another ${0} bailout".format(amount, member.mention))




# Admin use only:
# Remives a given number of points from a member's stash
@commands.check(is_approved)
@bot.command(pass_context=True)
async def remove(ctx,amount:int=0,member:discord.Member=None):
	''': Remove points/currency from a member's stash'''
	ID = str(member.id)
	check_id(ID)
	currency.data[ID]['currency'] = max(currency.data[ID]['currency'] - amount, 0)
	currency.save()
	await ctx.send("{0} just lost ${1} on OTM SPY puts".format(member.mention, amount))





# Checks your portfolio value
@bot.command(pass_context=True)
async def portfolio(ctx):
	ID = str(ctx.message.author.id)
	check_id(ID)

	optionValue, change, percentChange = mp.optionsPortfolioValue(currency.data[ID]['symbols'])
	stockValue, stockChange, stockPercentChange = ou.stocksPortfolioValue(currency.data[ID]['stocks'])

	totalValue = round(optionValue + stockValue + currency.data[ID]['currency'], 2)
	totalChange = round(change + stockChange, 2)
	totalPercentChange = round(percentChange + stockPercentChange, 2)

	await ctx.send(("your broke ass only has ${0} (Change: ${1} / {2}%)\n"
		"Investing power: ${3}\nOptions: ${4}\n"
		"Stocks: ${5}").format(totalValue, totalChange, totalPercentChange, currency.data[ID]['currency'], optionValue, stockValue))
	if str(ctx.message.author.id) == "160507791059058688":
		await ctx.send("Steven?: true\nSimp?: true\nHotel?: Trivago")





# Views the server leaderboard
@bot.command(aliases=['leaderboards'])
async def leaderboard(ctx):

	members = []
	for ID, assets in currency.data.items():
		if ID != 'name':
			optionValue, change, percentChange = mp.optionsPortfolioValue(assets['symbols'])
			totalValue = optionValue + assets['currency']
			members.append((ID, totalValue))

	if len(members) == 0:
		await bot.say('Leaderboard is empty')
		return

	ordered = sorted(members,key=lambda x:x[1] ,reverse=True )
	players = ''
	assets = ''

	for ID, playerAssets in ordered:
		player = '<@{}>'.format(ID)
        #await client.send_message(message.channel, ' : %s is the best ' % myid) #discord.utils.get(bot.get_all_members(), id=ID)
		players += player + '\n'
		assets += "${}".format(playerAssets) + '\n'

	embed = discord.Embed(title='Leaderboard')
	embed.add_field(name='Player', value=players)
	embed.add_field(name='Assets', value=assets)
	await ctx.send(embed=embed)



# Buys the given amount of the given stock/contract
@bot.command(pass_context=True)
async def buy(ctx, *args):
	contractArgs = args[:-1]
	ID = str(ctx.message.author.id)
	check_id(ID)
	currentLiquid = currency.data[ID]['currency']
	
	try:
		numberOfContracts = int(args[-1])

		if len(contractArgs) == 1: # this is a stock
			info = ou.getStockInfo(contractArgs[0])
			price = info['postMarketPrice']

			if currentLiquid > price:
				currency.data[ID]['stocks'].append([info['symbol'], numberOfContracts])
			else:
				await ctx.send("broke ass (you need ${0} to buy this)".format(price))
				return


		elif len(contractArgs) == 3: # this is an option
			t, d, o, s, st = mp.parseContractInfo(' '.join(contractArgs))
			price = ou.getOptionInfo(t, d, o, s, st)['lastPrice']

			if currentLiquid > price:
				currency.data[ID]['symbols'].append([st, numberOfContracts])
			else:
				await ctx.send("broke ass (you need ${0} to buy this)".format(price))
				return

		else:
			await ctx.send("Please check formatting (must follow the formatting for `!op` for options, or just the ticker for stocks")
			return
	except:
		await ctx.send("Please check formatting (must follow the formatting for `!op` for options, or just the ticker for stocks")
		raise ValueError("Please check formatting (must follow the formatting for `!op` for options, or just the ticker for stocks")
		return


	currency.data[ID]['currency'] -= price
	currency.save()
	await ctx.send("Purchase sucessful")


# Execute #
bot.run(TOKEN)
client.run(TOKEN)
