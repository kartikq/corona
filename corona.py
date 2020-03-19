#!/usr/bin/env python3
import os
from datetime import datetime
import dateutil.parser
import click
from tabulate import tabulate
from dal import Dal
import matplotlib.pyplot as plt
from importer import Importer

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

def plot_data(x, y, title, xlabel, ylabel):
    plt.scatter(x, y, s=60, c='red', marker='^')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

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

    if country is None:
        # world wide numbers
        if summary:
            # world wide summary
            print_table(dal.get_overall_summary(dt))
        else:
            # world wide details - country wise breakdown
            print_table(dal.get_overall_details(dt))
    else:
        # specific country is provided
        if region:
            if plot:
                # chart confirmed cases in specific country / region
                data = dal.get_country_region_plot_data(country, region)
                x,y = zip(*((dateutil.parser.parse(result[2]).strftime('%m-%d'),result[3]) for result in data['results']))
                plot_data(x,y, 'Number of confirmed cases in ' + region + ' / ' + country, 'Date', 'Confirmed')
            else:
                # specific region details
                print_table(dal.get_country_region_details(dt, country, region))
        elif plot:
            # chart confirmed cases in specific country
            data = dal.get_country_plot_data(country)
            x,y = zip(*((dateutil.parser.parse(result[1]).strftime('%m-%d'),result[2]) for result in data['results'] if result[1] is not None))
            plot_data(x,y, 'Number of confirmed cases in ' + country, 'Date', 'Confirmed')
        elif summary:
            # specific country summary
            print_table(dal.get_country_summary(dt, country))
        else:
            # specific country detail - lists all regions with stats
            print_table(dal.get_country_details(dt, country))

if __name__ == '__main__':
    execute_command()