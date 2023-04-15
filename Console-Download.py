import nexradaws
from pathlib import Path
from tqdm import tqdm
import sys
import pytz
from datetime import datetime


class NullWriter(object):
    def write(self, arg):
        pass


error1 = 'Invalid Selection'
nullwrite = NullWriter()
oldstdout = sys.stdout

# connect to aws
print('Connecting to Aws')
conn = nexradaws.NexradAwsInterface()


def func1():
    print('Gathering available years')
    availyears = conn.get_avail_years()
    print(availyears)
    year = input('Select Year: ')
    func2(year)


def func2(year):
    print('Gathering available months')
    try:
        availmonths = conn.get_avail_months(year)
        print(availmonths)
        month = input('Select Month: ')
        func3(year, month)
    except TypeError or ValueError:
        print(error1)
        func1()


def func3(year, month):
    print('Gathering available days')
    try:
        availdays = conn.get_avail_days(year, month)
        print(availdays)
        day = input('Select Day: ')
        func4(year, month, day)
    except TypeError or ValueError:
        print(error1)
        func2(year)


def func4(year, month, day):
    print('Gathering available radar sites')
    try:
        availradars = conn.get_avail_radars(year, month, day)
        print(availradars)
        radar = input('Select Radar Site: ')
        func5(year, month, day, radar)
    except TypeError or ValueError:
        print(error1)
        func3(year, month)


def func5(year, month, day, radar):
    timezone = pytz.timezone('US/Central')
    userstart = input('Start Time (hh:mm): ').split(":")
    userend = input('End Time (hh:mm): ').split(":")
    try:
        start = timezone.localize(datetime(int(year), int(month), int(day), int(userstart[0]), int(userstart[1])))
        end = timezone.localize(datetime(int(year), int(month), int(day), int(userend[0]), int(userend[1])))
    except ValueError or TypeError or IndexError:
        print(error1)
        func4(year, month, day)

    print('Gathering available scans')
    # noinspection PyTypeChecker
    availscans = conn.get_avail_scans_in_range(start, end, radar)
    # print("There are " + str(len(availscans)) + " Nexrad files available for the selected time\n")
    print(f"There are {len(availscans)} Nexrad  files available for {start} - {end}")
    userchoice = input('Download Nexrad? ')
    if userchoice.casefold() in ('yes', 'y', 'download'):
        downloadthefiles(availscans)
    else:
        print('Returning to the beginning')
        func1()


def downloadthefiles(availscans):
    downloadlocation = f"{Path.cwd()}/Data/"
    for i in tqdm(availscans):
        currentindice = availscans.index(i)
        sys.stdout = nullwrite  # disable output
        conn.download(availscans[currentindice], downloadlocation)
        sys.stdout = oldstdout  # enable output
    print('Download Complete.')
    exit()


# start the process
func1()
