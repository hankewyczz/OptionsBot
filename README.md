# OptionsBot

## What is OptionsBot?

A Python-based Discord bot which can be used for fetching stock and options info, charting their price and volume changes, and for trading stocks and options. 

## Installation

You'll need to create a `.env` file with two lines in it:
```
DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
BOT_ADMIN=123456789
```

where `DISCORD_TOKEN` is your discord bot token, and `BOT_ADMIN` is the user ID of whoever will be the admin of this bot (for most cases, use your own user ID).

## Usage
`!ping` : Responds 'pong'

`!op <TICKER> <DATE><TYPE> <STRIKE>`
`(alias: !option)` : Returns information about a specific option. The string formatting is pretty loose (aside from the spacing). Examples: `!op $spy 6/19c 300`, `!op AAPL 4/17p $400.50`, `!op T 1/18/22C 2010.50`

`!ops <TICKER> <DATE>**`
`(alias: !optionchain, !opc)` : Returns information about an options chain. Calling `!ops <TICKER>` will return a list of availible dates, and calling `!ops <TICKER> <DATE>` will return more specific information

`!c <TICKER> <DATE><TYPE> <STRIKE> <DURATION>` : Returns a chart of the price and volume of an option. The formatting is identical to `!op`, with the addition of a <DURATION> field. This takes a numberical value and date type (valid options are 'd', 'm', 'y'). **NOTE**: it is unlikely that data will be availible for the option more than a month back.

`!chartstock <STOCK_TICKER> <DURATION>`
`(alias: !cs)` : Returns a chart of the price and volume of a STOCK

`!buy (<TICKER> OR <TICKER> <DATE><TYPE> <STRIKE>) <N>` : Buys *N* contracts/shares of the given option or stock

`!portfolio` :  Returns the value of your portfolio (broken down into categories)

`!leaderboard` : Returns everyone's standings on the leaderboard"


## Admin-only commands
`!echo msg` : The bot simply echos the given msg

`!add N <@user>` : Adds N dollars to the given user

`!remove N <@user>` : Removes N dollars from the given user


# API
## Yahoo API

This project makes use of Yahoo's financial API, which unfortunatly isn't publically documented. As such, the project makes do with two versons of the API:

* V. 7:
  * V7 of the API is used to fetch contract information, stock information, and option chains
* V. 8:
  * V8 of the API is used to fetch chart data for graphing


Ideally, this project could make use of only one of them. However, it uses both for the following reasons:
* V7 doesn't have a documented method of fetching chart data
  * I didn't have the time to figure it out, and other people had informally documented the process for V8
* V8 changed the format of fetching plain stock/option information
  * I couldn't find any informal documentation about this on V8. Additionally, due to its age, V7 was more throughly (relativly speaking) documented

## Effects
As a result, the API might go under at any time, at Yahoo's discretion. Unless they completly rework it, it should be relativly easy to update the bot. 


  
  
