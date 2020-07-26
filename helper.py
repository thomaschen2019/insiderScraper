from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd
import sqlalchemy as db


def get_historical_links(stock):
    start = 0
    links = []
    while start % 100 == 0:
        url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=include&action=getcompany&type=4&count=100&start={}".format(stock.lower(), start)
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read())
        nameList = bsObj.findAll('a')
        for link in nameList:
            sep = link.get('href').split('/')
            if 'Archives' in sep and 'data' in sep:
                links.append(link.get('href'))
                start = start + 1
    print(len(links))
    return links

def find_all_reports_today():
    html = urlopen("https://www.sec.gov/cgi-bin/current?q1=0&q2=0&q3=4") 
    bsObj = BeautifulSoup(html.read())
    nameList = bsObj.findAll('a')
    reports_link = []
    for link in nameList:
        sep = link.get('href').split('/')
        if link.text in ['4', '4/A']:
            reports_link.append(link.get('href'))
    return reports_link

def find_all_xml(reports_web_link):
    xml_reports_link = []
    for link in reports_web_link:
        print("Getting ", link)
        url = 'https://sec.gov'+link
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read())
        nameList = bsObj.findAll('a') 
        for link in nameList:
            filename = link.text
            if 'xml' in filename.split('.'):
                xml_reports_link.append(link.get('href'))
    return xml_reports_link

def get_filing_data(xml_reports_link):
    all_trans = []
    for xml in xml_reports_link:
        url = "https://sec.gov" + xml
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read())
        #print(bsObj)
        symbol = bsObj.issuertradingsymbol.text
        name = bsObj.reportingowner.reportingownerid.rptownername.text
        owner = bsObj.reportingownerrelationship
        person_type_map = {'0010': 'major holder',
                           '0100': 'officer',
                           '1000': 'director',
                           '0001': 'other',
                           'unknown': None}
        try:
            person_type = owner.isdirector.text + owner.isofficer.text\
                + owner.istenpercentowner.text +owner.isother.text
            title = owner.officertitle.text
            person_type = person_type_map[person_type]
        except:
            print("Erorr Finding Owner Type")
            person_type = 'unknown'
        for trans in bsObj.findAll('nonderivativetransaction'):
            try:
                trans_type = trans.transactioncode.text
            except:
                print("Error Finding Transaction Type")
                trans_type = None
            try:
                all_trans.append({'ticker':symbol, 
                                  'trans_date':trans.transactiondate.value.string,
                                  'price':float(trans.transactionpricepershare.value.string),
                                  'num_shares':int(float(trans.transactionshares.value.string)),
                                  'direction':trans.transactionacquireddisposedcode.value.string,
                                  'trans_type': trans_type,
                                  'name':name,
                                  'position':title,
                                  'person_type':person_type,
                                  'owned_shares': int(float(trans.sharesownedfollowingtransaction.value.string)),})
            except Exception as e:
                print("Error {} occured for getting filing data for {}".format(e, symbol))
                print(url)
    df = pd.DataFrame(all_trans)
    print(df.shape)
    df = df.drop_duplicates()
    print(df.shape)
    return df