from flask import Flask, render_template, url_for, request
import nexradaws
import pytz
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
def getDataAWS(radar,sYear,sDay,sMonth,sStartH,sStartM,sEndH,sEndM):
    conn = nexradaws.NexradAwsInterface()

    downloadDirectory = os.getcwd()

    central_timezone = pytz.timezone('US/Central')
    start = central_timezone.localize(datetime(sYear,sMonth,sDay,sStartH,sStartM))
    end = central_timezone.localize (datetime(sYear,sMonth,sDay,sEndH,sEndM))
    scans = conn.get_avail_scans_in_range(start, end, radar)

    print('There are {} scans available between {} and {}\n'.format(len(scans), start, end))

    results = conn.download(scans, downloadDirectory)

    print(results.success)
    print(results.failed)
    
    return results.success
    
@app.route('/getData', methods=['post','get'])
def getData():
    error = None
    if request.method == 'POST':
        radarSite = request.form['selectedRadar']
        selectedTimeTo = request.form['timeTo']
        selectedTimeFrom = request.form['timeFrom']
        selectedDate = request.form['date']
        ssDate = selectedDate.split('/', 2)
        ssYear = int(ssDate[2])
        ssDay = int(ssDate[1])
        ssMonth = int(ssDate[0])
        ssTimeTo = selectedTimeTo.split(':', 1)
        ssTimeFrom = selectedTimeFrom.split(':', 1)
        ssTimeToHR = int(ssTimeTo[0])
        ssTimeToMIN = int(ssTimeTo[1])
        ssTimeFromHR = int(ssTimeFrom[0])
        ssTimeFromMIN = int(ssTimeFrom[1])
        
        return getDataAWS(radarSite, ssYear, ssDay, ssMonth, ssTimeFromHR, ssTimeFromMIN, ssTimeToHR, ssTimeToMIN)
    else:
        error = 'Could not post form.'
        return error