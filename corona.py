#!/usr/bin/env python3

import sqlite3
import csv
from datetime import datetime
import glob, os
import git
import dateutil.parser
import click
from tabulate import tabulate
from dal import Dal

def pull_latest_data(data_dir):
    g = git.cmd.Git(data_dir + 'COVID-19/')
    g.pull() 

def initialize():
    base_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
    data_dir = base_dir + 'data/'
    daily_reports_dir = data_dir + '/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

    dal = Dal(data_dir)
    dal.create_database()
    dt_raw = dal.get_max_updated_date()[0]

    if (dt_raw is None) or (datetime.now().date() > dateutil.parser.parse(dt_raw).date()):
        pull_latest_data(data_dir)
        if dt_raw is None: 
            dal.import_data(daily_reports_dir, dt_raw) 
        else:
            dal.import_data(daily_reports_dir, datetime.now().strftime('%m-%d-%Y'))
        dt_raw = dal.get_max_updated_date()[0]
    
    return {'dal': dal, 'last_update': dt_raw}

def print_table(results):
    res = results['results']
    headers = results['columns']
    print(tabulate(res,headers=headers))

@click.command()
@click.option('--country', default=None, help='filter by country')
@click.option('--region', default=None, help='filter by region (requires country)')
@click.option('--summary', is_flag=True, help='print summary statistics')
@click.option('--date', default=None, help='filter by date YYYY-MM-DD')
def execute_command(country, region, summary, date):
    """This CLI presents COVID-19 case data - updated daily"""
    config = initialize()

    dt = date if date is not None else config['last_update']
    dal = config['dal']

    if country is None:
        if summary:
            print_table(dal.get_overall_summary(dt))
        else:
            print_table(dal.get_overall_details(dt))
    else: 
        if summary:
            print_table(dal.get_country_summary(dt, country))
        else:
            print_table(dal.get_country_details(dt, country))

if __name__ == '__main__':
    execute_command()