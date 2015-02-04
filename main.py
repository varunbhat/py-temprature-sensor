#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import argparse
from ConfigParser import RawConfigParser
from temperusb.temper import TemperHandler
from DbFunctions import _ImageWeatherDb
import os

from SqlQueries import *

config = "../etc/config.cfg"


class pigpio:
    def __init__(self):
        self.db = _ImageWeatherDb(config=config)
        self._configparser = RawConfigParser(allow_no_value=True)


    def getTemp(self):
        th = TemperHandler()
        devs = th.get_devices()
        readings = []

        for i, dev in enumerate(devs):
            readings.append({'device': i,
                             'temperature_c': dev.get_temperature(),
                             'temperature_f': dev.get_temperature(format="fahrenheit"),
                             'ports': dev.get_ports(),
                             'bus': dev.get_bus()
            })
        return readings

    def get_hour_count(self):
        res = self.db.execute(SQL_QUERIES['CONSOLIDATE_RAW_COUNT']).next()[0]
        if res is None:
            return (0, 0, 0)
        else:
            return res

    def get_day_count(self):
        res = self.db.execute(SQL_QUERIES['CONSOLIDATE_HOURLY_COUNT']).next()[0]
        if res is None:
            return (0, 0, 0)
        else:
            return res

    def insert_hour_count(self, temp):
        return self.db.execute(SQL_QUERIES['PUT_HOURLY_COUNT'] % temp)

    def insert_min_count(self, temp):
        return self.db.execute(SQL_QUERIES['PUT_MIN_COUNT'] % temp)

    def insert_day_count(self, temp):
        return self.db.execute(SQL_QUERIES['PUT_DAILY_COUNT'] % temp)

    def truncate_day_s_raw_count(self):
        self.db.execute(SQL_QUERIES['PURGE_RAW_COUNT'])


def main():
    global config

    parser = argparse.ArgumentParser(description='pitemp DbWriter..')
    parser.add_argument("-f", "--configfile", type=str, help="use configuration file")
    parser.add_argument("-t", "--type", type=str, help="Run Type Options:\n\t 'hourly'\n\t 'minute'\n\t daily")

    args = parser.parse_args()

    if args.configfile is not None and args.configfile != '':
        if os.path.exists(args.configfile):
            config = args.configfile

    if args.type is not None and args.type in ['hourly', 'minute', 'daily']:
        ds = pigpio()
        if args.type == 'minute':
            res = ds.getTemp()[0]['temperature_c']
            print("Previous min Temp:", res)
            ds.insert_min_count(res)

        elif args.type == 'hourly':
            res = ds.get_hour_count()
            print("Previous Hour Temp:", res)
            ds.insert_hour_count(res)

        elif args.type == 'daily':
            res = ds.get_day_count()
            print("Previous day Temp:", res)
            ds.insert_day_count(res)
            # ds.truncate_day_s_raw_count()

    else:
        print("Please run with `type` arguement\nRun Type Options:\n\t '--type=hourly'\n\t '--type=minute'\n\t --type=daily")


if __name__ == "__main__":
    main()