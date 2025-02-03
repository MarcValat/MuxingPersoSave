# -*- coding: utf-8 -*-
"""
Program to change audio track names based on language flags and codec information in MKV files
"""

import os
import subprocess
import json
from tkinter import Tk, filedialog

def change_audio_track_names_by_language(mkv_file):
    mkvmerge_path = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
    mkvpropedit_path = mkvmerge_path.replace('mkvmerge.exe', 'mkvpropedit.exe')

    # Get the current track information
    result = subprocess.run([mkvmerge_path, '-J', mkv_file], capture_output=True, text=True, check=True, encoding='utf-8')
    info = json.loads(result.stdout)

    # Prepare commands to change track names
    commands = []
    track_updates = []

    for track in info['tracks']:
        if track['type'] == 'audio':
            track_id = track['id']
            language = track['properties'].get('language', '').upper()
            codec = track['codec']
            channels = track['properties'].get('audio_channels', '')
            current_name = track['properties'].get('track_name', '')

            # Debug: Print track information
            print(f"Track ID: {track_id}, Language: {language}, Codec: {codec}, Channels: {channels}, Current Name: {current_name}")

                        # If language is 'UND', set it to 'FRE'
            if language == 'UND':
                commands.extend(['--edit', f'track:a{track_id}', '--set', 'language=jpn'])
                language = 'JPN'  # Update language variable for naming purposes
                
            # Determine new track name based on language, codec, and channels
            language_map = {
                'JPN': 'JP',
                'FRE': 'FR',
                'ENG': 'EN',
                'CHI': 'CN'
            }
            lang_short = language_map.get(language, language)  # Use mapped abbreviation or original if missing
            codec_map = {
                'A_AAC': 'AAC',
                'A_FLAC': 'FLAC',
                'A_AC3': 'AC3',
                'A_EAC3': 'EAC3',
                'A_DTS': 'DTS',
                'A_TRUEHD': 'TrueHD',
                'A_MPEG/L3': 'MP3',        # Common MP3 codec
                'A_VORBIS': 'Vorbis',      # Vorbis codec
                'A_OPUS': 'Opus',          # Opus codec
                'A_PCM/INT/LIT': 'PCM',    # PCM codec
                'A_PCM/FLOAT/IEEE': 'PCM', # Floating-point PCM codec
                'A_MS/ACM': 'MS Audio',    # Microsoft Audio codec, commonly WMA
                'A_MLP': 'MLP',            # Meridian Lossless Packing
                'A_ALAC': 'ALAC'           # Apple Lossless Audio Codec
            }
            codec_short = codec_map.get(codec, codec)  # Use mapped codec or original if missing

            # Map channel counts to typical layouts
            channel_layouts = {
                1: "1.0",
                2: "2.0",
                6: "5.1",
                8: "7.1"
            }
            # Determine channel layout
            channel_layout = channel_layouts.get(channels, f"{channels}.1" if channels and int(channels) > 2 else f"{channels}.0")
            
            # Format the new track name
            new_name = f"{lang_short} {codec_short} {channel_layout}"

            # Append update command for mkvpropedit if necessary
            if new_name and current_name != new_name:
                commands.extend(['--edit', f'track:a{track_id}', '--set', f'name={new_name}'])
                track_updates.append((current_name, new_name))
                print(f"Scheduled update: {current_name} -> {new_name}")

    if commands:
        # Execute the mkvpropedit command
        try:
            subprocess.run([mkvpropedit_path, mkv_file] + commands, check=True)
            print(f"Updated track names for {os.path.basename(mkv_file)}: {track_updates}")
        except subprocess.CalledProcessError as e:
            print(f"Error during mkvpropedit execution: {e.stderr}")
    else:
        print(f"No updates necessary for {os.path.basename(mkv_file)}")

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
        change_audio_track_names_by_language(mkv_file_path)

if __name__ == "__main__":
    mkv_folder = select_mkv_folder()
    if mkv_folder:
        process_all_mkv_files_in_directory(mkv_folder)
    else:
        print("No folder selected.")
