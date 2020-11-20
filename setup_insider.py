import helper as scraper
import sqlalchemy as db
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

if __name__ == '__main__':
	con = db.create_engine("sqlite:///C:/Users/zheji/Desktop/TradingTools/fundamentalDB.sqlite")
	stocks = pd.read_csv('constituents_csv.csv').Ticker.unique()
	for stock in stocks[8:]:
		check = stock.split('.')
		if len(check)!= 1:
			print("Can't get info for ", stock)
			continue
		print("Getting insider transactions for ", stock)
		reports = scraper.get_historical_links(stock, 15)
		xml = scraper.find_all_xml(reports)
		df = scraper.get_filing_data(xml)
		df.to_sql('insider', con, if_exists='append', index = False)
