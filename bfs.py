import pandas as pd
import json
import requests as r
import sched, time
from datetime import datetime, timedelta
import os

runner_df = pd.read_csv('../Dixon-Coles-Football-Predictor-master/pred.csv', dtype=str)

def refresh_odds(row):

	marketId = str(row['MarketId'])
	
	url  = 'https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=GBP&locale=en_GB&marketIds='+marketId+'&rollupLimit=2&rollupModel=STAKE&types=MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST'

	res = r.get(url)

	data = res.json()
	
	eventNodes  = data['eventTypes'][0]['eventNodes']

	for events in eventNodes:

		for marketNodes in events['marketNodes']:

			homePrice = marketNodes['runners'][0]['exchange']['availableToBack'][0]['price']
			awayPrice = marketNodes['runners'][1]['exchange']['availableToBack'][0]['price']
			drawPrice = marketNodes['runners'][2]['exchange']['availableToBack'][0]['price']

			runner_df.loc[row.name,'BFCHome'] = homePrice
			runner_df.loc[row.name,'BFCDraw'] = drawPrice
			runner_df.loc[row.name,'BFCAway'] = awayPrice

			# Calculate the margins
			runner_df.loc[row.name,'HomeMargin'] = float(runner_df.loc[row.name,'BFCHome']) - float(runner_df.loc[row.name,'DCHome'])
			runner_df.loc[row.name,'DrawMargin'] = float(runner_df.loc[row.name,'BFCDraw']) - float(runner_df.loc[row.name,'DCDraw'])
			runner_df.loc[row.name,'AwayMargin'] = float(runner_df.loc[row.name,'BFCAway']) - float(runner_df.loc[row.name,'DCAway'])

runner_df.apply(refresh_odds, axis=1)

print (runner_df)