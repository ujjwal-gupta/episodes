# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

# For more information about TheTVDB.com's API, visit
# http://thetvdb.com/wiki/index.php?title=Programmers_API

# TO DO:
#   Fix bug in table.py where UTF-8 encoded unicode messes with the character
#     count.

import argparse, urllib2, datetime, random, re, xml.etree.ElementTree as et
from table import table, menu


DATE_FORMAT = "{:%d %B %Y}"     # For viewing air date in season information.
DESCRIPTION_LIMIT = 80          # Number of characters to display.

KEY = "F6C8EF890E843081"
MIRROR_URL = "http://thetvdb.com/api/{key}/mirrors.xml"
SERIES_URL = '{mirror}/api/GetSeries.php?seriesname="{name}"'
EPISODE_URL = "{mirror}/api/{key}/series/{series_id}/all/en.xml"


def season_information(series):
    # Randomly selects a mirror to connect to.
    response = urllib2.urlopen(MIRROR_URL.format(key=KEY))
    xml = response.read()
    root = et.fromstring(xml)

    mirrors = root.findall("Mirror")
    if len(mirrors) < 1:
        print "Warning: No mirrors found. Failing over to TheTVDB.com..."
        mirror = "http://thetvdb.com"
    else:
        mirror = grab(mirrors[random.randint(0, len(mirrors) - 1)],
                      "mirrorpath")
        print "Mirror: {}".format(mirror)

    # Identify the series by name, and retrieve its ID from TheTVDB.com.
    print "Search: {}".format(series)

    series = series.replace(" ", "%20")
    response = urllib2.urlopen(SERIES_URL.format(mirror=mirror, name=series))
    xml = response.read()
    root = et.fromstring(xml)

    series = root.findall("Series")

    if len(series) == 1:
        series_id = grab(series[0], "seriesid")
        series_name = grab(series[0], "SeriesName")

    else:
        rows = []
        for i in xrange(len(series)):
            name = grab(series[i], "SeriesName")
            aired = grab(series[i], "FirstAired")
            if aired is not None:
                aired = "{:%Y}".format(datetime.datetime.strptime(aired,
                                       "%Y-%m-%d"))
            rows.append((i + 1, name, aired))

        choice = menu("Matches", *zip(*rows), headers=["#", "Series Name",
                      "First Aired"], input_range=range(1, len(series) + 1),
                      footer="To select a series, enter its number.")
        series_id = grab(series[int(choice) - 1], "seriesid")
        series_name = grab(series[int(choice) - 1], "SeriesName")

    print "Series Name: {}".format(series_name)
    print "Series ID: {}".format(series_id)

    # Retrieve the episode list for the series.
    response = urllib2.urlopen(EPISODE_URL.format(mirror=mirror, key=KEY,
                               series_id=series_id))
    xml = response.read()
    root = et.fromstring(xml)

    episodes = [{"season": grab(e, "SeasonNumber", int),
                "episode": grab(e, "EpisodeNumber", int),
                "name": grab(e, "EpisodeName"),
                "date": grab(e, "FirstAired", lambda d: DATE_FORMAT.format(
                             datetime.datetime.strptime(d, "%Y-%m-%d"))),
                "description": grab(e, "Overview")}
                for e in root.findall("Episode")]

    # Show table of seasons, with the number of episodes in them.
    episodes.sort(key=lambda e: e["episode"])
    episodes.sort(key=lambda e: e["season"])

    season_list = list({e["season"] for e in episodes})
    season_list.sort()

    # Turn episodes into a dictionary, organizing the episodes into seasons.
    # The reason I chose a dict of lists, rather than a list of lists, is
    # because some shows have a season 0 (which usually means specials, etc.),
    # while others start at season 1. A dict allows us to index directly to
    # season 1 in either case.
    episodes = {s: [e for e in episodes if e["season"] == s]
                for s in season_list}

    # Optionally display episode information for each season.
    done = False
    while not done:
        s = menu("Season Information", season_list, [len(episodes[s]) for s in
                 season_list], headers=["Season", "Episodes"],
                 footer="Enter a season number for more information. (ENTER to"
                 " continue.)", input_range=season_list+[""])
        if s:
            s = int(s)
            rows = [(e["episode"], e["name"], e["date"],
                    short_description(e["description"])) for e in episodes[s]]
            #print rows
            menu("Season {}".format(s), *zip(*rows), headers=["Episode",
                 "Name", "Air Date", "Description"],
                 footer="ENTER to continue.")
        else:
            done = True

    return episodes


def grab(parent, child, convert=None):
    child = parent.find(child)
    if child is not None: child = child.text
    if child is not None:
        if convert: child = convert(child)
        else: child = child.encode("utf-8")     # Important. Watch for Unicode.
    return child


def short_description(description):
    if description:
        description = description.replace("\n", " ")
        if len(description) > DESCRIPTION_LIMIT:
            description = description[0:DESCRIPTION_LIMIT-2]
            description = re.sub(r"\W+\w*$", r"...", description)
    return description


if __name__ == "__main__":
    description = "Fetches season and episode information from TheTVDB.com. " \
                  "Please consider contributing."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("series", help="The name of the television series.",
                        nargs="+")
    args = parser.parse_args()

    season_information(" ".join(args.series))