import curses
import json
import re
import time
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join
from pathlib import Path

import culour
import humanfriendly
import humanize
from prettytable import PrettyTable, prettytable
from settings import settings


def timestamp_format(entry):
    entry["x"] = int(entry["x"] / 1000)
    return entry


def repeat_to_length(s, wanted):
    return (s * (wanted // len(s) + 1))[:wanted]


def days_filter(x, hours):
    yesterday = datetime.today() - timedelta(hours=hours)
    return datetime.fromtimestamp(x["x"]) > yesterday


def get_points_from_data(data, hours, current_points):
    def list_filter(x):
        return days_filter(x, hours)

    data_list = list(filter(list_filter, data["series"]))
    data_list = data_list[0] if data_list else None
    if data_list:
        return current_points - data_list["y"]
    else:
        return 0


class COLORS(object):
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def make_green(text):
    return f"{COLORS.GREEN}{text}{COLORS.END}"


def make_red(text):
    return f"{COLORS.RED}{text}{COLORS.END}"


def set_colors(array):
    final_array = []
    for k, row in enumerate(array):
        if k == len(array) - 1:
            final_array.append(row)
            continue
        final_row = []
        for i, cell in enumerate(row):

            def check_points(points):
                if points == 0:
                    return points
                elif points > 0:
                    return make_green(points)
                elif points < 0:
                    return make_red(points)

            if i == 0 or i == 1:
                final_row.append(cell)
            elif i < len(settings["columns"]) + 2:
                final_row.append(check_points(cell))
            else:
                final_row.append(cell)
        final_array.append(final_row)
    return final_array


def get_total_row(final_array):
    array = []
    for i in range(len(settings["columns"]) + 3):
        if i == 0:
            array.append("Total")
        elif i >= len(settings["columns"]) + 2:
            array.append("")
        else:
            array.append(humanize.intcomma(sum(int(row[i]) for row in final_array)))
    return array


def get_array():
    mypath = f"../analytics/{settings['username']}"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    final_array = []
    for streamer in onlyfiles:
        txt = Path(f"{mypath}/{streamer}").read_text()
        try:
            data = json.loads(txt)
        except:  # noqa E722
            continue
        streamer = re.sub(r"\.json$", "", streamer)
        if streamer in settings["blacklist"]:
            continue
        data["series"] = list(map(timestamp_format, data["series"]))
        last_entry = data["series"][-1]
        changes = []
        for column in settings["columns"]:
            changes.append(get_points_from_data(data, column, last_entry["y"]))
        date = datetime.fromtimestamp(last_entry["x"])
        # six_minutes_ago = datetime.today() - timedelta(minutes=5)
        # if not no_colors and date > six_minutes_ago:
        #     streamer = make_green(streamer)
        date = humanize.naturaltime(date)
        final_array.append([streamer, last_entry["y"]] + changes + [date])
    final_array = sorted(final_array, key=lambda x: x[1], reverse=True)
    final_array.append(get_total_row(final_array))
    return final_array


def header():
    result = ["Streamer", "Points"]
    for column in settings["columns"]:
        result.append(humanfriendly.format_timespan(timedelta(hours=column)))
    result.append("Updated")
    return result


def get_table():
    array = get_array()

    if settings["json_filename"]:
        f = open(settings["json_filename"], "w")
        f.write(json.dumps(array))
        f.close()

    if settings["html_filename"]:
        x = PrettyTable(hrules=prettytable.ALL)
        x.field_names = header()
        for streamer in array:
            x.add_row(streamer)
        x.align = "l"
        x.format = True
        f = open(settings["html_filename"], "w")
        f.write(x.get_html_string())
        f.close()

    final_array = set_colors(array)
    x = PrettyTable(hrules=prettytable.ALL)
    x.field_names = header()
    for streamer in final_array:
        x.add_row(streamer)
    x.align = "l"

    return x.get_string().splitlines()


def stats(window):
    window.nodelay(1)
    curses.curs_set(0)
    cycle = 0
    table = get_table()
    while window.getch() not in [ord(x) for x in ["q", "Q"]]:
        cycle += 1
        if cycle == settings["refresh_rate"] * 10:
            table = get_table()
            cycle = 0
        height, width = window.getmaxyx()
        if len(table) < height:
            height = len(table)
        for column in range(height):
            if settings["bugged_terminal"] and table[column][0] == "+":
                window.addstr(
                    column, 0, repeat_to_length("+------", len(table[column]))
                )
            else:
                if settings["debug"]:
                    f = open("log.txt", "a")
                    f.write(table[column] + "\n")
                    f.close()
                culour.addstr(window, column, 0, table[column])
        time.sleep(0.1)


curses.wrapper(stats)
