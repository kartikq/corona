import sqlite3
import csv
from datetime import datetime
import glob, os
import git
import dateutil.parser

class Dal:
    def __init__(self, data_dir):
        self.conn = sqlite3.connect(data_dir + 'corona.db')

    def __del__(self):
        self.conn.close()
    
    def create_database(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE if not exists cases (date text, country text, region text, confirmed integer, deaths integer, recovered integer)''')
        self.conn.commit()

    def import_data(self, daily_reports_dir, date):
        c = self.conn.cursor()
        files = glob.glob(daily_reports_dir + '*.csv') if date is None else [daily_reports_dir + date + '.csv']
        
        for file in files:
            try:
                with open(file,'r') as fin:
                    dr = csv.DictReader(fin)
                    to_db = [(i['Last Update'], i['Country/Region'], i['Province/State'], i['Confirmed'],i['Deaths'],i['Recovered']) for i in dr]
                    c.executemany("INSERT INTO cases (date, country, region, confirmed, deaths, recovered) VALUES (?, ?, ?, ?, ?, ?);", to_db)
            except:
                continue    
        self.conn.commit()

    def run_query(self, query, *argv):
        c = self.conn.cursor()
        results = c.execute(query,tuple(argv))
        cols = [description[0] for description in c.description]
        return {'columns':cols,'results': results}
    
    def get_max_updated_date(self):
        c = self.conn.cursor()
        c.execute('SELECT max(date) FROM cases')
        return c.fetchone()

    def get_overall_details(self, dt):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR  
        from `cases` where date(date) = date(?) group by country, date(date);
        """
        return self.run_query(query, dt)

    def get_overall_summary(self, dt): 
        query = """select sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?);
        """
        return self.run_query(query, dt)

    def get_country_details(self, dt, country):
        query = """select country, region, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? group by country, region, date(date);
        """
        return self.run_query(query, dt, country)

    def get_country_summary(self, dt, country):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? group by country, date(date);
        """
        return self.run_query(query, dt, country)

    

