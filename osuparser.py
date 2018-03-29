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
    events = {}
    events["Breaks"] = []
    start = lines.index("//Break Periods") + 1
    end = lines.index("//Storyboard Layer 0 (Background)")
    for line in lines[start:end]:
        (_, start_time, end_time) = line.split(",")
        events["Breaks"].append({
            "start": start_time,
            "end": end_time
        })
    return events


def parse_timingpoints(lines: [str]) -> dict:
    points = []
    last_ms_per_beat = 0.0
    for line in lines:
        (offset, ms_per_beat, meter, _, _, _, _, _) = line.split(",")
        ms_per_beat = float(ms_per_beat)
        if ms_per_beat < 0:
            print(offset, ms_per_beat, meter)
            ms_per_beat = last_ms_per_beat / (-0.01 * ms_per_beat)
        else:
            last_ms_per_beat = ms_per_beat
        points.append({
            "time": float(offset),
            "msPerBeat": ms_per_beat,
            "bpm": round(60 * 1000 / float(ms_per_beat), 2),
            "meter": int(meter)
        })
    return {"TimingPoints": points}


def parse_colours(lines: [str]) -> dict:
    return {}


def parse_hitobjects(lines: [str]) -> dict:
    hitobjects = []
    for line in lines:
        items = line.split(",")
        if(len(items) == 5):
            (x, y, time, type_data, hitSounds) = items
            extras = ""
        else:
            (x, y, time, type_data, hitSounds, extras) = line.split(",", 5)
        type_data = int(type_data)
        object_type = "circle"
        if (type_data & 0b0000010) > 0:
            object_type = "slider"
        if (type_data & 0b0001000) > 0:
            object_type = "spinner"

        if object_type == "circle" or object_type == "spinner":
            hitobjects.append({
                "x": int(x),
                "y": int(y),
                "time": int(time),
                "type": object_type,
                "newCombo": bool(type_data & 0x0000100),
                "hitSounds": int(hitSounds),
                "extras": extras
            })
        elif object_type == "slider":
            (slider_points, repeat, pixelLength, *_) = extras.split(",")
            (slider_type, *points) = slider_points.split("|")
            points = [p.split(":") for p in points]
            points = [{"x": p[0], "y": p[1]} for p in points]
            repeat = int(repeat) - 1
            pixelLength = float(pixelLength)
            endx = int(x)
            endy = int(y)
            if repeat % 2 == 0:
                endx = points[-1]["x"]
                endy = points[-1]["y"]
            hitobjects.append({
                "x": int(x),
                "y": int(y),
                "time": int(time),
                "type": object_type,
                "newCombo": bool(type_data & 0x0000100),
                "hitSounds": int(hitSounds),
                "endx": endx,
                "endy": endy,
                "slider_type": slider_type,
                "points": points,
                "repeat": repeat,
                "length": pixelLength
            })
    return {"HitObjects": hitobjects}


if __name__ == "__main__":
    import sys
    import pprint
    filepath = sys.argv[1]
    parsed = parse_file(filepath)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(parsed)
