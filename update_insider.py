import helper as scraper
import sqlalchemy as db
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

if __name__ == '__main__':
	con = db.create_engine("sqlite:///C:/Users/zheji/Desktop/TradingTools/fundamentalDB.sqlite")
	reports = scraper.find_all_reports_today()
	xml = scraper.find_all_xml(reports)
	df = scraper.get_filing_data(xml)
	df.to_sql('insider', con)