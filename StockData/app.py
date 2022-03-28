from math import ceil
from datetime import datetime
import pandas as pd
import requests
from functions import crsr, connection, create_overview_table, create_quotes_table, create_news_table, create_disclosure_table

payload = {}
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.otcmarkets.com',
    'Referer': 'https://www.otcmarkets.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
    'Cookie': 'ak_bmsc=344F105A52AE06813CC467A0CFBF54B2~000000000000000000000000000000~YAAQvZ82F95Cx7t/AQAA8VHVxw+5LtEeUMRJLrS+Iw6tNbiC3ZITvnh5HjsLfsfq+NC0yM9toEy8doTyupd5s+AfwKCWiVQDjT+sF/DQAT7CiRXw3KoVLCa6hDiTIkaYRJhFzIAqDA+jM9mQyLdB/DNB4cPdcyj0phfg1X2tq4aISDxtB9Rr3JPGEmyxhlUsGUotU3WvQyg2w6dDXW1Ya6JUs6iAvVw7PdZFkpi20UNeXrBZc5fU/RaUCGMAaV9V9otdbFSNQEaDg1QRrtQalg4G9C8RXevEkfyoPdcsS1UXXJ2Ecld76bNfUeFUWsI9c8aCf2+8R/Jpvg3PSaCgLT/KKnSIyM5m2uuJDuyYsZLllPVP78wa/mhU8PL+a5KF7AR+wyoAXioMqbs=; bm_sv=142F3243ABC3CB01E3911EFD3E6F62FF~G9vmKVVuMyw8ET8Nrv7MEAWIhlaDAjdzixybLBpDDA7AUsvlf6n/KazlcQ/QXxBGJghTmk3LCXFRsEi8Dbp643vjA63oWxz7EuAAlYh6me+hG4EQ5tOhFhCfGCbR2Lf1jjhaw1coI/txpOJdNXhjD717/cqY5tKHXctuPO/R1dI='
}


def convert_todate(t):
    ts = int(str(t)[:-3])
    # print(ts)
    return datetime.utcfromtimestamp(ts).strftime('%m/%d/%Y')


def get_overview(data):
    p = {
        "Open": data["Open"],
        "Daily Range": data["Daily Range"],
        "Volume": data["Volume"],
        "MARKET CAP": data['MARKET CAP']
    }
    df = pd.DataFrame([p])
    df.to_csv("Overview.csv", index=False)
    print("Overview updated!")
    sql = '''
            INSERT INTO overview_table (OPEN_,Daily_Range,Volume,MARKET_CAP)
            VALUES(?,?,?,?)
          '''
    val = (data["Open"], data["Daily Range"], data["Volume"], data['MARKET CAP'])
    crsr.execute(sql, val)
    connection.commit()
    get_disclosure()


def get_quote():
    url = "https://backend.otcmarkets.com/otcapi/stock/trade/inside/GZIC?symbol=GZIC"

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()

    p = {
        "Open": data["openingPrice"],
        "Daily Range": str(data["dailyLow"]) + "-" + str(data["dailyHigh"]),
        "Volume": data['volume'],
        "PREv CLOSE": data['previousClose'],
        "52Wk Range": data['annualLow'],
        "Average Vol (30D)": data['thirtyDaysAvgVol'],
        "BEST BID": str(data["bidPrice"]) + "x" + str(data['bidSize']),
        "BEST ASK": str(data['askPrice']) + "x" + str(data['askSize']),
        "MARKET CAP": data['marketCap'],
        "SHARES OUT": data['sharesOutstanding']
    }

    df = pd.DataFrame([p])
    df.to_csv("Quote.csv", index=False)
    sql = '''INSERT INTO quotes_table (Open_,Daily_Range,Volume,PREv_CLOSE,fifty_two_Wk_Range,Average_Vol_30D,BEST_BID,BEST_ASK,MARKET_CAP,SHARES_OUT) VALUES(?,?,?,?,?,?,?,?,?,?)'''
    val = (
    p["Open"], p["Daily Range"], p["Volume"], p["PREv CLOSE"], p["52Wk Range"], p["Average Vol (30D)"], p["BEST BID"],
    p["BEST ASK"], p["MARKET CAP"], p["SHARES OUT"])
    crsr.execute(sql, val)
    connection.commit()
    print("Quotes updated!")
    get_overview(p)


def get_news():
    url = "https://backend.otcmarkets.com/otcapi/company/GZIC/external/news?symbol=GZIC&page=1&pageSize=10&sortOn=1&sortDir=D"

    response = requests.request("GET", url, headers=headers, data=payload)

    total_items = int(response.json()['totalRecords']) / 25
    page = 1
    limit = 25
    for i in range(ceil(total_items)):
        url = f"https://backend.otcmarkets.com/otcapi/company/GZIC/external/news?symbol=GZIC&page={page}&pageSize={limit}&sortOn=1&sortDir=D"
        response = requests.request("GET", url, headers=headers, data=payload)
        data_s = response.json()["records"]
        for data in data_s:
            p = {
                "Press Release": data['formattedPublishedDate'],
                "TITLE": data['headline'],
                "NAME": data['sourceName']
            }
            sql = '''
                        INSERT INTO news_table (Press_Release,TITLE,NAME_)
                        VALUES(?,?,?)
                      '''
            val = (p["Press Release"], p["TITLE"], p["NAME"])
            crsr.execute(sql, val)
            connection.commit()
            df = pd.DataFrame([p])
            try:
                t = pd.read_csv("News.csv")
                df.to_csv("News.csv", index=False, mode="a", header=False)
            except FileNotFoundError:
                df.to_csv("News.csv", index=False)
        page += 1
    print("News updated!")


def get_disclosure():
    url = "https://backend.otcmarkets.com/otcapi/company/GZIC/financial-report?symbol=GZIC&page=1&pageSize=10&statusId=A&sortOn=releaseDate&sortDir=DESC"

    response = requests.request("GET", url, headers=headers, data=payload)

    total_items = int(response.json()['totalRecords']) / 25
    page = 1
    limit = 25
    for i in range(ceil(total_items)):
        url = f"https://backend.otcmarkets.com/otcapi/company/GZIC/financial-report?symbol=GZIC&page={page}&pageSize={limit}&statusId=A&sortOn=releaseDate&sortDir=DESC"
        response = requests.request("GET", url, headers=headers, data=payload)
        data_s = response.json()["records"]
        for data in data_s:
            p = {
                "PUBLISH DATE": convert_todate(data["createdDate"]),
                "TITLE": data['name'],
                "PERIOD END DATE": convert_todate(data['periodDate']),
                "STATUS": data['statusId']
            }
            sql = '''INSERT INTO disclosure_table (PUBLISH_DATE,TITLE,PERIOD_END_DATE,STATUS) VALUES(?,?,?,?)'''
            val = (p["PUBLISH DATE"], p["TITLE"], p["PERIOD END DATE"], p['STATUS'])
            crsr.execute(sql, val)
            connection.commit()
            df = pd.DataFrame([p])
            try:
                t = pd.read_csv("Disclosure.csv")
                df.to_csv("Disclosure.csv", index=False, mode="a", header=False)
            except FileNotFoundError:
                df.to_csv("Disclosure.csv", index=False)
        page += 1
    print("Disclosure updated!")
    get_news()


create_news_table()
create_overview_table()
create_quotes_table()
create_disclosure_table()
get_quote()
print("process Completed")
