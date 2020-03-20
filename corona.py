#!/usr/bin/env python3
import os
from datetime import datetime
import dateutil.parser
import click
from tabulate import tabulate
from dal import Dal
import matplotlib.pyplot as plt
from importer import Importer
import pandas as pd

def initialize():
    base_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
    data_dir = base_dir + 'data/'
    dal = Dal(data_dir)
    importer = Importer(data_dir, dal)
    return {'dal': dal, 'importer': importer}

def print_table(results):
    res = results['results']
    headers = results['columns']
    print(tabulate(res,headers=headers))

@click.command()
@click.option('--country', default=None, help='filter by country')
@click.option('--region', default=None, help='filter by region (requires country)')
@click.option('--summary', is_flag=True, help='print summary statistics')
@click.option('--date', default=None, help='filter by date YYYY-MM-DD')
@click.option('--plot', is_flag=True, help='plot trends, (requires country or country + region arguments)')
@click.option('--reload', is_flag=True, help='reload all data')
def execute_command(country, region, summary, date, plot, reload):
    """Command line interface for COVID-19 statistics.
    Data sourced from Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL).
    https://systems.jhu.edu/research/public-health/ncov/
    """
    config = initialize()
    dal = config['dal']
    importer = config['importer']
    
    if reload:
        importer.import_all()
        exit(0)

    dt = date if date is not None else dal.get_max_updated_date()

    if summary:
        print_table(dal.get_summary(dt, country))
        exit(0)
    
    if plot:
        if country is not None:
            data_raw = dal.get_plot_data(country, region)
            data = pd.DataFrame(data_raw['results'], columns=data_raw['columns'])
            plt.close('all')
            data.plot('date',y=['confirmed','deaths'])
            plt.show()  
        exit(0)

    print_table(dal.get_details(dt, country, region))

if __name__ == '__main__':
    execute_command()