# Discord specific
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
# From project
from Formatting import messageParser as mp
import generateChart as gc
from Utils import optionsUtil as ou
# General
import os
from datetime import datetime
import json

# Loads the env file (contains the token)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ADMIN_ID = os.getenv('BOT_ADMIN')

# For putting someone in timeout
MOVE_BACK = False
MEMBER_TO_MOVE = []
TIMEOUT_CHANNEL = int(os.getenv("TIMEOUT_CHANNEL"))
CANNOT_BE_TIMEOUTED = [str(BOT_ADMIN_ID), "201503408652419073", "285480424904327179"]



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



# ping
@bot.command(name='wis')
async def wis(ctx):
	await ctx.send("WOMEN IN STEM", tts=True)
	await ctx.send(" https://womeninstem.org/")





# If someone's acting up, removes them from this voice channel and moves them everytime they join back
@bot.command(name='timeout')
async def timeout(ctx, member:discord.Member=None):
	guild = ctx.message.guild
	global TIMEOUT_CHANNEL, MOVE_BACK, MEMBER_TO_MOVE

	if str(member.id) not in CANNOT_BE_TIMEOUTED:
		channel = guild.get_channel(TIMEOUT_CHANNEL)
		# If the channel has been deleted
		# You will need to update .env with the new channel ID, or it'll keep making new ones
		# everytime the program is restarted
		if channel == None:
			TIMEOUT_CHANNEL = await newVoiceChannel(guild, "Steven's Simp Spot")
		else:
			try:
				await member.move_to(channel)
				MOVE_BACK = True
				MEMBER_TO_MOVE.append(member)
			except:
				await ctx.send("that user {} isn't in a voice channel".format(member))




# Creates a new voice channel
async def newVoiceChannel(guild, name):
	global TIMEOUT_CHANNEL

	await guild.create_voice_channel(name=name)
	for c in guild.voice_channels:
		if c.name == name:
			TIMEOUT_CHANNEL = c.id
			return c.id


## If they try leaving, move them back
@bot.event
async def on_voice_state_update(member, before, after):

	global TIMEOUT_CHANNEL

	if MOVE_BACK == True: # If there are members to moveback
		if member in MEMBER_TO_MOVE: # if the member who just moved is on the list
			if after.channel != None:
				if after.channel.id != TIMEOUT_CHANNEL:
					channel = member.guild.get_channel(TIMEOUT_CHANNEL)
					if channel == None:
						channel = await newVoiceChannel(member.guild, "Steven's Simp Spot")

					await member.move_to(channel)
		# Nobody else can join the timeout channel
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

	misc = ("`!ping` : Responds 'pong'")
	
	options = ("`!op <TICKER> <DATE><TYPE> <STRIKE>`\n`(alias: !option)` : Returns information about a specific option. "
		"The string formatting is pretty loose (aside from the spacing). Examples: `!op $spy 6/19c 300`, `!op AAPL 4/17p "
		"$400.50`, `!op T 1/18/22C 2010.50`\n\n`!ops <TICKER> <DATE>**`\n`(alias: !optionchain, !opc)` : Returns "
		"information about an options chain. Calling `!ops <TICKER>` will return a list of availible dates, and calling "
		"`!ops <TICKER> <DATE>` will return more specific information\n\n")

	charting = ("`!c <TICKER> <DATE><TYPE> <STRIKE> <DURATION>` : Returns a chart of the price and volume of an option. "
		"The formatting is identical to `!op`, with the addition of a <DURATION> field. This takes a numberical value "
		"and date type (valid options are 'd', 'm', 'y'). **NOTE**: it is unlikely that data will be availible for the "
		"option more than a month back.\n\n`!chartstock <STOCK_TICKER> <DURATION>`\n`(alias: !cs)` : Returns a chart of "
		"the price and volume of a STOCK\n\n")

	trading = ("`!buy (<TICKER> OR <TICKER> <DATE><TYPE> <STRIKE>) <N>` : Buys *N* contracts/shares of the given option "
		"or stock\n\n`!portfolio` :  Returns the value of your portfolio (broken down into categories)\n\n"
		"`!leaderboard` : Returns everyone's standings on the leaderboard")

	embed.add_field(name="Misc", value=misc, inline=False)
	embed.add_field(name="Options", value=options, inline=False)
	embed.add_field(name="Charting", value=charting, inline=False)
	embed.add_field(name="Trading", value=trading, inline=False)
	await ctx.send(embed=embed)




# ping
@bot.command(name='ping')
async def ping(ctx):
	await ctx.send("pong", delete_after=1)
	await ctx.message.delete()



