from datetime import datetime
import urllib.request
import json
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as mtick
import numpy as np


baseURL = "https://query1.finance.yahoo.com/v8/finance/chart/"
	
def getData(symbol, length):
	url = baseURL + symbol + "?range=" + str(length) + "d&includePrePost=false&interval=2m"
	print(url)

	with urllib.request.urlopen(url) as thisUrl:
		data = json.loads(thisUrl.read().decode())

	try:
		time = data['chart']['result'][0]['timestamp']
		price = data['chart']['result'][0]['indicators']['quote'][0]['close']
		volume = data['chart']['result'][0]['indicators']['quote'][0]['volume']
		prevClose = data['chart']['result'][0]['meta']['previousClose']
	except:
		raise ValueError("Not enough data for a graph")


	price = extrapolateData(price, prevClose, True)
	volume = extrapolateData(volume, 0, False)

	return time, price, volume


def extrapolateData(data, prev, append):
	new = []
	for d in data:
		if d == None:
			new.append(prev)
		else:
			new.append(d)
			if append:
				prev = d
	return new



def drawGraph(x, y, vol, title):
	yMax = max(2, int(np.max(y)))
	yMin = int(np.min(y))
	yRange = int((yMax - yMin) / 2)

	fig, ax1 = plt.subplots()

	
	dates = [datetime.fromtimestamp(xs) for xs in x]

	ax1.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
	ax1.xaxis.set_major_locator(md.MinuteLocator(interval=60))

	fmt = '${x:,.0f}'
	tick = mtick.StrMethodFormatter(fmt)
	ax1.yaxis.set_major_formatter(tick)

	ax1.set_xlim(xmin = np.min(dates), xmax = np.max(dates))
	ax1.set_ylim(ymin = max(0, yMin - yRange), ymax = yMax + yRange)



	ax2 = ax1.twinx()
	ax2.set_ylim(ymin = 0, ymax = max(vol) * 2)

	ax2.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
	ax2.xaxis.set_major_locator(md.MinuteLocator(interval=120))

	ax2.plot(dates, vol, "#B2DCCB", label="Volume")
	ax2.fill_between(dates, vol, facecolor="#B2DCCB")
	ax1.plot(dates, y, "#00A95D", label="Price")
	ax1.fill_between(dates, y, facecolor="#00A95D")
	
	plt.title(title)
	plt.legend()
	name = "charts/" + title + '.png'
	plt.savefig(name)
	return name


def generateChart(symbol, length):
	time, price, volume = getData(symbol, length)
	return drawGraph(time, price, volume, symbol)

#https://query1.finance.yahoo.com/v8/finance/chart/TSLA?range=1d&includePrePost=false&interval=5m
