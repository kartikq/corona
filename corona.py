#!/usr/bin/env python3
import os
from datetime import datetime
import dateutil.parser
import click
from tabulate import tabulate
from dal import Dal
import matplotlib.pyplot as plt
from matplotlib import style
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
    columns = results['columns']
    print(tabulate(res,headers=columns))

def plot_data(results, *titles):
    style.use('dark_background')
    res = results['results']
    columns = results['columns']
    data = pd.DataFrame(res, columns=columns)
    data_pivot1 = data.pivot(index='date', columns='country', values=['confirmed'])
    data_pivot2 = data.pivot(index='date', columns='country', values=['deaths'])
    plt.close('all')
    fig, axes = plt.subplots(nrows=1,ncols=2,figsize=(12,6))
    data_pivot1.plot(ax = axes[0], title=titles[0])
    data_pivot2.plot(ax = axes[1], title=titles[1])
    for ax in axes:
        # Fix odd formatting of labels with pivot tables
        handles, labels = ax.get_legend_handles_labels()
        labels_new = [label.strip('()').split(',')[1] for label in labels]
        ax.legend(handles,labels_new)
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

    if summary:
        print_table(dal.get_summary(dt, country))
        exit(0)
    
    if plot:
        data = dal.get_plot_data(country, region)
        title1 = 'Confirmed cases {} {}'
        title2 = 'Deaths {} {}'
        rgn = '' if region is None else region
        cntry = 'US, China, Italy, Worldwide' if country is None else country
        plot_data(data, title1.format(rgn,cntry), title2.format(rgn, cntry))
        exit(0)

    print_table(dal.get_details(dt, country, region))

if __name__ == '__main__':
    execute_command()