# Echo (don't tell steven)
@bot.command(name='echo')
#@commands.check(is_approved)
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
	try:
		t, d, o, s, st = mp.parseContractInfo(' '.join(args))
		optionInfo = ou.getOptionInfo(st)
	except:
		await ctx.send("String could not be parsed. Please check your formatting (`!help`) for more info")
		raise ValueError("String could not be parsed")

	# Cleans up the title string
	cleanTitle = "$" + str(t) + " " + d.strftime('%m/%d') + o + " $" + s

	if 'quote' in optionInfo:
		opChange = optionInfo['quote']['regularMarketChange']
		cSymbol = optionInfo['quote']['symbol']
		lastPrice = optionInfo['quote']['regularMarketPreviousClose']
		perChange = optionInfo['quote']['regularMarketChangePercent']
		volume = optionInfo['quote']['regularMarketVolume']
		openInterest = optionInfo['quote']['openInterest']
		bid = optionInfo['quote']['bid']
		ask = optionInfo['quote']['ask']
	else:
		opChange = optionInfo['change']
		cSymbol = optionInfo['contractSymbol']
		lastPrice = optionInfo['lastPrice']
		perChange = optionInfo['percentChange']
		volume = optionInfo['volume']
		openInterest = optionInfo['openInterest']
		bid = optionInfo['bid']
		ask = optionInfo['ask']

	print(optionInfo)

	change = round(opChange, 2)

	if change < 0:
		change = "-$" + str(change * -1)
		color = 0xff0000
	else:
		change = "+$" + str(change)
		color = 0x00ff00

	embed = discord.Embed(title=cleanTitle, description=cSymbol, color=color)
	embed.add_field(name="Last Price", value="$" + str(round(lastPrice, 2)))
	embed.add_field(name="Change", value=change)
	embed.add_field(name="% Change", value=round(perChange, 2))
	embed.add_field(name="Volume", value=volume)
	embed.add_field(name="OI", value=round(openInterest, 2))
	embed.add_field(name="Bid / Ask", value="$" + str(round(bid, 2)) + " / $" + str(round(ask, 2)))
	embed.add_field(name="B/A Spread", value="$" + str(round(round(ask, 2) - round(bid, 2), 2)))

	embed.set_footer(text="Data requested at " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)') + 
		"\nData may not be accurate as of the time requested due to API delay")

	await ctx.send(embed=embed)




# Returns an option chain
# Takes a ticker and (optionally) a date
@bot.command(aliases=["opc", "optionchain"])
async def ops(ctx, *args):
	string = ' '.join(args)

	try: # Tries parsing the stirng
		ticker, date = mp.parseChainInfo(string)
	except:
		await ctx.send("String could not be parsed - please check the formatting and the ticker spelling")
		raise ValueError("Improperly formatted input")

	# Initializes the embed
	embed = discord.Embed(title=string.upper(), description=("When a date is specified, 5 options above/below "
		"the current price will be returned\nFormat: `Strike Price`\nCall Option\nPut Option"), color=0x0000ff)

	try:
		# If we're not given a date:
		if date == None:
			embed.add_field(name="Availible Dates", value = ou.getChainDates(ticker))
			embed.add_field(name="More Info", value="To search more specifically, use `!ops ticker date`", inline=False)
		# Else, we have a date : try to get the info
		else:
			values, strikes = ou.printChain(ticker, int(date.timestamp()))
			for i in range(0, len(values)-1):
				embed.add_field(name = strikes[i], value=values[i], inline=False)
	except:
		await ctx.send("No data found. Please check the formatting, ticker spelling, and date")
		raise ValueError("No data found for input")
	
	embed.set_footer(text="Data requested " + datetime.today().strftime('%H:%M:%S (%m/%m/%y)'))
	await ctx.send(embed=embed)


# Charts an options contract
@bot.command(aliases=['chart'])
async def c(ctx, *args):
	string = ' '.join(args)
	string = string.upper()

	try:
		await ctx.send("Compiling data....", delete_after=1.0)
		length, optionInfo = ou.getChartInfo(string)

		chart = gc.Chart(string, optionInfo['underlyingSymbol'], length)
		file = discord.File(chart.name)
		await ctx.message.channel.send("Change in Price (and Volume)", file=file)
	except:
		await ctx.send("No data was found. This has two main causes:\n"
			"Check if the option exists using `!op`. It might just exist. Alternativly, it might be a formatting issue\n"
			"Otherwise, try adjusting the duration. Note: "
			"it is **very** unlikely for any contract to have data for more than a month back")






# Charts a stock
# Takes a ticker and a duration
@bot.command(aliases=['chartstock'])
async def cs(ctx, *args):

	try:
		ticker, duration = args
	except:
		raise ValueError("Improperly formatted")

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
		await ctx.send("Invalid duration format (Format: XY, where X is a number and Y is one of "
			": d, m, y)\neg. 5d, 13d, 3m, 1y")
	
	# Tries generating the chart
	try:
		await ctx.send("Compiling data....", delete_after=1.0)
		chart = gc.Chart(ticker, ticker.upper(), length, interval=interval)
		file = discord.File(chart.name)
		# Sends the chart (if sucessful)
		await ctx.message.channel.send("Price and Volume Changes", file=file)
	except:
		await ctx.send("No data found. Is the ticker spelled correctly?\nThis may happen due to interval lengths - "
			"the specified interval may be too small (for example, if you call 1D over the weekend, the day would "
			"not have any trading data). More commonly, the interval might be too large")
		currency.data[ID]



