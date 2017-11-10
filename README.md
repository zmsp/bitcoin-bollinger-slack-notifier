Sends bitcoin price notification to slack. Uses bollinger bands algorithm to decide optimal buy and sell price and uses coinbase to get the current price. 

Requirements:

`
pandas
`

# How to run
Update config.py to match your prefered slack configuration.

Then run `python btc-alert.py` 