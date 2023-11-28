import tkinter as tk
import os
import glob
from tkinter import messagebox


class NameInputWindow:
    def __init__(self, root, user_name, config_name, window_type, callback):
        self.root = root
        self.name = user_name
        self.config_name = config_name
        self.window_type = window_type
        self.callback = callback

        # Create a new window for name input
        self.name_dialog = tk.Toplevel(self.root)
        self.name_dialog.title("Name Input")
        self.name_dialog.geometry("500x300")

        # Create a label and entry field for the name
        self.name_label = tk.Label(self.name_dialog, text="Please input your name")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.name_dialog)
        self.name_entry.insert(0, self.name)  # Insert the name into the entry field
        self.name_entry.pack()

        # Create labels for config_name and window_type
        self.config_label = tk.Label(
            self.name_dialog, text=f"Config Name: {self.config_name}"
        )
        self.config_label.pack()
        self.window_label = tk.Label(
            self.name_dialog, text=f"Window Type: {self.window_type}"
        )
        self.window_label.pack()

        # Create a submit button
        self.submit_button = tk.Button(
            self.name_dialog, text="Submit", command=self.submit_name
        )
        self.submit_button.pack()

    def submit_name(self):
        # Get the name from the entry field
        self.name = self.name_entry.get().strip()  # Remove leading/trailing whitespace

        # Check if the name is empty
        if not self.name:
            messagebox.showerror("Error", "Please enter a name.")
            return

        # Check if the directory exists
        directory_name = f"user_evaluation_output/{self.window_type}/{self.name}*"
        if glob.glob(directory_name):
            messagebox.showerror(
                "Error",
                "A directory starting with this name already exists in this window type. Please enter a different name.",
            )
            return

        # Destroy the name input window
        self.name_dialog.destroy()

        # Call the callback function with the name
        self.callback(self.name)
