# OptionsBot

## What is OptionsBot?

A Python-based Discord bot which can be used for fetching stock and options info, charting their price and volume changes, and for trading stocks and options. 

The main point of this was to create a bot for trading options contracts - the rest evolved as addons to the bot. 

## Installation

You'll need to create a `.env` file with two lines in it:
```
DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
BOT_ADMIN=123456789
```

where `DISCORD_TOKEN` is your discord bot token, and `BOT_ADMIN` is the user ID of whoever will be the admin of this bot (for most cases, use your own user ID).

## Usage
`!ping` : Responds 'pong'

`!op <TICKER> <DATE><TYPE> <STRIKE>`\n`(alias: !option)` : Returns information about a specific option. The string formatting is pretty loose (aside from the spacing). Examples: `!op $spy 6/19c 300`, `!op AAPL 4/17p $400.50`, `!op T 1/18/22C 2010.50`

`!ops <TICKER> <DATE>**`\n`(alias: !optionchain, !opc)` : Returns information about an options chain. Calling `!ops <TICKER>` will return a list of availible dates, and calling `!ops <TICKER> <DATE>` will return more specific information

`!c <TICKER> <DATE><TYPE> <STRIKE> <DURATION>` : Returns a chart of the price and volume of an option. The formatting is identical to `!op`, with the addition of a <DURATION> field. This takes a numberical value and date type (valid options are 'd', 'm', 'y'). **NOTE**: it is unlikely that data will be availible for the option more than a month back.

`!chartstock <STOCK_TICKER> <DURATION>`\n`(alias: !cs)` : Returns a chart of the price and volume of a STOCK

`!buy (<TICKER> OR <TICKER> <DATE><TYPE> <STRIKE>) <N>` : Buys *N* contracts/shares of the given option or stock

`!portfolio` :  Returns the value of your portfolio (broken down into categories)

`!leaderboard` : Returns everyone's standings on the leaderboard"


## Admin-only commands
`!echo msg` : The bot simply echos the given msg

`!add N <@user>` : Adds N dollars to the given user

`!remove N <@user>` : Removes N dollars from the given user


## Troubleshooting

99% of the time, any bot errors are due to users forgetting how to format commands. Hopefully, all of these cases have been covered, but in the off chance I missed one, restarting the bot should do the trick.

If the bot completely stops working, odds are Yahoo changed their API. This will result in one of two cases: 

- 1) They just changed the URL scheme, in which case, a fix should take minutes
- 2) They completely rewrote their API / removed it from public view / restricted it, in which case a fix will take a while (and might not be worthwile). 
