#!/usr/bin/env python3
import schedule
import time
import os
from dal import Dal
from importer import Importer
from datetime import datetime

def import_job():
    base_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
    data_dir = base_dir + 'data/'
    dal = Dal(data_dir)
    importer = Importer(data_dir, dal)
    print('importing ' + str(datetime.now()))
    importer.import_date(datetime.now())

schedule.every().hour.do(import_job)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)