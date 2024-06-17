import sys
from datetime import datetime
from pathlib import Path

import nexradaws
import pytz
from loguru import logger
from tqdm import tqdm


class NullWriter(object):
    def write(self, arg):
        pass


class InvalidSelectionError(Exception):
    """Raised when the user makes an invalid selection during the download prompts"""


null_writer = NullWriter()
old_stdout = sys.stdout

# connect to aws
logger.info("Connecting to AWS")
conn = nexradaws.NexradAwsInterface()


def select_year():
    logger.info("Gathering available years")
    avail_years = conn.get_avail_years()
    logger.info(avail_years)
    selected_year = input("Select Year: ")
    if selected_year not in avail_years:
        raise InvalidSelectionError("Invalid year selection")
    return selected_year


def select_month(year):
    logger.info("Gathering available months")
    try:
        avail_months = conn.get_avail_months(year)
        logger.info(avail_months)
        selected_month = input("Select Month: ")
        if selected_month not in avail_months:
            raise InvalidSelectionError("Invalid month selection")
        return selected_month
    except (TypeError, ValueError) as e:
        raise InvalidSelectionError(f"{str(e)}. Invalid month selection")


def select_day(year, month):
    logger.info("Gathering available days")
    try:
        avail_days = conn.get_avail_days(year, month)
        logger.info(avail_days)
        day = input("Select Day: ")
        if day not in avail_days:
            raise InvalidSelectionError("Invalid day selection")
        return day
    except (TypeError, ValueError) as e:
        raise InvalidSelectionError(f"{str(e)}. Invalid year or month selection")


def select_site(year, month, day):
    logger.info("Gathering available radar sites")
    try:
        avail_radars = conn.get_avail_radars(year, month, day)
        logger.info(avail_radars)
        site = input("Select Radar Site: ")
        if site not in avail_radars:
            raise InvalidSelectionError("Invalid radar site selection")
        return site
    except (TypeError, ValueError) as e:
        InvalidSelectionError(f"{str(e)}. Invalid year, month, and/or day selection")


def select_times(year, month, day, site):
    timezone = pytz.timezone("US/Central")
    userstart = input("Start Time (hh:mm): ").split(":")
    userend = input("End Time (hh:mm): ").split(":")
    try:
        start = timezone.localize(
            datetime(
                int(year), int(month), int(day), int(userstart[0]), int(userstart[1])
            )
        )
        end = timezone.localize(
            datetime(int(year), int(month), int(day), int(userend[0]), int(userend[1]))
        )
        return start, end
    except (ValueError, TypeError, IndexError) as e:
        raise InvalidSelectionError(f"{str(e)}. Invalid time selection")


def gather_scans(start, end, site):
    logger.info("Gathering available scans")
    try:
        avail_scans = conn.get_avail_scans_in_range(start, end, site)
    except TypeError:
        raise InvalidSelectionError(
            f"No scans found for site {site} and times {start} through {end}"
        )
    logger.info(
        f"There are {len(avail_scans)} Nexrad files available for {start} - {end}"
    )
    return avail_scans


def download_scan(site: str, avail_scans: list, download_path: str | Path):
    if isinstance(download_path, str):
        download_path = Path(download_path).resolve()
    download_path.mkdir(parents=True, exist_ok=True)
    for i in tqdm(avail_scans):
        current_indice = avail_scans.index(i)
        sys.stdout = null_writer  # disable output
        conn.download(avail_scans[current_indice], download_path)
        sys.stdout = old_stdout  # enable output
    logger.success(f"Scan downloaded to {download_path}")
    sys.exit(0)


def main():
    try:
        year = select_year()
        month = select_month(year)
        day = select_day(year, month)
        site = select_site(year, month, day)
        start_time, end_time = select_times(year, month, day, site)
        scans = gather_scans(start_time, end_time, site)

        if scans is None or len(scans) == 0:
            logger.error(
                f"No scans found for site {site} and time {start_time} through {end_time}. Starting from beginning..."
            )
            main()

        userchoice = input("Download Nexrad? ")
        if userchoice.casefold() in ("yes", "y", "download"):
            download_path = Path.cwd() / f"Data/{site}/{year}"
            download_scan(site, scans, download_path)
        else:
            logger.info("Returning to the beginning")
            return None

    except InvalidSelectionError as e:
        logger.error(f"{str(e)}. Starting from beginning...")
        main()


if __name__ == "__main__":
    main()
