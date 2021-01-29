Sends bitcoin price notification to slack. Uses bollinger bands algorithm to decide optimal buy and sell price and uses coinbase to get the current price. 
Bollinger Bands investment strategy: https://www.investopedia.com/articles/technical/102201.asp


Requirements: see the requirement.txt

# How to run
Update config.py to match your prefered slack configuration.

Then run `python btc-alert.py` 