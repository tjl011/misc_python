#!/usr/bin/python3

"""
Script that analyzes a company's closing stock price and displays that as a graph
@author Thomas Ludwig

Usage:
This program takes the CSV file as input via the -i argument. It expects
that the CSV file has a header line and has the same column layout as the
"goog.csv" file in this repository. 

This program can either generate an output file containing the graphs (the
output file path is specified via the -o argument) or
generates the graph in a separate window.

The user is also give the option to specify the long-term window (specified
by the -l) and the short-term window (specifed by the -s argument). The user
can specify days or weeks by appending a "d" to the aforementioned arguments
for days and "w" or nothing for weeks.
"""

import argparse
import sys
import csv
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import pandas


def process_csv_file(fpath):
    """ Retrieves the date and closing stock price listed in the CSV
        file specified by fpath
        Inputs
        fpath - path to the input CSV file. The CSV file is assumed to contain
                a header line as well as having the first column as the Dates
                (day-Month-year) and the fifth column contains the closing
                price.

        Exceptions:
        ValueError - will be raised if the program fails to interpret a Date
        IOError - failure to open or read from the input file

        returns - A list of tuples consisting of the parsed dates (as datetime
                  objects)
                  and the closing price. The tuples are sorted by date.
    """
    with open(fpath, "r") as f:
        reader = csv.reader(f)
        data = [row for row in reader]
        data = data[1:] # skip over the header
        # get the date, closing price
        data = [(datetime.strptime(r[0], "%d-%b-%y"), float(r[4])) for r in data]

    # sort by date
    data = sorted(data, key=lambda x: x[0])
    return data


def plot_data(data, out_file=None, long_win=28, short_win=14):
    """ Processes the input data and plots the curves.
        Inputs
        data - list of (Date, closing price) tuples
        out_file - path to file that graphs will be written to, if not
                  specified, the figures will be displayed in a popup
                  window
        long_win - long-term smoothing window, in days (defaults to 4 weeks)
        short_win - short-term smoothign window, in days (defaults to 2 weeks)

    """

    dates = [d[0] for d in data]
    prices = [p[1] for p in data]

    lt_av = pandas.ewma(np.asarray(prices), span=long_win)
    st_av = pandas.ewma(np.asarray(prices), span=short_win)

    diff_ltst = len(lt_av) * [0.0]

    for i in range(len(diff_ltst)):
        diff_ltst[i] = lt_av[i] - st_av[i]

    diff_ltst_av = pandas.ewma(np.asarray(diff_ltst), span=(1.5 * 7))

    diff_av_diff = len(diff_ltst_av) * [0.0]
    for i in range(len(diff_av_diff)):
        diff_av_diff[i] = diff_ltst[i] - diff_ltst_av[i]

    years = matplotlib.dates.YearLocator()   # every year
    months = matplotlib.dates.MonthLocator()  # every month
    years_fmt = matplotlib.dates.DateFormatter('%Y')

    #fig, ax = plt.subplots()
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.set_title("Analysis of Google Stock Price")

    ax.plot(dates, diff_ltst, label="diff_ltst")
    ax.plot(dates, diff_ltst_av, label="diff_ltst_av")
    ax.plot(dates, diff_av_diff, label="diff_av_diff")

    ax.legend(loc="lower left", prop={'size': 7})
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)
    ax.set_xlabel("Date (Years, Months)")
    ax.set_ylabel("Closing Price (Dollars)")

    ax = fig.add_subplot(212)
    ax.plot(dates, prices, label="Closing")
    ax.plot(dates, lt_av, label="lt_av")
    ax.plot(dates, st_av, label="st_av")
    ax.legend(loc="upper left", prop={'size': 7})
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)
    ax.set_xlabel("Date (Years, Months)")
    ax.set_ylabel("Closing Price (Dollars)")

    if out_file is None:
        plt.show()
    else:
        plt.savefig(out_file)


def __convert_input(val):
    """ Interpret and user input from weeks to days.
        val - input specified by end-user. Must be a str with a number followed
              by either "w", "d", or nothing. 'w' stands for weeks,
              "d" stands for days. If there is
              no identifier, we the end user specified weeks
        returns a float representing the number of days
    """
    if val[-1] == 'w':
        return float(val[:-1]) * 7
    elif val[-1] == 'd':
        return float(val[:-1])
    else:
        return float(val) * 7


def __interpret_args():
    """ Function that instantiates argument parser and interprets
        user arguments.
    """
    parser = argparse.ArgumentParser(description="analysis of stock price")
    parser.add_argument("-i", "--input_file", action="store", nargs='?', required=True)
    parser.add_argument("-o", "--output_file", action="store", nargs='?')
    parser.add_argument("-l", "--long", action="store", nargs='?', default="4w")
    parser.add_argument("-s", "--short", action="store", nargs='?', default="2w")
    return parser.parse_args()


def __main():
    """ Main entry point of the script.
    """
    args = __interpret_args()
    out_fpath = args.output_file
    short_win = __convert_input(args.short)
    long_win = __convert_input(args.long)
    try:
        data = process_csv_file(args.input_file)
        plot_data(data, out_fpath, short_win, long_win)
    except IOError as err:
        print("IOError: " + str(err))
        sys.exit(1)
    except ValueError as err:
        print("ValueError: " + str(err))
        sys.exit(1)


if __name__ == "__main__":
    __main()
