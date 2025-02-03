# -*- coding: utf-8 -*-
"""
Program to change subtitle track names to "Français" and "Français (forcé)" 
and skip empty subtitle tracks based on track size in MKV files.
"""

import os
import subprocess
import json
from tkinter import Tk, filedialog

def change_subtitle_track_names_by_size(mkv_file):
    mkvmerge_path = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
    mkvpropedit_path = mkvmerge_path.replace('mkvmerge.exe', 'mkvpropedit.exe')

    print(f"Processing file: {mkv_file}")

    try:
        result = subprocess.run([mkvmerge_path, '-J', mkv_file], capture_output=True, text=True, check=True, encoding='utf-8')
        info = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running mkvmerge: {e.stderr}")
        return

    subtitle_tracks = []
    for track in info['tracks']:
        if track['type'] == 'subtitles':
            track_number = track['properties']['number']
            size = int(track['properties'].get('tag_number_of_bytes', 0))
            current_name = track['properties'].get('track_name', '')
            subtitle_tracks.append((track_number, size, current_name))

    subtitle_tracks.sort(key=lambda x: x[1], reverse=True)

    print("Tracks and their sizes:")
    for track_number, size, current_name in subtitle_tracks:
        print(f"Track {track_number}: Size = {size} bytes, Current Name = '{current_name}'")

    for i, (track_number, size, current_name) in enumerate(subtitle_tracks):
        if size == 0:
            continue

        if i == 0 and current_name != "Français":
            new_name = "Français"
            commands = ["--edit", f"track:{track_number}", "--set", f"name={new_name}"]
        elif i == 1 and current_name != "Français (forcé)":
            new_name = "Français (forcé)"
            commands = ["--edit", f"track:{track_number}", "--set", f"name={new_name}"]
        else:
            continue

        try:
            full_command = [mkvpropedit_path, mkv_file] + commands
            subprocess.run(full_command, check=True, capture_output=True, text=True)
            print(f"Updated track {track_number}: Old Name = '{current_name}', New Name = '{new_name}'")
        except subprocess.CalledProcessError as e:
            print(f"Error during mkvpropedit execution for track {track_number}.")


def select_mkv_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    mkv_folder = filedialog.askdirectory(title="Select Folder Containing MKV Files")
    root.destroy()
    return mkv_folder

def process_all_mkv_files_in_directory(directory):
    mkv_files = [f for f in os.listdir(directory) if f.endswith('.mkv')]
    for mkv_file in mkv_files:
        mkv_file_path = os.path.join(directory, mkv_file)
        change_subtitle_track_names_by_size(mkv_file_path)

if __name__ == "__main__":
    mkv_folder = select_mkv_folder()
    if mkv_folder:
        process_all_mkv_files_in_directory(mkv_folder)
    else:
        print("No folder selected.")