#############
## ECONOMY ##
#############
class jFile:
	def __init__(self, fileName):
		# Check if valid file
		if os.path.isfile(fileName):
			try:
				with open(fileName) as f:
					data = json.load(f)
				
				self.fileName = fileName
				self.data = data
			except:
				raise ValueError("Could not load data from json file")
		else:
			os.mknod(filename)
			self.fileName = fileName
			self.data = {}
	# Saves the json file 
	def save(self):
		with open(self.fileName, "w") as f:
			json.dump(self.data, f, indent=4, sort_keys=True)



currency=jFile('currency.json')
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





# Checks a member's portfolio by ID
async def memberPortfolio(id):
	ID = str(id)
	check_id(ID)

	optionValue, change, percentChange = ou.optionsPortfolioValue(currency.data[ID]['symbols'])
	stockValue, stockChange, stockPercentChange = ou.stocksPortfolioValue(currency.data[ID]['stocks'])

	totalValue = round(optionValue + stockValue + currency.data[ID]['currency'], 2)
	totalChange = round(change + stockChange, 2)
	totalPercentChange = round(percentChange + stockPercentChange, 2)

	return totalValue, totalChange, totalPercentChange, optionValue, stockValue




# Checks your portfolio value
@bot.command(pass_context=True)
async def portfolio(ctx):
	ID = str(ctx.message.author.id)
	value, change, percentChange, optionValue, stockValue = await memberPortfolio(ID)

	await ctx.send(("your broke ass only has ${0} (Change: ${1} / {2}%)\n"
		"Investing power: ${3}\nOptions: ${4}\n"
		"Stocks: ${5}").format(value, change, percentChange, currency.data[ID]['currency'], optionValue, stockValue))
	
	if str(ctx.message.author.id) == "160507791059058688":
		await ctx.send("Steven?: true\nSimp?: true\nHotel?: Trivago")





# Views the server leaderboard
@bot.command(aliases=['leaderboards'])
async def leaderboard(ctx):

	members = []
	for ID, assets in currency.data.items():
		if ID != 'name':
			totalValue, *trash = await memberPortfolio(ID)
			members.append((ID, totalValue))

	if len(members) == 0:
		return await ctx.send('Leaderboard is empty')

	ordered = sorted(members, key=lambda x:x[1], reverse=True)
	players, assets = '', ''

	for ID, playerAssets in ordered:
		players += '<@{}>\n'.format(ID)
		assets += "${}".format(playerAssets) + '\n'

	embed = discord.Embed(title='Leaderboard')
	embed.add_field(name='Player', value=players)
	embed.add_field(name='Assets', value=assets)
	await ctx.send(embed=embed)




# validPurchase (float currentLiquid, float price)
# Checks if this is a valid purchase
async def validPurchase(currentLiquid, price):
	if currentLiquid > price:
		return True
	else:
		await ctx.send("broke ass (you need ${0} to buy this)".format(price))
		return

# buySymbol(data, list contractArgs, int numberOfContracts)
# buys the given symbol
async def buySymbol(data, *args):
	args = list(args)
	try:
		contractArgs, numberOfContracts = args[:-1][0], args[-1]
	except:
		raise ValueError("Input improperly formatted")

	currentLiquid = data['currency']

	if len(contractArgs) == 1: # this is a stock
		info = ou.getStockInfo(contractArgs[0])
		symbol, price = info['symbol'], info['regularMarketPrice']

		if validPurchase(currentLiquid, price):
			data['stocks'].append([symbol, numberOfContracts])

	elif len(contractArgs) == 3: # this is an option
		t, d, o, s, symbol = mp.parseContractInfo(' '.join(contractArgs))
		price = ou.getOptionInfo(symbol)['lastPrice']

		if validPurchase(currentLiquid, price):
			data['symbols'].append([symbol, numberOfContracts])

	else:
		return await ctx.send("Please check formatting (`!help`)")
		raise ValueError("Please check formatting (`!help`)")

	data['currency'] -= price
	return data


# Buys the given amount of the given stock/contract
@bot.command(pass_context=True)
async def buy(ctx, *args):
	contractArgs = list(args)[:-1]
	ID = str(ctx.message.author.id)
	check_id(ID)
	
	try:
		data = await buySymbol(currency.data[ID], contractArgs, int(args[-1]))
		currency.data[ID] = data
	except:
		await ctx.send("Please check formatting (`!help`)")
		raise ValueError("Please check formatting (`!help`)")
	
	currency.save()
	await ctx.send("Purchase sucessful")

# Execute #
bot.run(TOKEN)
client.run(TOKEN)
