import git
import glob, os
from os import path
import csv
import dateutil.parser

class Importer:
    def __init__(self, data_dir, dal):
        self.dal = dal
        self.data_dir = data_dir
        self.daily_reports_dir = data_dir + '/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

    def __pull_latest_data(self):
        repo = git.Repo(os.path.dirname(os.path.realpath(__file__)))
        for submodule in repo.submodules:
            submodule.update(init=True, to_latest_revision=True)

    def __normalize_country_names(self, country):
        if country=='Mainland China':
            return 'China'
        else: 
            return country

    def __get_by_substr(self, d, s):
        # ugly hack because the file headers are often mangled
        for k in d.keys(): 
            if s.lower() in k.lower():
                return d[k]
        return None

    def __get_date_from_file(self, filepath):
        # ugly hack to use date from filename instead of column because column values are incorrect
        base=os.path.basename(filepath)
        return os.path.splitext(base)[0]

    def __import_files(self, files):
        for file in files:
            with open(file,'r') as fin:
                dr = csv.DictReader(fin)
                # do not use 'Last Update' column from file, it is often incorrect instead infer date from file name
                date_from_file = dateutil.parser.parse(self.__get_date_from_file(file)).strftime('%Y-%m-%d')
                to_db = [(date_from_file, self.__normalize_country_names(self.__get_by_substr(i, 'Country')), self.__get_by_substr(i,'State'), self.__get_by_substr(i,'Confirmed'), self.__get_by_substr(i,'Deaths'), self.__get_by_substr(i,'Recovered'), self.__get_by_substr(i,'Lat'), self.__get_by_substr(i, 'Long')) for i in dr]
                self.dal.insert_case_data(to_db)

    def import_date(self, date):
        self.__pull_latest_data()
        date_formatted = date.strftime('%m-%d-%Y')
        file = self.daily_reports_dir + date_formatted + '.csv'
        if path.exists(file):
            self.__import_files([file])

    def import_all(self):
        self.dal.destroy_database()
        self.dal.create_database()
        self.__pull_latest_data()
        files = glob.glob(self.daily_reports_dir + '*.csv')
        self.__import_files(files)