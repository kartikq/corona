import sqlite3
import csv
from datetime import datetime
import glob, os
import git
import dateutil.parser
import sys

class Dal:
    def __init__(self, data_dir):
        self.conn = sqlite3.connect(data_dir + 'corona.db')

    def __del__(self):
        self.conn.close()
    
    def create_database(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE if not exists cases (date text, country text, region text, confirmed integer, deaths integer, recovered integer)''')
        self.conn.commit()

    def cleanup_province_key(self, d):
        # ugly hack because the file headers are often mangled
        if 'Province/State' in d.keys():
            return d['Province/State']
        if '\ufeffProvince/State' in d.keys():
            return d['\ufeffProvince/State']
    
    def get_date_from_file(self, filepath):
        # ugly hack to use date from filename instead of column because column values are incorrect
        base=os.path.basename(filepath)
        return os.path.splitext(base)[0]

    def import_data(self, daily_reports_dir, date):
        c = self.conn.cursor()
        files = glob.glob(daily_reports_dir + '*.csv') if date is None else [daily_reports_dir + date + '.csv']
        
        for file in files:
            try:
                with open(file,'r') as fin:
                    dr = csv.DictReader(fin)
                    # do not use 'Last Update' column from file, it is often incorrect
                    date_from_file = dateutil.parser.parse(self.get_date_from_file(file)).strftime('%Y-%m-%d')
                    print(date_from_file)
                    to_db = [(date_from_file, i['Country/Region'], self.cleanup_province_key(i), i['Confirmed'],i['Deaths'],i['Recovered']) for i in dr]
                    c.executemany("INSERT INTO cases (date, country, region, confirmed, deaths, recovered) VALUES (?, ?, ?, ?, ?, ?);", to_db)
            except:
                print(sys.exc_info())
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

    def get_country_region_details(self, dt, country, region):
        query = """select country, region, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? and region = ? group by country, region, date(date);
        """
        return self.run_query(query, dt, country, region)

    def get_country_region_plot_data(self, country, region):
        query = """select country, region, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where country = ? and region = ? group by country, region, date(date) order by date(date) asc;
        """
        return self.run_query(query, country, region)

    def get_country_plot_data(self, country):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where country = ? group by country, date(date) order by date(date) asc;
        """
        return self.run_query(query, country)
    

