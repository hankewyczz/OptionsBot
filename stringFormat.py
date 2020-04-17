# formatStrike(String strike)
# Formats the decimals of the stock price
def formatStrike(strike):
	# Properly appends a decimal to the strike price
	if "." in strike:
		strikeSplit = len(strike.split(".")[1])

		if len(strikeSplit) > 3:
			strike += "." + strikeSplit[:3] # Truncates it
		else:
			for i in range(strikeSplit, 3):
				strike += "0"
	else:
		strike += ".000"

	strikeAsString = formatStrikeAsString(strike)
	return strike, strikeAsString


# formatStrikeAsString(String strike) 
# Formats the strike price as a string for the contracts symbol (eg. 00030000)
def formatStrikeAsString(strike):
	# Gets the stock price as a string
	strikeAsString = re.sub('[^0-9]', '', strike)
	for i in range(len(strikeAsString), 8):
		strikeAsString = "0" + strikeAsString # Adds leading 0s to fill the string

	return strikeAsString