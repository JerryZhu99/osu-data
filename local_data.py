import os

import osuparser


def get_paths(osu_path: str) -> [dict]:
    files = []
    for (root, _, filenames) in os.walk(osu_path + "\\songs"):
        for file in filenames:
            if file[-4:] == ".osu":
                files.append(os.path.join(root, file))
    return files


def get_beatmaps(osu_path: str) -> [dict]:
    filepaths = get_paths(osu_path)
    songs = [osuparser.parse_file(file) for file in filepaths]
    return songs


def main():
    import sys
    beatmaps = get_beatmaps(sys.argv[1])
    for beatmap in beatmaps:
        print(beatmap["Title"] + " / " + beatmap["Version"])


if __name__ == '__main__':
    main()
