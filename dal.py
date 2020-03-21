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
        ddl = """
        CREATE TABLE if not exists cases (date text, country text, region text, confirmed integer, deaths integer, recovered integer, unique(date, country, region)) 
        """
        c.execute(ddl)
        self.conn.commit()
    
    def destroy_database(self):
        c = self.conn.cursor()
        c.execute("""DROP TABLE if exists cases""")
        self.conn.commit()

    def __run_query(self, query, *argv):
        c = self.conn.cursor()
        results = c.execute(query,tuple(argv))
        cols = [description[0] for description in c.description]
        return {'columns':cols,'results': results}

    def insert_case_data(self, rows):
        c = self.conn.cursor()
        query = """
        INSERT OR IGNORE INTO cases (date, country, region, confirmed, deaths, recovered) VALUES (?, ?, ?, ?, ?, ?);
        """
        c.executemany(query, rows)
        self.conn.commit()

    def get_max_updated_date(self):
        c = self.conn.cursor()
        c.execute('SELECT max(date) FROM cases')
        return c.fetchone()[0]

    def get_summary(self, dt, country):
        if country is None:
            return self.get_overall_summary(dt)
        else:
            return self.get_country_summary(dt, country)

    def get_overall_summary(self, dt): 
        query = """select sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?);
        """
        return self.__run_query(query, dt)

    def get_country_summary(self, dt, country):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? group by country, date(date);
        """
        return self.__run_query(query, dt, country)

    def get_details(self, dt, country, region):
        if country is None and region is None:
            return self.get_overall_details(dt)
        elif region is None:
            return self.get_country_details(dt, country)
        else:
            return self.get_country_region_details(dt, country, region)

    def get_overall_details(self, dt):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR  
        from `cases` where date(date) = date(?) group by country, date(date);
        """
        return self.__run_query(query, dt)

    def get_country_details(self, dt, country):
        query = """select country, region, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? group by country, region, date(date);
        """
        return self.__run_query(query, dt, country)

    def get_country_region_details(self, dt, country, region):
        query = """select country, region, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where date(date) = date(?) and country = ? and region = ? group by country, region, date(date);
        """
        return self.__run_query(query, dt, country, region)

    def get_plot_data(self, country, region):
        if country is None:
            query = """
            select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
            from `cases` where country = 'US' group by country, date(date)
            union all
            select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
            from `cases` where country = 'China' group by country, date(date)
            union all
            select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
            from `cases` where country = 'Italy' group by country, date(date)
            union all
            select 'World' as country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
            from `cases` group by date(date) order by date(date) asc;
            """
            return self.__run_query(query)
        return self.get_country_region_plot_data(country, region)

    def get_country_region_plot_data(self, country, region):
        if region is None:
            return self.get_country_plot_data(country)
        
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR, region 
        from `cases` where country = ? and region = ? group by country, region, date(date) order by date(date) asc;
        """
        return self.__run_query(query, country, region)

    def get_country_plot_data(self, country):
        query = """select country, date(date) as date, sum(confirmed) as confirmed, sum(deaths) as deaths, sum(recovered) as recovered, sum(deaths)*1.0/sum(confirmed)*100 as CFR 
        from `cases` where country = ? group by country, date(date) order by date(date) asc;
        """
        return self.__run_query(query, country)
    

