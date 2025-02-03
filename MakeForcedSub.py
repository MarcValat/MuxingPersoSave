"""
Deletes every line containing Default to create a forced subtitle using the original one
"""
import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select folder containing .ass files")
    return folder_path

def process_ass_file(file_path):
    # Regex pattern to identify lines that have a "Default" style
    # This will match any style that contains "Default" in its name
    unwanted_styles_pattern = re.compile(r'Dialogue:.*,Default|Dialogue:.*,Italique|Dialogue:.*,TiretsItalique|Dialogue:.*,TiretsDefault')

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            # If the line does not match the "Default" style, keep it
            if not unwanted_styles_pattern.search(line):
                f.write(line)

def process_folder(folder_path):
    if not folder_path:
        messagebox.showerror("Error", "No folder selected.")
        return

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".ass"):
            file_path = os.path.join(folder_path, filename)
            process_ass_file(file_path)
    
    messagebox.showinfo("Success", "All .ass files have been processed.")

if __name__ == "__main__":
    folder_path = select_folder()
    process_folder(folder_path)
