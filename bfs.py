import pandas as pd
import json
import requests as r
import sched, time
from datetime import datetime, timedelta
import os

scheduler = sched.scheduler(time.time, time.sleep)

marketId = input("Betfair market ID: ")
sampleRate = input("Sample rate (in seconds): ")

url  = 'https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=GBP&locale=en_GB&marketIds='+marketId+'&rollupLimit=2&rollupModel=STAKE&types=MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST'

runner_df = pd.DataFrame()

def refresh_odds(runner_df):
	
	res = r.get(url)

	data = res.json()
	
	eventNodes  = data['eventTypes'][0]['eventNodes']

	for events in eventNodes:

		for marketNodes in events['marketNodes']:

			# Making a countdown to event begins timer
			current_time = datetime.now()
			current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
			eventStart   = marketNodes['description']['marketTime']
			eventStart   = datetime.strptime(eventStart, '%Y-%m-%dT%H:%M:%S.%fZ')
			current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")			
			timeDelta    = ( eventStart + timedelta(hours=1)) - current_time

			homeTeam  = marketNodes['runners'][0]['description']['runnerName']
			homePrice = marketNodes['runners'][0]['exchange']['availableToBack'][0]['price']

			awayTeam  = marketNodes['runners'][1]['description']['runnerName']
			awayPrice = marketNodes['runners'][1]['exchange']['availableToBack'][0]['price']

			drawPrice = marketNodes['runners'][2]['exchange']['availableToBack'][0]['price']

			runner_dict = { 'LastMove':current_time,
							'TimeDelta':timeDelta,
						    'HomeTeam':homeTeam,
						    'AwayTeam':awayTeam,
						    'HomeBackPrice':homePrice,
						    'DrawBackPrice':drawPrice,
						    'AwayBackPrice':awayPrice
						   }

			if runner_df.empty:
				runner_df = runner_df.append( runner_dict, ignore_index=True )
			
			last_odds = runner_df.tail(1).reset_index()
			
			if ( ( last_odds.loc[0, ['HomeBackPrice'] ].values[0] != runner_dict['HomeBackPrice'] ) | 
				 ( last_odds.loc[0, ['DrawBackPrice'] ].values[0] != runner_dict['DrawBackPrice'] ) | 
				 ( last_odds.loc[0, ['AwayBackPrice'] ].values[0] != runner_dict['AwayBackPrice'] ) ):

				runner_df = runner_df.append( runner_dict, ignore_index=True )
				runner_df = runner_df[['LastMove','TimeDelta','HomeTeam','AwayTeam','HomeBackPrice','DrawBackPrice','AwayBackPrice']]

				last_odds = runner_df.tail(1).reset_index()

				print ("LAST ODDS: \r\n",last_odds)

	scheduler.enter(float(sampleRate), 1, refresh_odds, (runner_df,))

scheduler.enter(float(sampleRate), 1, refresh_odds, (runner_df,) )

scheduler.run()



