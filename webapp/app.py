from datetime import datetime
from pathlib import Path

import nexradaws
import pytz
from flask import Flask, render_template, request

# from flask_assets import Environment, Bundle

app = Flask(__name__)
# uncomment to use sass/scss (this is just for changing styling of materialize)
# assets = Environment(app)
# bundles = {
  # 'example_style': Bundle(
            # 'SCSS/materialize.scss',
            # filters='pyscss',
            # output='Gen/materialize.css',
  # )
# }
# assets.register(bundles)

@app.route("/")
def index():
    sitefile = open("sites.txt", "r")
    sitefiledata = sitefile.read()
    sitelist = sitefiledata.split("\n")
    return render_template("index.html", sites=sitelist)


def getDataAWS(radar, sYear, sDay, sMonth, sStartH, sStartM, sEndH, sEndM):
    conn = nexradaws.NexradAwsInterface()

    downloadDirectory = f"{Path.cwd()}/Data/"

    timezone = pytz.timezone("US/Central")
    start = timezone.localize(datetime(sYear, sMonth, sDay, sStartH, sStartM))
    end = timezone.localize(datetime(sYear, sMonth, sDay, sEndH, sEndM))

    scans = conn.get_avail_scans_in_range(start, end, radar)

    results = conn.download(scans, downloadDirectory)

    print(results.success)
    print(results.failed)

    return "done"


@app.route("/getData", methods=["post"])
def getData():
    if request.method == "POST":
        radarSite = request.form["selectedRadar"]
        selectedTimeTo = request.form["timeTo"]
        selectedTimeFrom = request.form["timeFrom"]
        selectedDate = request.form["date"]
        sDate = selectedDate.split("/", 2)
        sYear = int(sDate[2])
        sDay = int(sDate[1])
        sMonth = int(sDate[0])
        sTimeTo = selectedTimeTo.split(":", 1)
        sTimeFrom = selectedTimeFrom.split(":", 1)
        sTimeToHR = int(sTimeTo[0])
        sTimeToMIN = int(sTimeTo[1])
        sTimeFromHR = int(sTimeFrom[0])
        sTimeFromMIN = int(sTimeFrom[1])

        try:
            results = getDataAWS(
                radarSite,
                sYear,
                sDay,
                sMonth,
                sTimeFromHR,
                sTimeFromMIN,
                sTimeToHR,
                sTimeToMIN,
            )
        except TypeError or ValueError or IndexError:
            results = "Error retrieving data"
        return results
    else:
        error = "Could not post form"
        return error
