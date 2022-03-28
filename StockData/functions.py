import pyodbc

# conn = pyodbc.connect('Driver={SQL Server};'
#                       'Server=RON\SQLEXPRESS;'
#                       'Database=Stock_DB;'
#                       'Trusted_Connection=yes;')
#
# cursor = conn.cursor()


import sqlite3

# connecting to the database
connection = sqlite3.connect("Stocks_DB.db")

# cursor
crsr = connection.cursor()

def create_overview_table():
    sql_command = """CREATE TABLE IF NOT EXISTS overview_table ( 
    OPEN_ VARCHAR(200), 
    Daily_Range VARCHAR(200), 
    Volume INT(500), 
    MARKET_CAP INT(500));"""

    # execute the statement
    crsr.execute(sql_command)

    # close the connection
    print("Overview table created.")


def create_quotes_table():
    sql_command = """CREATE TABLE IF NOT EXISTS quotes_table ( 
    Open_ VARCHAR(200),
    Daily_Range VARCHAR(200),
    Volume INT(100),
    PREv_CLOSE VARCHAR(20),
    fifty_two_Wk_Range VARCHAR(100),
    Average_Vol_30D VARCHAR(200),
    BEST_BID VARCHAR(100),
    BEST_ASK VARCHAR(100),
    MARKET_CAP INT(200),
    SHARES_OUT INT(200)
    );"""

    # execute the statement
    crsr.execute(sql_command)

    # close the connection
    print("Quotes table created.")


def create_disclosure_table():
    sql_command = """CREATE TABLE IF NOT EXISTS disclosure_table ( 
    PUBLISH_DATE DATE,
    TITLE VARCHAR(200),
    PERIOD_END_DATE DATE,
    STATUS VARCHAR(10));"""

    # execute the statement
    crsr.execute(sql_command)

    # close the connection
    print("disclosure table created.")


def create_news_table():
    sql_command = """CREATE TABLE IF NOT EXISTS news_table ( 
    Press_Release VARCHAR(200),
    TITLE VARCHAR(300),
    NAME_ VARCHAR(100));"""

    # execute the statement
    crsr.execute(sql_command)

    # close the connection
    # connection.close()
    print("News table created.")
