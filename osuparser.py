""" A module for parsing .osu files.
"""


def parse_file(path: str) -> dict:
    """Parses the .osu file at the given path."""
    data = open(path, 'r', encoding="utf8").read()
    return parse(data)


def parse(data: str) -> dict:
    """Parses the given osu data."""
    parsed = {}

    lines = [i.strip() for i in data.split("\n")]

    parsed["File Version"] = lines[0]

    def data_range(category: str):
        if category in lines:
            i = lines.index(category)
            if "" in lines[i:]:
                return lines[i + 1: lines.index("", i)]
            else:
                return lines[i + 1: len(lines)]
        else:
            return []

    parsed.update(parse_general(data_range("[General]")))
    parsed.update(parse_editor(data_range("[Editor]")))
    parsed.update(parse_metadata(data_range("[Metadata]")))
    parsed.update(parse_difficulty(data_range("[Difficulty]")))
    parsed.update(parse_events(data_range("[Events]")))
    parsed.update(parse_timingpoints(data_range("[TimingPoints]")))
    parsed.update(parse_colours(data_range("[Colours]")))
    parsed.update(parse_hitobjects(data_range("[HitObjects]")))

    return parsed


def parse_key_vals(lines: [str], strings: [str], integers: [str],
                   decimals: [str], booleans: [str]) -> dict:
    """Parses the given lines, processing integers, decimals, and booleans."""
    parsed = {}
    for line in lines:
        (prop, val) = [s.strip() for s in line.split(":", 1)]
        if prop in strings:
            parsed[prop] = val
        elif prop in integers:
            parsed[prop] = int(val)
        elif prop in decimals:
            parsed[prop] = float(val)
        elif prop in booleans:
            parsed[prop] = bool(val)
    return parsed


def parse_general(lines: [str]) -> dict:
    strings = ["AudioFilename", "SampleSet"]
    integers = ["AudioLeadIn", "PreviewTime", "Mode"]
    decimals = ["StackLeniency"]
    booleans = ["Countdown", "LetterboxInBreaks", "WidescreenStoryboard"]
    return parse_key_vals(lines, strings, integers, decimals, booleans)


def parse_editor(lines: [str]) -> dict:
    strings = ["Bookmarks"]
    integers = ["BeatDivisor", "GridSize"]
    decimals = ["DistanceSpacing", "TimelineZoom"]
    booleans = []
    parsed = parse_key_vals(lines, strings, integers, decimals, booleans)
    if "Bookmarks" in parsed:
        parsed["Bookmarks"] = [int(s) for s in parsed["Bookmarks"].split(",")]
    return parsed


def parse_metadata(lines: [str]) -> dict:
    strings = ["Title", "TitleUnicode", "Artist",
               "ArtistUnicode", "Creator", "Version", "Source", "Tags"]
    integers = ["BeatmapID", "BeatmapSetID"]
    decimals = []
    booleans = []
    parsed = parse_key_vals(lines, strings, integers, decimals, booleans)
    if "Tags" in parsed:
        parsed["Tags"] = parsed["Tags"].split(" ")
    return parsed


def parse_difficulty(lines: [str]) -> dict:
    strings = []
    integers = []
    decimals = ["HPDrainRate", "CircleSize", "OverallDifficulty",
                "ApproachRate", "SliderMultiplier", "SliderTickRate"]
    booleans = []
    return parse_key_vals(lines, strings, integers, decimals, booleans)


def parse_events(lines: [str]) -> dict:
    return {}


def parse_timingpoints(lines: [str]) -> dict:
    return {}


def parse_colours(lines: [str]) -> dict:
    return {}


def parse_hitobjects(lines: [str]) -> dict:
    hitobjects = []
    for line in lines:
        (x, y, time, type_data, hitSounds, *extras) = line.split(",", 5)
        type_data = int(type_data)
        object_type = [1, 0, 0]
        if (type_data & 0x0000010) > 0:
            object_type = [0, 1, 0]
        if (type_data & 0x0001000) > 0:
            object_type = [0, 0, 1]

        hitobjects.append({
            "x": int(x),
            "y": int(y),
            "time": int(time),
            "type": object_type,
            "newCombo": bool(type_data & 0x0000100),
            "hitSounds": int(hitSounds),
            "extras": extras
        })
    return {"HitObjects": hitobjects}


if __name__ == "__main__":
    import sys
    import pprint
    filepath = sys.argv[1]
    parsed = parse_file(filepath)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(parsed)
