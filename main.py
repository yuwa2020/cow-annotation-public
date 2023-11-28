# Standard Library Imports
import os
import csv
import argparse
import subprocess

# Third-Party Imports
import tkinter as tk
import importlib
from PIL import Image, ImageTk, ImageDraw

# Local Imports
from time_tracker import TimeTracker
from annotations_loader import AnnotationsLoader
from video_player import VideoPlayer
from multi_view_window import MultiViewWindow
from top_k_view_window import TopkViewWindow
from application_state import ApplicationState
from cheat_mode import CheatMode
from name_input_window import NameInputWindow


def get_config(type):
    if type == 10:
        type = "catalog"
        module = importlib.import_module(f"config_{type}")
        return module.Config, 10
    elif type == 20:
        type = "demo"
        module = importlib.import_module(f"config_{type}")
        return module.Config, 20
    else:
        module = importlib.import_module(f"config_type{type}")
        return module.Config, int(type)


class CowApp:
    def __init__(self, root, args):
        # Local imports
        self.user_number = args.user_number
        if args.user_number == -1:
            self.user_name = ""
            self.config, self.config_number = get_config(args.config_type)
            self.window_type = args.window_type

        elif args.section == 0:
            # Demo mode
            user_configurations = self.read_csv(
                "Catalog/answer/Sheet-1-user_evaluation_window_and_config_number.csv"
            )[args.user_number]
            self.user_name = user_configurations["Name"]
            self.window_type = int(user_configurations[f"Section1-Window"])
            if self.window_type == 1:
                self.window_type = int(user_configurations[f"Section2-Window"])
            self.config_number = 20
            self.config, self.config_number = get_config(self.config_number)

        else:
            self.section = args.section
            user_configurations = self.read_csv(
                "Catalog/answer/Sheet-1-user_evaluation_window_and_config_number.csv"
            )[args.user_number]
            self.user_name = user_configurations["Name"]
            self.config_number = int(
                user_configurations[f"Section{self.section}-Config"]
            )
            self.window_type = int(user_configurations[f"Section{self.section}-Window"])
            self.config, self.config_number = get_config(self.config_number)

            print("config", self.config_number)
            print("Window type is", self.window_type)

        self.root = root
        self.root.withdraw()
        self.time_tracker = TimeTracker()
        self.app_state = ApplicationState(self.config)
        self.evalation_mode = False

        # Use the argument
        if args.evaluation_mode:
            print("Evaluation mode is on")
            self.app_state.change_evaluation_mode()
        else:
            # The evaluation mode is off
            pass

        # Load annotations
        annotations_loader = AnnotationsLoader()
        (
            self.annotations,
            self.individual_cow_annotations,
            self.nearest_bbox_per_cow,
        ) = annotations_loader.load_annotations(self.config.ANNOTATION_FILE)
        self.individual_identification_annotations = (
            annotations_loader.load_individual_identification_annotations(
                self.config.IDENTIFICATION_FILE
            )
        )
        self.name_input_window = NameInputWindow(
            root,
            self.user_name,
            self.config_number,
            self.window_type,
            self.start_main_app,
        )

    @staticmethod
    def read_csv(filename):
        user_config = {}
        with open(filename, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                if row[0]:  # Check if the first cell is not empty
                    user_config[int(row[0])] = {
                        "Name": row[1],
                        "Section1-Config": row[2],
                        "Section2-Config": row[3],
                        "Section1-Window": row[4],
                        "Section2-Window": row[5],
                    }
        return user_config

    def start_main_app(self, name):
        self.root.deiconify()
        self.root.title("Annotation Tool")
        print(self.name_input_window.name)

        # Now print the current window size
        print("Width:", root.winfo_width())
        print("Height:", root.winfo_height())

        ###multi-view window and video(Left)###
        self.left_canvas = tk.Canvas(root)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH)

        self.multi_view_window = MultiViewWindow(
            self.config,
            self.window_type,
            self.left_canvas,
            self.nearest_bbox_per_cow,
            self.show_all_windows,
            self.app_state,
            self.time_tracker,
            self.main_change_change_image_by_frame,
        )

        self.video_player = VideoPlayer(
            root,
            self.config,
            self.left_canvas,
            self.annotations,
            self.individual_cow_annotations,
            self.nearest_bbox_per_cow,
            self.show_all_windows,
            self.save_all_histories_and_ids,
            self.app_state,
            self.time_tracker,
        )

        right_canvas = tk.Canvas(root)
        right_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.top_k_view_window = TopkViewWindow(
            self.config,
            self.window_type,
            right_canvas,
            self.individual_identification_annotations,
            self.show_all_windows,
            self.finish_evaluation,
            self.app_state,
            self.time_tracker,
            self.hide_bounding_box,
        )
        if self.app_state.get_evaluation_mode() != True:
            self.cheat_mode = CheatMode(
                right_canvas,
                self.show_all_windows,
                self.app_state,
                self.time_tracker,
            )

        # Create a start button
        self.start_button = tk.Button(
            self.left_canvas,
            text="Start Evaluation",
            command=self.start_action,
            height=3,
            width=20,
            font=("Helvetica", 20),  # Change the font type and size
            bg="#4CAF50",  # Change the background color to green
        )
        self.start_button.pack()

        self.root.bind("<KeyPress>", self.key_pressed)
        # Load the first image

        self.time_tracker.start_or_resume_timer(0)

    ###keyboard Shortcuts###
    def key_pressed(self, event, *args):
        if event.keysym == "space":
            self.time_tracker.record_key_press(event.keysym)
            self.video_player.toggle_video()
        elif event.keysym == "Right":
            self.time_tracker.record_key_press(event.keysym)
            self.video_player.change_image_10("next")
        elif event.keysym == "Left":
            self.time_tracker.record_key_press(event.keysym)
            self.video_player.change_image_10("previous")
        elif event.keysym == "period":
            self.time_tracker.record_key_press(event.keysym)
            self.video_player.change_image("next")
        elif event.keysym == "comma":
            self.time_tracker.record_key_press(event.keysym)
            self.video_player.change_image("previous")
        elif event.keysym == "Escape":
            self.time_tracker.record_key_press(event.keysym)
            self.multi_view_window.deselect_cow()
        elif (
            event.keysym == "Return"
        ) and self.app_state.get_evaluation_mode() == False:
            self.cheat_mode.cheat_mode_show()

    def hide_bounding_box(self):
        # Hide bounding box
        display_bounding_boxes = self.app_state.get_display_bounding_boxes()
        if display_bounding_boxes:
            self.app_state.change_display_bounding_boxes()
            self.time_tracker.record_button_press("hide bounding box")
            self.show_all_windows()
        else:
            self.app_state.change_display_bounding_boxes()
            self.show_all_windows()

    def main_change_change_image_by_frame(self, frame):
        # This state can be change afterwards
        self.video_player.change_image_by_frame(frame)

    def show_all_windows(self):
        selected_cow = self.app_state.get_selected_cow()
        print("selected cow is", selected_cow)

        if selected_cow:
            self.video_player.load_and_draw_cow_image()
        else:
            self.video_player.load_image()

        self.multi_view_window.show_selected_cow()
        if self.window_type == 3:
            self.multi_view_window.show_multi_view_window()
        if self.window_type == 2 or self.window_type == 3:
            self.top_k_view_window.show_top_10_cows()

    def start_action(self):
        self.start_button.pack_forget()
        self.time_tracker.start_total_timer()
        self.video_player.load_image()
        self.evalation_mode = True
        self.start_evaluation()
        evaluation_window = tk.Frame(self.left_canvas)
        evaluation_window.pack(side=tk.TOP)
        save_history_button = tk.Button(
            self.left_canvas,
            text="Finish Test",
            command=self.save_all_histories_and_ids,
        )
        save_history_button.pack(side=tk.BOTTOM, padx=10)

    def start_evaluation(self):
        messagebox_label = tk.Label(
            self.left_canvas,
            text="Evaluation has started",
            font=("Helvetica", 50, "bold"),
            fg="white",
            bg="#008000",  # Set the background color to green
        )
        messagebox_label.place(relx=0.5, rely=0.5, anchor="center")
        self.left_canvas.after(4000, messagebox_label.place_forget)

    def finish_evaluation(self):
        if self.section == 1:
            messagebox_label = tk.Label(
                self.left_canvas,
                text=f"End of evaluation for Section {self.section}. This section is finished.",
                font=("Helvetica", 40, "bold"),
                fg="white",
                bg="#0000ff",  # Set the background color to blue
            )
        elif self.section == 2:
            messagebox_label = tk.Label(
                self.left_canvas,
                text=f"End of evaluation for Section {self.section}. Thank you for your cooperation.",
                font=("Helvetica", 35, "bold"),
                fg="white",
                bg="#0000ff",  # Set the background color to blue
            )
        messagebox_label.place(relx=0.5, rely=0.5, anchor="center")
        self.save_all_histories_and_ids()
        self.left_canvas.after(7000, messagebox_label.pack_forget)

    def save_all_histories_and_ids(self):
        self.time_tracker.stop_timer(0)
        button_history, cow_annnotation_times = self.time_tracker.get_all_history()

        window_type = int(self.window_type)
        if self.config_number != 20:
            # Create a directory with the name
            directory_name = f"user_evaluation_output/{window_type}"
        else:
            # Demo mode
            directory_name = f"user_evaluation_output/demo/{window_type}"

        os.makedirs(directory_name, exist_ok=True)

        with open(
            os.path.join(
                directory_name,
                f"{self.name_input_window.name}-{self.config_number}-history.csv",
            ),
            "w",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Button", "Discription", "Time"])
            for event in button_history:
                writer.writerow(
                    [event[0], event[1], event[2], event[3]]
                )  # Access elements of the tuple by index

        with open(
            os.path.join(
                directory_name,
                f"{self.name_input_window.name}-{self.config_number}-combined_data.csv",
            ),
            "w",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "query_video_cow_tags",
                    "database_video_cow_IDs",
                    "query_video_cow_tags(for confirmation)",
                    "time",
                ]
            )

            saved_cows = self.app_state.get_saved_cows()
            cow_annnotation_times = self.time_tracker.get_all_cow_times()
            for i in range(len(saved_cows)):
                writer.writerow(
                    [
                        saved_cows[i][0],
                        saved_cows[i][1],
                        cow_annnotation_times[i][0],
                        cow_annnotation_times[i][1],
                    ]
                )

        # after finishing the task, run the script
        if self.section == 2:
            subprocess.run(
                [
                    "python",
                    "user_evaluation_answer/calculate_answer_accuracy.py",
                    "--user_number",
                    str(self.user_number),
                ]
            )


if __name__ == "__main__":
    # Create a parser
    parser = argparse.ArgumentParser(description="Turn on or off the evaluation mode.")

    # Add arguments
    parser.add_argument(
        "--eval",
        dest="evaluation_mode",
        action="store_true",
        help="Turn on the evaluation mode",
    )
    parser.add_argument(
        "--user_number",
        dest="user_number",
        type=int,
        default=-1,
        help="Enter the user number",
    )
    parser.add_argument(
        "--section",
        dest="section",
        type=int,
        default=1,
        help="Enter the section number",
    )

    parser.add_argument(
        "--config",
        dest="config_type",
        type=int,
        default=1,
        help="Select the configuration type",
    )

    # Add the window type argument
    parser.add_argument(
        "--window",
        dest="window_type",
        type=int,
        default=3,
        help="Select the window type",
    )

    # Parse arguments
    args = parser.parse_args()

    # Initialize the Tkinter window
    root = tk.Tk()
    # root.geometry("1680x1000")  # Set the dimensions of the window
    root.geometry("1680x1025")

    # Initialize the CowApp class and create the application
    app = CowApp(root, args)

    # Start the Tkinter event loop to run the application
    root.mainloop()
