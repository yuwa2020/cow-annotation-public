import os
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
from PIL.Image import Resampling
import numpy as np
import random

# Local imports
from time_tracker import TimeTracker


class MultiViewWindow:
    def __init__(
        self,
        config,
        window_type,
        left_canvas,
        nearest_bbox_per_cow,
        show_all_windows,
        app_state,
        time_tracker,
        main_change_change_image_by_frame,
    ):
        # Local imports
        self.config = config
        self.window_type = window_type

        self.nearest_bbox_per_cow = nearest_bbox_per_cow
        self.show_all_windows = show_all_windows
        self.app_state = app_state
        self.main_change_change_image_by_frame = main_change_change_image_by_frame
        self.time_tracker = time_tracker
        self.multi_window_canvas = None
        self.selected_cow_label = {}
        self.multi_window = {}
        self.multi_view_labels = {}

        self.image_files = self.get_sorted_image_files(self.config.IMAGE_DIR)
        self.setup_multi_window(left_canvas)

    def setup_multi_window(self, left_canvas):
        self.multi_window_canvas = tk.Frame(left_canvas)
        self.multi_window_canvas.pack(side=tk.TOP, fill=tk.Y)

        customFont = tkFont.Font(size=24, weight="bold")
        selected_cow_label = tk.Label(
            self.multi_window_canvas, text="Selected Cow", font=customFont, fg="red"
        )
        selected_cow_label.grid(row=0, column=0)

        self.multi_view_labels = {}
        self.selected_cow_label = {}

        self.default_selected_image()

        if self.window_type == 3:
            self.default_multi_view_image()

        customFont = tkFont.Font(size=20)
        confirm_button = tk.Button(
            self.multi_window_canvas,
            text="Deselect Cow",
            font=customFont,
            command=self.deselect_cow,
        )
        confirm_button.grid(row=1, column=1, ipadx=15, ipady=40)

    def draw_rectangle_crop_image(
        self, draw, x1, y1, x2, y2, r, g, b, line_opacity=255, line_width=8
    ):
        """
        Draw a rectangle on the canvas.

        Parameters:
        None

        Returns:
        None
        """
        draw.rectangle(
            [(int(x1), int(y1)), (int(x2), int(y2))],
            outline=(r, g, b, line_opacity),
            width=line_width,
        )

    def crop_image(self, frame_number, tool_number, x=None, y=None, w=None, h=None):
        """
        Crop the image around the selected cow based on its bounding box.

        Parameters:
        - frame_number: int, the frame number for which to crop the image
        - tool_number: int, the tool number (0:selected_cow, 1:multi_view_window)

        Returns:
        - cropped_img: PIL Image object, cropped image
        """

        def find_coordinates_and_image_path():
            x1, y1, x2, y2 = None, None, None, None
            selected_cow = self.app_state.get_selected_cow()
            if frame_number in self.nearest_bbox_per_cow[selected_cow]:
                distance, annotation = self.nearest_bbox_per_cow[selected_cow][
                    frame_number
                ]
                if tool_number == 0:
                    self.app_state.save_selected_cow_annotation(annotation)
                # print("distance: ", distance), print("annotation: ", annotation)
                x, y, w, h = annotation
                x1 = x
                y1 = y
                x2 = x + w
                y2 = y + h
                img_path = self.image_files[frame_number]
                img = Image.open(img_path)
                img_width, img_height = img.size

                # Add a margin, checking that we don't go out of image boundaries
                x1 = max(0, x1 - boundaries)
                y1 = max(0, y1 - boundaries)
                x2 = min(img_width, x2 + boundaries)
                y2 = min(img_height, y2 + boundaries)

                # Crop the image
                cropped_img = img.crop((x1, y1, x2, y2))
                return (x1, y1, x2, y2, cropped_img)
            else:
                x1 = 0
                y1 = 0
                x2 = 0
                y2 = 0
                img_path = self.config.SELECTED_COW_NO_PHOTO
                img = Image.open(img_path)
                return (x1, y1, x2, y2, img)

        if tool_number == 0:
            boundaries = 25
            line_width = 4
            x1, y1, x2, y2, cropped_img = find_coordinates_and_image_path()
            if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
                self.app_state.set_selected_cow_exist(False)
            else:
                self.app_state.set_selected_cow_exist(True)

        elif tool_number == 1:
            boundaries = 10
            line_width = 3
            x1, y1, x2, y2, cropped_img = find_coordinates_and_image_path()

        # Draw the bounding box on the cropped image in red
        draw = ImageDraw.Draw(cropped_img, "RGBA")
        if (tool_number == 0 and x1 != 0) or (
            self.app_state.display_bounding_boxes and x1 != 0
        ):
            self.draw_rectangle_crop_image(
                draw,
                boundaries,
                boundaries,
                x2 - x1 - boundaries,
                y2 - y1 - boundaries,
                255,
                0,
                0,
                170,
                line_width,
            )

        return cropped_img

    def resize_and_center(
        self, image, frame_width, frame_height, background_color="#ECD9D9"
    ):
        """
        Resize and center the image within the given frame dimensions.

        Parameters:
        - image: PIL Image object
        - frame_width: int, the width of the frame
        - frame_height: int, the height of the frame
        - background_color: str, the background color

        Returns:
        - PIL Image object, resized and centered
        """
        image_aspect_ratio = float(image.width / image.height)
        if image.width / frame_width > image.height / frame_height:
            new_width = frame_width
            new_height = int(frame_width / image_aspect_ratio)
        else:
            new_height = frame_height
            new_width = int(frame_height * image_aspect_ratio)
        new_image = image.resize((new_width, new_height), Resampling.LANCZOS)

        background = Image.new("RGB", (frame_width, frame_height), background_color)

        paste_x = (frame_width - new_width) // 2
        paste_y = (frame_height - new_height) // 2
        background.paste(new_image, (paste_x, paste_y))
        return ImageTk.PhotoImage(background)

    ###multi-view window ###
    def get_sorted_image_files(self, directory):
        # Get a list of all image files in the directory
        image_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".jpg")
        ]
        # Sort the images by filename
        image_files = sorted(image_files)
        # Insert a dummy element at the beginning to make the index start from 1
        image_files.insert(0, None)
        return image_files

    def default_selected_image(self):
        # Open and resize the image
        image = Image.open(self.config.SELECTED_COW_DEFAULT)
        photo = self.resize_and_center(
            image,
            self.config.SELECTED_COW_FRAME_WIDTH,
            self.config.SELECTED_COW_FRAME_HEIGHT,
            "#FFE4AF",
        )

        self.label_3 = tk.Label(
            self.multi_window_canvas,
            image=photo,
            compound="top",
            bg="#FFE4AF",
            fg="black",
            width=self.config.SELECTED_COW_FRAME_WIDTH,
            height=self.config.SELECTED_COW_FRAME_HEIGHT,
        )
        self.label_3.image = photo
        self.label_3.grid(row=1, column=0, padx=5, pady=10)
        self.selected_cow_label[0] = {
            "label": self.label_3,
            "photo": photo,
        }

    def default_multi_view_image(self):
        """
        Generate a default multi-view image.

        Parameters:
        - image_path: str, path to the image

        Returns:
        None
        """
        customFont = tkFont.Font(size=24, weight="bold")
        multi_view_label = tk.Label(
            self.multi_window_canvas, text="Multi-View Images", font=customFont
        )
        multi_view_label.grid(row=0, column=3)

        for j in range(1, 4):
            # Open and resize the image
            image = Image.open(self.config.MULTI_WINDOW_DEFAULT)
            photo = self.resize_and_center(
                image,
                self.config.MULTI_WINDOW_FRAME_WIDTH,
                self.config.MULTI_WINDOW_FRAME_HEIGHT,
                "#97C8F5",
            )

            self.label_2 = tk.Label(
                self.multi_window_canvas,
                image=photo,
                text=f"",
                compound="top",
                bg="#97C8F5",
                fg="black",
                width=self.config.MULTI_WINDOW_FRAME_WIDTH,
                height=self.config.MULTI_WINDOW_FRAME_HEIGHT + 15,
                borderwidth=4.1,
                relief="flat",
            )
            self.label_2.image = photo
            self.label_2.grid(row=1, column=j + 1, padx=5, pady=10)
            self.multi_view_labels[j] = {"label": self.label_2, "photo": photo}

            # Bind a function to label click event
            self.label_2.bind(
                "<Button-1>",
                lambda event, cow=j: self.on_multiwindow_select(event, cow),
            )

    def find_multiview_cow(self):
        """
        Find the multi view cow.

        Parameters:
        None

        Returns:
        - multi_view_cows: list, selected_cow_direction: int
        """
        multi_view_cows = []

        x_values = []
        y_values = []
        frames = []

        selected_cow = self.app_state.get_selected_cow()
        if selected_cow != None:
            # Get all possible frames
            all_frames = sorted(self.nearest_bbox_per_cow[selected_cow].keys())

            # Fill in the bounding box data where it exists
            x_values = {}
            y_values = {}

            for frame in all_frames:
                if frame in self.nearest_bbox_per_cow[selected_cow]:
                    bbox = self.nearest_bbox_per_cow[selected_cow][frame][1]
                    x_values[frame] = bbox[0]
                    y_values[frame] = bbox[1]

            # Sort x_values and y_values by frame numbers
            sorted_frames = sorted(x_values.keys())

            # Now calculate the distances
            distances = {
                frame: np.sqrt(
                    (x_values[frame] - x_values[prev_frame]) ** 2
                    + (y_values[frame] - y_values[prev_frame]) ** 2
                )
                for prev_frame, frame in zip(sorted_frames, sorted_frames[1:])
            }

            total_distance = sum(distances.values())

            # Define the number of equally spaced tracklets you want to select
            num_selections = 4

            # Calculate the distance between each selected point
            interval_distance = int(total_distance / (num_selections - 1))

            # Select the points at these intervals
            selected_tracklets = []
            covered_distance = 0
            for frame in sorted(distances.keys()):
                covered_distance += distances.get(frame, 0)
                if covered_distance >= interval_distance * len(selected_tracklets):
                    bbox = self.nearest_bbox_per_cow[selected_cow].get(
                        frame, [None, (0, 0, 0, 0)]
                    )[1]
                    selected_tracklets.append((frame, bbox))

            # Discard the first frame
            selected_tracklets = selected_tracklets[1:]

            # Handle cases where cows are not moving. Sometimes, there may appear to be movement in a frame due to camera location
            if len(selected_tracklets) < 2:
                # Select two random frames
                selected_frames = random.sample(all_frames, 2)

                # Append the selected frames and their bounding boxes to selected_tracklets
                for frame in selected_frames:
                    bbox = self.nearest_bbox_per_cow[selected_cow][frame][1]
                    selected_tracklets.append((frame, bbox))

            print(selected_tracklets)

            return selected_tracklets

    ###multi-view window###
    def deselect_cow(self):
        selected_cow = self.app_state.get_selected_cow()
        self.time_tracker.pause_timer(selected_cow)
        self.time_tracker.record_button_press("Deselect Cow", number=selected_cow)
        self.app_state.reset_selected_cow()
        self.app_state.set_top_10_cows_image_page(1)
        self.show_all_windows()

    def show_selected_cow(self):
        # find image or default image
        selected_cow = self.app_state.get_selected_cow()
        current_image_frame = self.app_state.get_current_image_frame()
        if selected_cow:
            image = self.crop_image(frame_number=current_image_frame, tool_number=0)
        else:
            img = Image.open(self.config.SELECTED_COW_DEFAULT)
            image = img

        selected_and_clear_image_grid = 0
        # Resize and center the image using the helper function
        new_photo = self.resize_and_center(
            image,
            self.config.SELECTED_COW_FRAME_WIDTH,
            self.config.SELECTED_COW_FRAME_HEIGHT,
            "#FFE4AF",
        )

        # Update the label and photo in the dictionary
        self.selected_cow_label[selected_and_clear_image_grid]["label"].config(
            image=new_photo,
            compound="top",
            bg="#FFE4AF",
            width=self.config.SELECTED_COW_FRAME_WIDTH,
            height=self.config.SELECTED_COW_FRAME_HEIGHT,
        )
        self.selected_cow_label[selected_and_clear_image_grid][
            "label"
        ].image = new_photo
        self.selected_cow_label[selected_and_clear_image_grid]["photo"] = new_photo

    def show_multi_view_window(self):
        # Clear any existing frames and find cows to show in multi-view
        view_cow = 0
        selected_tracklets = self.find_multiview_cow()
        selected_cow = self.app_state.get_selected_cow()

        if selected_cow:
            multi_view_cows = [tracklet[0] for tracklet in selected_tracklets]
            # Loop through available views
            selected_cow = self.app_state.get_selected_cow()

        for i in range(1, 4):
            if selected_cow:
                frame = multi_view_cows[i - 1]
                # Store the frame index for the multi-view window
                self.multi_window[i - 1] = frame
                minutes, seconds = divmod(frame, 60)

                # Crop image using function
                new_image = self.crop_image(frame_number=frame, tool_number=1)
                view_cow += 1
            else:
                new_image = Image.open(self.config.MULTI_WINDOW_DEFAULT)

            new_photo = self.resize_and_center(
                new_image,
                self.config.MULTI_WINDOW_FRAME_WIDTH,
                self.config.MULTI_WINDOW_FRAME_HEIGHT,
                "#97C8F5",
            )

            # Update the label and photo in the dictionary
            if selected_cow:
                self.multi_view_labels[i]["label"].config(
                    image=new_photo,
                    text=f"{minutes:02}:{seconds:02}",
                    compound="top",
                    bg="#97C8F5",
                    fg="black",
                    width=self.config.MULTI_WINDOW_FRAME_WIDTH,
                    height=self.config.MULTI_WINDOW_FRAME_HEIGHT + 15,
                    borderwidth=4.1,
                    relief="flat",
                )
            else:
                self.multi_view_labels[i]["label"].config(
                    image=new_photo,
                    text=f"",
                    compound="top",
                    bg="#97C8F5",
                    fg="black",
                    width=self.config.MULTI_WINDOW_FRAME_WIDTH,
                    height=self.config.MULTI_WINDOW_FRAME_HEIGHT + 15,
                    borderwidth=4.1,
                    relief="flat",
                )
            self.multi_view_labels[i]["label"].image = new_photo
            self.multi_view_labels[i]["photo"] = new_photo

    def on_multiwindow_select(self, event, select):
        if self.app_state.get_selected_cow() != None:
            self.time_tracker.record_button_press(
                "Clicked on Mult-View Image", number=select
            )

            multi_view_original = self.app_state.get_multi_view_original()
            current_image_frame = self.app_state.get_current_image_frame()
            if multi_view_original == None:
                self.app_state.set_multi_view_original(current_image_frame)
            self.selected_topk_cow = None
            # click event
            self.main_change_change_image_by_frame(self.multi_window[select - 1])

            # Update the video slider
        else:
            self.time_tracker.record_button_press(
                "Without selecting cow, Clicked on Mult-View Image", number=select
            )
