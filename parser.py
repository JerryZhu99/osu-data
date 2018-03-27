

def parse_file(path: str) -> dict:
    data = open(path, 'r').read()
    return parse(data)


def parse(data: str) -> dict:
    parsed = {}

    lines = data.split("\n")
    lines = [line for line in lines if not (
        line.startswith("//") or line == "")]

    parsed["version"] = lines[0]

    general = lines.index("[General]")
    editor = lines.index("[Editor]")
    metadata = lines.index("[Metadata]")
    difficulty = lines.index("[Difficulty]")
    events = lines.index("[Events]")
    timingpoints = lines.index("[TimingPoints]")
    colours = lines.index("[Colours]")
    hitobjects = lines.index("[HitObjects]")

    parsed.update(parse_general(lines[general + 1:editor]))
    parsed.update(parse_editor(lines[editor + 1:metadata]))
    parsed.update(parse_metadata(lines[metadata + 1:difficulty]))
    parsed.update(parse_difficulty(lines[difficulty + 1:events]))
    parsed.update(parse_events(lines[events + 1:timingpoints]))
    return parsed


def parse_key_vals(lines: [str], strings: [str], integers: [str],
                   decimals: [str], booleans: [str]) -> dict:
    parsed = {}
    for line in lines:
        print(line)
        (prop, val) = [s.strip() for s in line.split(":")]
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
    integers = ["BeatDivisor", "GridSize", "TimelineZoom"]
    decimals = ["DistanceSpacing"]
    booleans = []
    parsed = parse_key_vals(lines, strings, integers, decimals, booleans)
    parsed["Bookmarks"] = [int(s) for s in parsed["Bookmarks"].split(",")]
    return parsed


def parse_metadata(lines: [str]) -> dict:
    strings = ["Title", "TitleUnicode", "Artist",
               "ArtistUnicode", "Creator", "Version", "Source", "Tags"]
    integers = ["BeatmapID", "BeatmapSetID"]
    decimals = []
    booleans = []
    parsed = parse_key_vals(lines, strings, integers, decimals, booleans)
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


def parse_hitobjects(lines: [str]) -> dict:
    return {}


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1]
    parsed = parse_file(filepath)
    print(parsed)
