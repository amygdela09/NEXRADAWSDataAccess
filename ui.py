import calendar
from pathlib import Path
import sys
try:
    import ujson as json
except ImportError:
    import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDateTimeEdit, QLabel, QHBoxLayout, QComboBox
import nexradaws

ROOT_DIR = Path(__file__).parent


def create_site_dict(conn):
    sites = {}
    years = conn.get_avail_years()[1:]
    for year in years:
        sites[year] = {}
        for month in range(1, 12):
            sites[year][month] = {}
            days_in_month = calendar.monthrange(int(year), month)[1]
            for day in range(1, days_in_month):
                try:
                    avail_radars = conn.get_avail_radars(int(year), int(month), int(day))
                    sites[year][month][day] = []
                    for radar in avail_radars:
                        sites[year][month][day].append(radar)
                        print(year, month, day, radar)
                except TypeError:  # invalid selection
                    continue
    with open(ROOT_DIR / "sites.json", "w+") as f:
        f.seek(0)
        json.dump(sites, f)
        f.truncate()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = nexradaws.NexradAwsInterface()
        self.setup()

    def dt_edit_hanged(self, event):
        print(event)

    def setup(self):
        # set window size
        self.setGeometry(150, 150, 300, 100)
        # get size of screen for window placement
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        frmX = (screen_size.width() - self.width()) / 2
        frmY = (screen_size.height() - self.height()) / 2
        # move window to center of screen
        self.move(frmX, frmY)
        self.setWindowTitle("Amygdela NEXRAD Viewer")

        vlayout = QVBoxLayout()

        label = QLabel("Select radar site/timeframe for scan")
        label.resize(label.sizeHint())
        vlayout.addWidget(label, alignment=Qt.AlignCenter)

        hlayout1 = QHBoxLayout()

        self.combo_site = QComboBox(disabled=True)  # select a date first
        hlayout1.addWidget(self.combo_site)

        self.dt_edit = QDateTimeEdit(calendarPopup=True)
        self.dt_edit.dateTimeChanged.connect(self.dt_edit_changed)
        hlayout1.addWidget(self.dt_edit, alignment=Qt.AlignCenter)

        vlayout.addLayout(hlayout1)

        self.btn_download = QPushButton("Download")
        vlayout.addWidget(self.btn_download, alignment=Qt.AlignCenter)

        self.setLayout(vlayout)


def run():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    conn = nexradaws.NexradAwsInterface()
    if not Path(ROOT_DIR / "sites.json").exists():
        print("Downloading site availability...")
        create_site_dict(conn)
        print("Done!")
    run()
