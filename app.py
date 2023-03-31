from flask import Flask, render_template, url_for, request
import nexradaws
import pytz
from datetime import datetime
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def getDataAWS(radar, sYear, sDay, sMonth, sStartH, sStartM, sEndH, sEndM):
    conn = nexradaws.NexradAwsInterface()

    downloadDirectory = os.getcwd()

    timezone = pytz.timezone('US/Central')
    start = timezone.localize(datetime(sYear, sMonth, sDay, sStartH, sStartM))
    end = timezone.localize(datetime(sYear, sMonth, sDay, sEndH, sEndM))
    scans = conn.get_avail_scans_in_range(start, end, radar)

    results = conn.download(scans, downloadDirectory)

    print(results.success)
    print(results.failed)

    return 'done'


@app.route('/getData', methods=['post', 'get'])
def getData():
    if request.method == 'POST':
        radarSite = request.form['selectedRadar']
        selectedTimeTo = request.form['timeTo']
        selectedTimeFrom = request.form['timeFrom']
        selectedDate = request.form['date']
        sDate = selectedDate.split('/', 2)
        sYear = int(sDate[2])
        sDay = int(sDate[1])
        sMonth = int(sDate[0])
        sTimeTo = selectedTimeTo.split(':', 1)
        sTimeFrom = selectedTimeFrom.split(':', 1)
        sTimeToHR = int(sTimeTo[0])
        sTimeToMIN = int(sTimeTo[1])
        sTimeFromHR = int(sTimeFrom[0])
        sTimeFromMIN = int(sTimeFrom[1])

        return getDataAWS(radarSite, sYear, sDay, sMonth, sTimeFromHR, sTimeFromMIN, sTimeToHR, sTimeToMIN)
    else:
        error = 'Could not post form.'
        return error
