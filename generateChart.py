from datetime import datetime, timedelta
import urllib.request
import json
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as mtick
import numpy as np
import messageParser as mp
import optionsUtil as ou


'''
##############
## OVERVIEW ##
##############

getData(String symbol, int length, int interval)
	Takes the ticker/contract symbol and the duration of the chart

extrapolateData(list[X] data, X prev, boolean append)
	Fills any blank spots in the data by extrapolating 

drawGraph(list[int] x, list[float] y, list[int] vol, String title, int length)
	Takes lists of x, y, and volume data, and draws a graph

generateChart(String string, String symbol, int length)
	Takes the given string, the contract symbol, and the length of data to be viewed)

'''

class Chart:
	# The base URL for fetching the chart data. (Replace here if/when yahoo gets tired of people mooching off their API
	baseURL = "https://query1.finance.yahoo.com/v8/finance/chart/"

	# (String symbol, int length, int interval)
	# Takes the ticker/contract symbol and the duration of the chart
	def getData(self, symbol, length, interval):
		# Gets the start and end dates of the chart based on the arg length
		endDate = datetime.now()
		startDate = endDate - timedelta(days=length)

		# Calculates the unix timestamps for the start/end dates
		period1, period2 = [int(x.timestamp()) for x in [startDate, endDate]]
		
		# All the URL arguments
		# "interval" MUST be 2m. No clue why, but Yahoo throws a hissy fit if we try using other intervals, 
		# even though it lists [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo] as valid intervals
		urlArgs = {"period1": str(period1), "period2": str(period2), "interval": interval, "includePrePost": "true"}

		urlArgsString = ""
		for key in urlArgs.keys():
			urlArgsString = "{0}{1}={2}&".format(urlArgsString, key, urlArgs[key])

		# Oh yeah, it's all coming together (put the URL together and fetch data)
		data = ou.loadFrom("{0}{1}?{2}".format(self.baseURL, symbol, urlArgsString))

		try: # Using time as the bellwether here - everything else, we can extrapolate
			time = data['chart']['result'][0]['timestamp']
		except:
			raise ValueError("Not enough data for a graph")

		price = data['chart']['result'][0]['indicators']['quote'][0]['close']
		volume = data['chart']['result'][0]['indicators']['quote'][0]['volume']
		try:
			prevClose = data['chart']['result'][0]['meta']['previousClose']
		except: 
			prevClose = data['chart']['result'][0]['meta']['chartPreviousClose']
		
		# Extrapolates data to fit every point (Yahoo has some [many] blind spots for some [most] contracts)
		price = self.extrapolateData(price, prevClose)
		volume = [0 if x == None else x for x in volume]


		# returns a list[int], list[float], list[int]
		return time, price, volume


	# (list[X] data, X prev)
	# Fills any blank spots in the data by extrapolating 
	def extrapolateData(self, data, prev):
		new = []
		for d in data:
			if d == None:
				new.append(prev)
			else:
				new.append(d)
				prev = d
		return new



	# tickFormatter(int length)
	# Given the chart duration, determine x-Axis formatting
	def tickFormatter(self, length, ax2):
		# Sets the tick formatting for the x-axis
		formatting = {1: ["%H:%M", 1, "%H:%M", 8], 2: ["%m/%d", 24, "%H:%M", 4], 5: ["%m/%d", 24, "%H:%M", 12], 10: ["%m/%d", 24, "%H:%M", 48]}

		# handles the smalle cases
		if length <= 10:
			if length > 5 and length < 10:
				length = 5
			elif length > 2 and length < 5:
				length = 2
			majF, majL, minF, minL = formatting[length][0], formatting[length][1], formatting[length][2], formatting[length][3]

		# long-term cases
		elif length > 10:
			majF, majL, minF, minL = formatting[10][0], 24 * int(length/10), formatting[10][2], 48 * int(length/10)

		# Sets the x-axis date formats
		ax2.xaxis.set_major_formatter(md.DateFormatter(majF))
		ax2.xaxis.set_major_locator(md.HourLocator(interval=majL))
		ax2.xaxis.set_minor_formatter(md.DateFormatter(minF))
		ax2.xaxis.set_minor_locator(md.HourLocator(interval=minL))
		return ax2





	# generateAxes(x, y, dates)
	# generates the axes and figure from the x, y, and dates
	def generateAxes(self, x, y):
		# Calculates the min and max of the y-axis (for price)
		# We don't want the max to be 0, so we take the max of (2 and the real max)
		yMax = int(max(2, np.max(y)))
		yMin = int(np.min(y))
		yRange = int((yMax - yMin) / 2)

		dates = [datetime.fromtimestamp(date) for date in x]

		# Init
		fig, ax1 = plt.subplots()

		# Sets the max and min for the x-axis
		ax1.set_xlim(xmin = np.min(dates), xmax = np.max(dates))
		# Sets min/max for pricing. Min can never go below 0.
		ax1.set_ylim(ymin = max(0, yMin - yRange), ymax = yMax + yRange)

		# Sets the tick formatting for the prices y-axis
		ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

		return fig, ax1




	# (list[int] x, list[float] y, list[int] vol, String title, int length)
	# Takes lists of x, y and draws a graph
	def drawGraph(self, x, y):
		# Converts the timestamps in x into date objects
		dates = [datetime.fromtimestamp(date) for date in x]

		# Initializes
		fig, ax1 = self.generateAxes(x, y)

		# Plots the prices
		ax1.plot(dates, y, "#00A95D")
		l1 = ax1.fill_between(dates, y, facecolor="#00A95D")

		return fig, ax1, l1

	# (String string, String symbol, int length)
	# Takes the given string, the contract symbol, and the length of data to be viewed
	def __init__(self, string, symbol, length, interval="2m"):
		time, price, volume = self.getData(symbol, length, interval)
		cleanTitle = string.upper()
		cleanTitle = cleanTitle.replace("$", "\$")

		fig, ax1, l1 = self.drawGraph(time, price)

		# Initializes axes2 with identical xAxis
		ax2 = self.tickFormatter(length, ax1.twinx())
		ax2.set_ylim(ymin = 0, ymax = max(volume) * 2) # So volume occupies the bottom half of the graph
		
		# Plots the volume
		dates = [datetime.fromtimestamp(date) for date in time]
		ax2.plot(dates, volume, "#B2DCCB")
		l2 = ax2.fill_between(dates, volume, facecolor="#B2DCCB")

		
		# Meta
		plt.title(cleanTitle)
		name = "charts/" + symbol + '.png'
		plt.savefig(name)
		plt.legend([l1, l2], ["Price", "Volume"]) # Legend for both

		self.name = name
