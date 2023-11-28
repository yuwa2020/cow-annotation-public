import os
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
from PIL.Image import Resampling
import numpy as np


class TopkViewWindow:
    def __init__(
        self,
        config,
        window_type,
        right_canvas,
        individual_identification_annotations,
        show_all_windows,
        finish_evaluation,
        app_state,
        time_tracker,
        hide_bounding_box,
    ):
        # Local imports
        self.config = config
        self.window_type = window_type

        self.individual_identification_annotations = (
            individual_identification_annotations
        )
        self.hide_bounding_box = hide_bounding_box
        self.show_all_windows = show_all_windows
        self.finish_evaluation = finish_evaluation
        self.cow_labels = {}
        self.top_10_matched_cows_info = {}
        self.grid_frame_topk = None  # Initialize this with your grid frame
        self.selected_topk_cow = None

        self.app_state = app_state
        self.time_tracker = time_tracker

        self.setup_top_k_window(self.config.DATABASE_IMAGE_DIR, right_canvas)

    def setup_top_k_window(self, database_image_dir, right_canvas):
        ###Top-k Display Window (Right)###
        self.database_image_files = self.get_sorted_image_files(database_image_dir)

        self.canvas = tk.Canvas(right_canvas)
        self.canvas.pack()

        self.bottom_right_canvas = tk.Frame(right_canvas)
        self.bottom_right_canvas.pack(side=tk.BOTTOM)

        customFont = tkFont.Font(size=20)

        if self.window_type == 2 or self.window_type == 3:
            previous_page_button = tk.Button(
                self.bottom_right_canvas,
                text="Previous",
                font=customFont,
                command=lambda: self.navigate_top10_cow("Previous"),
            )
            previous_page_button.grid(row=0, column=0, ipadx=10, ipady=10)

            next_page_button = tk.Button(
                self.bottom_right_canvas,
                text="Next",
                font=customFont,
                command=lambda: self.navigate_top10_cow("Next"),
            )
            next_page_button.grid(row=0, column=2, ipadx=10, ipady=10)

            self.top10_cow_number_photo = tk.Label(
                self.bottom_right_canvas, text="0/0", font=customFont
            )
            self.top10_cow_number_photo.grid(row=0, column=1, ipadx=10, ipady=10)

        self.text_selected_cow = tk.Label(
            self.bottom_right_canvas, text="Cow #0", font=customFont
        )
        self.text_selected_cow.grid(row=1, column=0, ipadx=10, ipady=10)

        confirm_button = tk.Button(
            self.bottom_right_canvas,
            text="Confirm ID",
            font=customFont,
            command=self.confirm_id,
        )
        confirm_button.grid(row=1, column=1, ipadx=10, ipady=10)

        # Vertical Scrollbar widget and associate it with the canvas
        scrollbar = tk.Scrollbar(
            right_canvas, orient="vertical", command=self.canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Re-pack the canvas that appears to the left of the scrollbar
        self.canvas.pack_forget()
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # self.grid_frame_topk frame inside the canvas
        self.grid_frame_topk = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.grid_frame_topk, anchor="nw"
        )

        # Update the scroll region of the canvas
        self.grid_frame_topk.bind("<Configure>", self.on_frame_configure)

        if self.window_type == 2 or self.window_type == 3:
            customFont = tkFont.Font(family="Helvetica", size=20, weight="bold")
            topk_label = tk.Label(
                self.grid_frame_topk, text="Top-K Matched Cows", font=customFont
            )
            topk_label.grid(row=0, columnspan=4)

        hide_bounding_box_button = tk.Button(
            self.grid_frame_topk,
            text="Hide Bounding Box",
            command=self.hide_bounding_box,
        )
        hide_bounding_box_button.grid(row=7, column=1, ipadx=10, ipady=10)

        # Manual input cow ID
        self.input_value = tk.StringVar()
        self.input_value.trace("w", self.check_input)

        manual_input_label = tk.Label(
            self.grid_frame_topk, text="Manual Input Cow #", font=customFont
        )
        manual_input_label.grid(row=8, column=0)

        id_input_field = tk.Entry(
            self.grid_frame_topk,
            textvariable=self.input_value,
            highlightthickness=0,
            bd=0,
            highlightbackground="#FFFFFF",
            highlightcolor="#FFFFFF",
            width=2,
        )
        id_input_field.grid(row=8, column=1, ipadx=10, ipady=10)

        self.cow_labels = {}  # To store Label and PhotoImage objects for each cow

        if self.window_type == 2 or self.window_type == 3:
            self.initialize_top10_image()

    ###top-k window###
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
        if tool_number == 2:
            boundaries = 10
            line_width = 3
            x1 = x
            y1 = y
            x2 = x + w
            y2 = y + h
            img_path = self.database_image_files[frame_number]

        img = Image.open(img_path)
        img_width, img_height = img.size

        # Add a margin, checking that we don't go out of image boundaries
        x1 = max(0, x1 - boundaries)
        y1 = max(0, y1 - boundaries)
        x2 = min(img_width, x2 + boundaries)
        y2 = min(img_height, y2 + boundaries)

        # Crop the image
        cropped_img = img.crop((x1, y1, x2, y2))

        # Draw the bounding box on the cropped image in red
        draw = ImageDraw.Draw(cropped_img, "RGBA")
        if tool_number == 0 or self.app_state.display_bounding_boxes:
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

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    ###Top-k Display Window###
    def initialize_top10_image(self):
        """
        Generate a initial top 10 image.

        Parameters:
        None

        Returns:
        None
        """
        for i in range(1, 11):
            row = (i - 1) // 2 + 1  # Calculate grid row, starting from 1
            col = (i - 1) % 2  # Calculate grid column
            image_path = f"{self.config.TOP10_IMAGE_DIR_DEFAULT}/cow_1.jpg"

            # Open and resize the image
            image = Image.open(image_path)
            photo = self.resize_and_center(
                image, self.config.TOP10_FRAME_WIDTH, self.config.TOP10_FRAME_HEIGHT
            )
            # Create a label with the image and the cow's score
            topk_label = tk.Label(
                self.grid_frame_topk,
                image=photo,
                text=f"Cow #0 distance: 0.00",
                compound="top",
                bg="#ECD9D9",
                fg="black",
                width=self.config.TOP10_FRAME_WIDTH + 5,
                height=self.config.TOP10_FRAME_HEIGHT + 20,
                borderwidth=4.1,
                relief="raised",
            )

            # Keep a reference to prevent garbage collection
            topk_label.image = photo

            # Place the label in the grid
            topk_label.grid(row=row, column=col, padx=5, pady=5)

            # Store the label and photo for the cow in the dictionary
            self.cow_labels[i] = {"label": topk_label, "photo": photo}

            # Bind the click event on the label to the on_cow_select function
            topk_label.bind(
                "<Button-1>",
                lambda event, cow=i: self.on_cow_select(event, cow),
            )

    def Update_the_label_and_photo_for_top10_image(
        self,
        Top_10_grid_rank,
        new_photo,
        cow_id=0,
        distance=0,
        background_color="#ECD9D9",
        relief="raised",
        cow_rank=0,
    ):
        """
        Update the label and photo for top 10 image.

        Parameters:
        - Top_10_grid_rank: int, the ranking of the cow
        - new_photo: PIL Image object, the new photo
        - cow_id: int, the id of the cow
        - distance: float, the distance of the cow

        Returns:
        None
        """
        selected_cow = self.app_state.get_selected_cow()
        if selected_cow and cow_id > 0 and distance > 0:
            text = f"rank {cow_rank} Cow #{cow_id} distance: {distance}"
            bg = background_color
        else:
            text = f"Cow #0 distance: 0.00"
            bg = "#ECD9D9"

        self.cow_labels[Top_10_grid_rank]["label"].config(
            image=new_photo,
            text=text,
            compound="top",
            bg=bg,
            fg="black",
            width=self.config.TOP10_FRAME_WIDTH + 5,
            height=self.config.TOP10_FRAME_HEIGHT + 20,
            borderwidth=4.1,
            relief=relief,
        )
        self.cow_labels[Top_10_grid_rank]["label"].image = new_photo
        self.cow_labels[Top_10_grid_rank]["photo"] = new_photo

    def on_cow_select(self, event, top10_rank):
        if (
            self.app_state.get_selected_cow() != None
            and self.app_state.get_selected_cow_exist()
        ):
            # click event
            self.selected_topk_cow_rank = top10_rank
            top_10_cows_image_page = self.app_state.get_top_10_cows_image_page()
            cow_rank = top10_rank + 10 * (top_10_cows_image_page - 1)
            (
                self.selected_topk_cow,
                dummy,
                dummy,
                dummy,
                dummy,
                dummy,
                dummy,
            ) = self.top_10_matched_cows_info[cow_rank]

            self.selected_topk_cow = int(self.selected_topk_cow)
            self.time_tracker.record_button_press(
                "Clicked on database cow #", self.selected_topk_cow
            )

            self.text_selected_cow.config(text=f"Cow #{self.selected_topk_cow}")
            self.top10_cow_number_photo.config(
                text=f"{1}/{int(self.top10_matched_cows_each_image_number[top10_rank])}"
            )

            self.show_top_10_cows()

            # Crop and resize image
            cow_id, distance, frame_number, x, y, w, h = self.top_10_matched_cows_info[
                cow_rank
            ]

            print(cow_id, distance, frame_number, x, y, w, h)
            new_image = self.crop_image(
                int(frame_number), 2, int(x), int(y), int(w), int(h)
            )
            new_photo = self.resize_and_center(
                new_image,
                self.config.TOP10_FRAME_WIDTH,
                self.config.TOP10_FRAME_HEIGHT,
                "#008000",
            )
            cow_rank = top10_rank + 10 * (top_10_cows_image_page - 1)
            self.Update_the_label_and_photo_for_top10_image(
                top10_rank,
                new_photo,
                int(cow_id),
                float(distance),
                "#008000",
                "flat",
                cow_rank,
            )
        else:
            self.time_tracker.record_button_press(
                "Without selecting cow ID, clicked on database cow #", top10_rank
            )

    def find_top10_cows(self):
        Top_10_grid_rank = 1
        current_image_frame = self.app_state.get_current_image_frame()
        target_frame = int(current_image_frame)
        selected_cow = self.app_state.get_selected_cow()
        target_cow_tag = int(selected_cow)
        (
            selected_x,
            selected_y,
            selected_w,
            selected_h,
        ) = self.app_state.get_selected_cow_annotation()
        if target_frame in self.individual_identification_annotations:
            # Initialize the bounding_boxes list for this frame
            for annotation in self.individual_identification_annotations[target_frame]:
                (
                    cow_tag,
                    query_x,
                    query_y,
                    query_w,
                    query_h,
                    cow_id,
                    distance,
                    top_10_frame,
                    x,
                    y,
                    w,
                    h,
                ) = annotation

                if (
                    cow_tag == target_cow_tag
                    and selected_x == query_x
                    and selected_y == query_y
                    and selected_w == query_w
                    and selected_h == query_h
                ):
                    cow_id = int(cow_id)
                    distance = float(distance)
                    distance = round(distance, 2)
                    # Check if the id matches any saved cows
                    saved_cows = self.app_state.get_saved_cows()
                    matching_rows = [row for row in saved_cows if row[1] == cow_id]
                    if len(matching_rows) == 0:
                        self.top_10_matched_cows_info[Top_10_grid_rank] = [
                            int(cow_id),
                            float(distance),
                            int(top_10_frame),
                            int(x),
                            int(y),
                            int(w),
                            int(h),
                        ]
                        Top_10_grid_rank += 1

    def show_top_10_cows(self):
        self.top_10_matched_cows_before_crop_image = {}
        self.top_10_matched_cows_info = np.zeros(
            (100, 7)
        )  # cow_id, distance, frame_number, x, y, w, h
        self.top10_matched_cows_each_image_number = np.zeros((11, 1))
        top_10_cows_image_page = self.app_state.get_top_10_cows_image_page()
        self.top10_cow_number_photo.config(text=f"{top_10_cows_image_page}/3")

        selected_cow = self.app_state.get_selected_cow()
        if selected_cow and self.app_state.get_selected_cow_exist():
            # Find the top 10 matched cows
            self.find_top10_cows()
        else:
            self.text_selected_cow.config(text=f"Cow #0")

        for Top_10_grid_rank in range(1, 11):
            cow_rank = Top_10_grid_rank + 10 * (top_10_cows_image_page - 1)
            cow_id, distance, frame_number, x, y, w, h = self.top_10_matched_cows_info[
                cow_rank
            ]
            if selected_cow and self.app_state.get_selected_cow_exist():
                # Crop and resize image
                new_image = self.crop_image(
                    int(frame_number), 2, int(x), int(y), int(w), int(h)
                )
                new_photo = self.resize_and_center(
                    new_image,
                    self.config.TOP10_FRAME_WIDTH,
                    self.config.TOP10_FRAME_HEIGHT,
                )

                self.top_10_matched_cows_before_crop_image[Top_10_grid_rank] = new_image

                self.Update_the_label_and_photo_for_top10_image(
                    Top_10_grid_rank,
                    new_photo,
                    int(cow_id),
                    float(distance),
                    "#ECD9D9",
                    "raised",
                    cow_rank,
                )
            else:
                # Show Default image
                image_path = f"{self.config.TOP10_IMAGE_DIR_DEFAULT}/cow_0.jpg"

                # Open and resize the image
                image = Image.open(image_path)
                new_photo = self.resize_and_center(
                    image, self.config.TOP10_FRAME_WIDTH, self.config.TOP10_FRAME_HEIGHT
                )
                self.Update_the_label_and_photo_for_top10_image(
                    Top_10_grid_rank, new_photo
                )

    def navigate_top10_cow(self, direction):
        top_10_cows_image_page = self.app_state.get_top_10_cows_image_page()

        if self.app_state.get_selected_cow() != None:
            if direction == "Next":
                self.time_tracker.record_button_press(
                    "Clicked on Top 10 Next button, current page",
                    top_10_cows_image_page,
                )
                if top_10_cows_image_page == 3:
                    self.app_state.set_top_10_cows_image_page(1)
                else:
                    self.app_state.add_top_10_cows_image_page()
            elif direction == "Previous":
                self.time_tracker.record_button_press(
                    "Clicked on Top 10 Previous button, current page:",
                    top_10_cows_image_page,
                )
                if top_10_cows_image_page == 1:
                    self.app_state.set_top_10_cows_image_page(3)
                else:
                    self.app_state.subtract_top_10_cows_image_page()

            top_10_cows_image_page = self.app_state.get_top_10_cows_image_page()
            self.top10_cow_number_photo.config(text=f"{top_10_cows_image_page}/3")

            for Top_10_grid_rank in range(1, 11):
                cow_rank = Top_10_grid_rank + 10 * (top_10_cows_image_page - 1)
                (
                    cow_id,
                    distance,
                    frame_number,
                    x,
                    y,
                    w,
                    h,
                ) = self.top_10_matched_cows_info[cow_rank]
                if cow_id != 0:
                    # Crop and resize image
                    new_image = self.crop_image(
                        int(frame_number), 2, int(x), int(y), int(w), int(h)
                    )
                    new_photo = self.resize_and_center(
                        new_image,
                        self.config.TOP10_FRAME_WIDTH,
                        self.config.TOP10_FRAME_HEIGHT,
                    )

                    self.top_10_matched_cows_before_crop_image[
                        Top_10_grid_rank
                    ] = new_image

                    self.Update_the_label_and_photo_for_top10_image(
                        Top_10_grid_rank,
                        new_photo,
                        int(cow_id),
                        float(distance),
                        "#ECD9D9",
                        "raised",
                        cow_rank,
                    )
                else:
                    # Show Default image
                    image_path = f"{self.config.TOP10_IMAGE_DIR_DEFAULT}/cow_0.jpg"

                    # Open and resize the image
                    image = Image.open(image_path)
                    new_photo = self.resize_and_center(
                        image,
                        self.config.TOP10_FRAME_WIDTH,
                        self.config.TOP10_FRAME_HEIGHT,
                    )
                    self.Update_the_label_and_photo_for_top10_image(
                        Top_10_grid_rank, new_photo
                    )
        else:
            self.time_tracker.record_button_press(
                "Without selecting cow ID, Clicked on", direction
            )

    def confirm_id(self):
        # Confirm the selected cow ID
        selected_cow = self.app_state.get_selected_cow()
        saved_cows = self.app_state.get_saved_cows()
        print(saved_cows)

        if selected_cow and any(cow == self.selected_topk_cow for _, cow in saved_cows):
            self.time_tracker.record_button_press(
                "The selected cow ID has been confirmed before"
            )
            messagebox_label = tk.Label(
                self.bottom_right_canvas,
                text=f"Error: Cow ID #{self.selected_topk_cow} has been confirmed before",
                font=("Helvetica", 20, "bold"),
                fg="white",
                bg="#ff0000",  # Set the background color to red
            )

        elif (
            selected_cow
            and self.selected_topk_cow
            and self.app_state.get_selected_cow_exist()
        ):
            # Create a label widget to display the confirmation message
            self.time_tracker.record_button_press(
                "Confirmed database cow #", self.selected_topk_cow
            )
            messagebox_label = tk.Label(
                self.bottom_right_canvas,
                text=f"Cow ID #{self.selected_topk_cow} confirmed",
                font=("Arial", 30),
                fg="#ffffff",  # Set the foreground color to white
                bg="#008000",  # Set the background color to green
                borderwidth=2,  # Add a border around the label
                relief="groove",  # Set the border style to "groove"
            )

            # Save the selected cow ID
            self.app_state.add_saved_cows(selected_cow, self.selected_topk_cow)
            self.time_tracker.stop_timer(selected_cow)

            self.app_state.reset_selected_cow()
            self.selected_topk_cow = None
            self.text_selected_cow.config(text=f"Cow #0")
            self.app_state.set_top_10_cows_image_page(1)
            self.show_all_windows()

            # Evaluation Mode Check
            eval_cow = self.app_state.get_eval_cow()
            saved_cows = self.app_state.get_saved_cows()
            saved_cows_first_column = [cow[0] for cow in saved_cows]

            eval_cow_set = set(eval_cow)
            saved_cows_row_set = set(saved_cows_first_column)

            # compare
            are_equal = eval_cow_set == saved_cows_row_set

            if self.app_state.get_evaluation_mode() and are_equal:
                self.finish_evaluation()

        else:
            self.time_tracker.record_button_press(
                "Clicked confirm without selecting cow ID"
            )
            messagebox_label = tk.Label(
                self.bottom_right_canvas,
                text=f"Error: No cow ID selected",
                font=("Helvetica", 30, "bold"),
                fg="white",
                bg="#ff0000",  # Set the background color to red
            )

        messagebox_label.grid(
            row=0, column=0, columnspan=3, rowspan=2, ipadx=25, ipady=25
        )

        # Schedule the label widget to be removed from the grid after 3 seconds
        self.bottom_right_canvas.after(3000, lambda: messagebox_label.grid_remove())

    def check_input(self, *args):
        value = self.input_value.get()
        if not value:
            print("Input field is empty")
            self.text_selected_cow.config(text=f"Cow #0")
            self.selected_topk_cow = None
        else:
            print(f"Input value is: {value}")
            if 1 <= int(value) <= 67:
                self.text_selected_cow.config(text=f"Cow #{value}")
                self.selected_topk_cow = int(value)
