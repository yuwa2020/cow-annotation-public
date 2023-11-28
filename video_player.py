import os
import tkinter as tk
import tkinter.font as tkFont

from PIL import Image, ImageTk, ImageDraw


class VideoPlayer:
    # Constants for original image dimensions
    ACTUAL_IMAGE_WIDTH, ACTUAL_IMAGE_HEIGHT = 1920, 1080

    def __init__(
        self,
        root,
        config,
        left_canvas,
        annotations,
        individual_cow_annotations,
        nearest_bbox_per_cow,
        show_all_windows,
        save_all_histories_and_ids,
        app_state,
        time_tracker,
    ):
        self.root = root
        # Local import
        self.config = config

        self.annotations = annotations
        self.individual_cow_annotations = individual_cow_annotations
        self.nearest_bbox_per_cow = nearest_bbox_per_cow
        self.show_all_windows = show_all_windows
        self.save_all_histories_and_ids = save_all_histories_and_ids
        self.app_state = app_state
        self.time_tracker = time_tracker
        self.video_timer = None
        self.play_state = False
        self.bounding_boxes = {}
        self.eval_cow = []

        self.image_files = self.get_sorted_image_files(self.config.IMAGE_DIR)
        self.setup_video_player(
            left_canvas, self.config.IMAGE_DIR, self.config.DATABASE_IMAGE_DIR
        )

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

    def setup_video_player(self, left_canvas, image_dir, database_image_dir):
        self.video_canvas = tk.Frame(left_canvas)
        self.video_canvas.pack(side=tk.TOP, fill=tk.BOTH)

        self.app_state.set_current_image_frame(1)  # frame_number_start_with_0

        self.image_label = tk.Label(self.video_canvas)
        self.image_label.bind("<Button-1>", self.on_canvas_click)
        self.image_label.pack(side=tk.TOP)
        self.image_label.focus_set()  # Set focus to the image_label widget

        ##Video controller
        video_controller = tk.Frame(self.video_canvas)
        video_controller.pack(side=tk.TOP, fill=tk.BOTH)

        # Create Canvas (seek bar)
        self.seek_canvas = tk.Canvas(
            video_controller, width=1200, height=20, bg="white"
        )
        self.seek_canvas.pack(side=tk.TOP)

        # Draw seek bar on canvas
        self.seek_canvas.create_rectangle(0, 5, 1200, 20, fill="#858585")

        # Draw slider on canvas
        self.slider = self.seek_canvas.create_rectangle(1, 5, 6, 20, fill="#0F99FD")

        # Event bindings
        self.seek_canvas.bind("<Button-1>", self.handle_slider_click)
        self.seek_canvas.bind("<B1-Motion>", self.handle_slider_click)

        # Play/pause and next frame buttons frame
        controls_frame = tk.Frame(video_controller)
        controls_frame.pack(side=tk.LEFT)  # Added padding

        # Play/pause button canvas
        self.play_canvas = tk.Canvas(
            controls_frame, width=30, height=30, highlightthickness=0
        )
        self.play_canvas.create_polygon(
            5, 5, 5, 25, 25, 15, fill="black"
        )  # initial shape is play
        self.play_canvas.grid(row=0, column=0, padx=3)
        self.play_canvas.bind("<Button-1>", lambda e: self.toggle_video())

        # # Next frame button canvas
        # next_frame_canvas = tk.Canvas(
        #     controls_frame, width=30, height=30, highlightthickness=0
        # )
        # next_frame_canvas.create_line(5, 5, 5, 25, fill="black", width=3)
        # next_frame_canvas.create_polygon(10, 5, 10, 25, 25, 15, fill="black")
        # next_frame_canvas.grid(row=0, column=3, padx=5)
        # next_frame_canvas.bind("<Button-1>", lambda e: self.change_image("next"))

        # Time code label
        customFont = tkFont.Font(family="Open Sans", size=17)
        self.timecode_label = tk.Label(
            video_controller, text="00:01", font=customFont, padx=10
        )
        self.timecode_label.pack(side=tk.LEFT)

    def resize_to_aspect_ratio(self, img, aspect_ratio):
        """
        Resize an image while maintaining a given aspect ratio.

        Parameters:
        - img: PIL Image object
        - aspect_ratio: float, desired aspect ratio (width/height)

        Returns:
        - resized_img: PIL Image object, resized image
        """
        width, height = img.size
        new_height = round(width / aspect_ratio)

        if new_height > height:
            new_width = round(height * aspect_ratio)
            new_height = height
        else:
            new_width = width

        return img.resize((new_width, new_height), Image.ANTIALIAS)

    def play_video(self):
        """
        Play a video and deselect any selected cow.

        Parameters:
        None

        Returns:
        None
        """
        self.change_image("next")
        self.video_timer = self.root.after(1000, self.play_video)

    def pause_video(self):
        """
        Pause the currently playing video.

        Parameters:
        None

        Returns:
        None
        """
        if self.video_timer:
            self.root.after_cancel(self.video_timer)
            self.video_timer = None

    def toggle_video(self):
        """
        Toggle the video between playing and paused states.

        Parameters:
        None

        Returns:
        None
        """
        # Clear the canvas before drawing new shapes
        self.play_canvas.delete("all")

        # If the video is currently playing, pause it
        if self.play_state:
            self.time_tracker.record_button_press(
                "Pause video at", self.app_state.get_current_image_frame()
            )
            self.play_canvas.create_polygon(5, 5, 5, 25, 25, 15, fill="black")
            self.pause_video()
            self.play_state = False
        else:
            self.time_tracker.record_button_press(
                "Play video at", self.app_state.get_current_image_frame()
            )
            # If the video is currently paused, play it
            self.play_canvas.create_rectangle(5, 5, 12, 25, fill="black")
            self.play_canvas.create_rectangle(18, 5, 25, 25, fill="black")
            self.play_video()
            self.play_state = True

    def update_slider(self, x):
        """
        Update the position of the slider based on a given x-coordinate.

        Parameters:
        - x: int, x-coordinate

        Returns:
        None
        """
        self.app_state.set_top_10_cows_image_page(1)
        # Perform boundary checks here (if applicable)
        if x < 1:
            x = 1
        elif x > len(self.image_files) - 1:
            x = len(self.image_files) - 1

        # Calculate new_x to fit within the 1200px seek bar
        new_x = (x / (len(self.image_files) - 2)) * 1200

        self.seek_canvas.coords(self.slider, new_x - 5, 5, new_x + 5, 20)
        self.seek_canvas.tag_raise(self.slider)
        self.app_state.set_current_image_frame(x)

        # Update the time code
        current_image_frame = self.app_state.get_current_image_frame()
        minutes, seconds = divmod(current_image_frame, 60)
        self.timecode_label.config(text=f"{minutes:02}:{seconds:02}")

    def draw_rectangle(
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

    def draw_bounding_boxes(self, img):
        """
        Draw bounding boxes on the image based on the current frame's annotations.

        Parameters:
        - img: PIL Image object

        Returns:
        - img: PIL Image object, image with bounding boxes drawn
        """
        current_image_frame = self.app_state.get_current_image_frame()
        draw = ImageDraw.Draw(img, "RGBA")
        if current_image_frame in self.annotations:
            # Initialize the bounding_boxes list for this frame
            self.bounding_boxes[current_image_frame] = []
            for annotation in self.annotations[current_image_frame]:
                id, x, y, w, h, camera_num = annotation
                evaluation_mode = self.app_state.get_evaluation_mode()
                if evaluation_mode == True:
                    eval_cow = self.app_state.get_eval_cow()
                    if int(id) in eval_cow:
                        # Check if the id matches any saved cows
                        saved_cows = self.app_state.get_saved_cows()
                        matching_rows = [row for row in saved_cows if row[0] == id]
                        if len(matching_rows) > 0:
                            self.draw_rectangle(
                                draw, int(x), int(y), int(x + w), int(y + h), 0, 128, 0
                            )  # mid-range green
                            # Draw the cow's id in yellow
                            id = int(id)
                            text = str(int(matching_rows[0][1]))
                            text_position = (int(x), int(y))
                            draw.text(text_position, text, fill="yellow")
                        else:
                            self.draw_rectangle(
                                draw, int(x), int(y), int(x + w), int(y + h), 255, 0, 0
                            )  # red
                            # Store bounding box coordinates along with id in self.bounding_boxes
                            self.bounding_boxes[current_image_frame].append(
                                (x, y, x + w, y + h, id, camera_num)
                            )

                else:
                    # Check if the id matches any saved cows
                    saved_cows = self.app_state.get_saved_cows()
                    matching_rows = [row for row in saved_cows if row[0] == id]
                    if len(matching_rows) > 0:
                        self.draw_rectangle(
                            draw, int(x), int(y), int(x + w), int(y + h), 0, 128, 0
                        )  # mid-range green
                        # Draw the cow's id in yellow
                        id = int(id)
                        text = str(int(matching_rows[0][1]))
                        text_position = (int(x), int(y))
                        draw.text(text_position, text, fill="yellow")
                    else:
                        self.draw_rectangle(
                            draw, int(x), int(y), int(x + w), int(y + h), 255, 0, 0
                        )  # red
                        # Store bounding box coordinates along with id in self.bounding_boxes
                        self.bounding_boxes[current_image_frame].append(
                            (x, y, x + w, y + h, id, camera_num)
                        )

        return img

    def draw_bounding_boxes_for_selected_cow(self, img):
        """
        Draw the tracks of the selected cow and original frame on the given image.

        Parameters:
        - img: PIL Image object

        Returns:
        - img: PIL Image object with tracks drawn
        """
        current_image_frame = self.app_state.get_current_image_frame()
        draw = ImageDraw.Draw(img, "RGBA")
        selected_cow = self.app_state.get_selected_cow()
        if selected_cow in self.individual_cow_annotations:
            for frame, (
                size,
                bbox,
            ) in self.nearest_bbox_per_cow[selected_cow].items():
                x, y, w, h = bbox
                # Original Cow
                multi_view_original = self.app_state.get_multi_view_original()
                # if frame == multi_view_original:
                #     self.draw_rectangle(
                #         draw, int(x), int(y), int(x + w), int(y + h), 255, 0, 0
                #     )  # red
                if frame == current_image_frame:
                    self.draw_rectangle(
                        draw, int(x), int(y), int(x + w), int(y + h), 255, 0, 0
                    )  # blue
        return img

    def draw_tracks_of_selected_cow(self, img, line_opacity=190):
        """
        Draw the tracks of the selected cow on the given image.

        Parameters:
        - img: PIL Image object

        Returns:
        - img: PIL Image object with tracks drawn
        """
        draw = ImageDraw.Draw(img, "RGBA")
        selected_cow = self.app_state.get_selected_cow()
        if selected_cow in self.individual_cow_annotations:
            middle_points = []  # Initialize the list to hold middle pointså
            # Extract middle points of the largest bounding boxes
            for frame, (
                size,
                bbox,
            ) in self.nearest_bbox_per_cow[selected_cow].items():
                x, y, w, h = bbox
                middle_x = x + w / 2
                middle_y = y + h / 2
                middle_points.append((middle_x, middle_y))

            # Draw lines between middle points to form the track
            for i in range(len(middle_points) - 1):
                draw.line(
                    [middle_points[i], middle_points[i + 1]],
                    fill=(0, 0, 255, line_opacity),
                    width=8,
                )

        return img

    def on_canvas_click(self, event, *args):
        """
        Handle click events on the canvas.

        Parameters:
        - event: tkinter Event object

        Returns:
        None
        """
        print("on canvas click")

        gui_width = self.image_base_width
        gui_height = self.ACTUAL_IMAGE_HEIGHT / (
            self.ACTUAL_IMAGE_WIDTH / self.image_base_width
        )

        # Convert click coordinates to actual image coordinates
        actual_x = (event.x / gui_width) * self.ACTUAL_IMAGE_WIDTH
        actual_y = (event.y / gui_height) * self.ACTUAL_IMAGE_HEIGHT

        x, y = actual_x, actual_y
        current_image_frame = self.app_state.get_current_image_frame()

        selected_cow = self.app_state.get_selected_cow()
        if selected_cow == None:
            # Loop through all bounding boxes in the current frame
            for x1, y1, x2, y2, box_id, camera_num in self.bounding_boxes.get(
                current_image_frame, []
            ):
                if x1 <= x <= x2 and y1 <= y <= y2:
                    box_id = int(box_id)
                    self.time_tracker.record_button_press(
                        "Clicked on query cow ",
                        box_id,
                    )

                    self.app_state.set_selected_cow(int(box_id))
                    selected_cow = self.app_state.get_selected_cow()
                    self.time_tracker.start_or_resume_timer(selected_cow)
                    self.show_all_windows()
                    break
        else:
            # If a cow is already selected, draw tracks and bounding boxes
            if selected_cow in self.individual_cow_annotations:
                for annotation in self.individual_cow_annotations[selected_cow]:
                    frame, x1, y1, w, h, camera_num, transform_dimensions = annotation
                    selected_frame = 0
                    x2 = x1 + w
                    y2 = y1 + h
                    multi_view_original = self.app_state.get_multi_view_original()
                    if frame == multi_view_original:
                        print(f"Select:{frame} ")
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            self.app_state.set_current_image_frame(multi_view_original)

                            self.show_all_windows()
                            self.change_image_by_frame(frame)

                            minutes, seconds = divmod(frame, 60)
                            self.timecode_label.config(
                                text=f"{minutes:02}:{seconds:02}"
                            )

    def load_image(self):
        # Load the image
        current_image_frame = self.app_state.get_current_image_frame()
        img_path = self.image_files[current_image_frame]
        img = Image.open(img_path)
        img = self.draw_bounding_boxes(img)  # draw_annotation_data

        # Resize the image to a maximum width of 600 pixels while maintaining the aspect ratio
        self.image_base_width = 1200
        w_percent = self.image_base_width / float(img.width)
        h_size = int(float(img.height) * float(w_percent))
        img = img.resize((self.image_base_width, h_size), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)

    def load_and_draw_cow_image(self):
        # Load the image
        current_image_frame = self.app_state.get_current_image_frame()
        img_path = self.image_files[current_image_frame]
        img = Image.open(img_path)
        multi_view_original = self.app_state.get_multi_view_original()
        if multi_view_original:
            img = self.draw_tracks_of_selected_cow(img, 128)
        else:
            print("test execute load_and_draw_cow_image")
            img = self.draw_tracks_of_selected_cow(img, 190)  # draw_annotation_data
        img = self.draw_bounding_boxes_for_selected_cow(img)  # draw_annotation_data

        # Resize the image to fit a 16:9 aspect ratio
        img = self.resize_to_aspect_ratio(img, 16 / 9)

        # Resize the image to a maximum width of 600 pixels while maintaining the aspect ratio
        base_width = 1200
        w_percent = self.image_base_width / float(img.width)
        h_size = int(float(img.height) * float(w_percent))
        img = img.resize((self.image_base_width, h_size), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)

    def handle_slider_click(self, event):
        """
        Handle the slider click event.

        Parameters:
        - event: tkinter Event object

        Returns:
        None
        """
        # Update the slider position based on the x-coordinate of the click
        # Calculate original_x
        original_x = (event.x / 1200) * (len(self.image_files) - 2)

        self.update_slider(original_x)

        self.time_tracker.record_button_press("Slider clicked at", int(original_x))

        selected_cow = self.app_state.get_selected_cow()
        self.show_all_windows()

    def change_image(self, direction):
        """
        Change the image by the specified direction.

        Parameters:
        - direction: string, "next" or "previous"

        Returns:
        None
        """
        if direction == "next":
            # Go to the next image
            self.app_state.add_current_image_frame()
            current_image_frame = self.app_state.get_current_image_frame()
            if current_image_frame > len(self.image_files) - 1:
                self.app_state.set_current_image_frame(len(self.image_files) - 1)
        elif direction == "previous":
            # Go to the previous image
            self.app_state.subtract_current_image_frame()
            current_image_frame = self.app_state.get_current_image_frame()
            if current_image_frame <= 1:
                self.app_state.set_current_image_frame(1)

        current_image_frame = self.app_state.get_current_image_frame()
        self.update_slider(current_image_frame)
        self.show_all_windows()
        self.time_tracker.record_image_change(current_image_frame)

    def change_image_10(self, direction):
        """
        Change the image by the specified direction.

        Parameters:
        - direction: string, "next" or "previous"

        Returns:
        None
        """
        if direction == "next":
            # Go to the next image
            self.app_state.add_ten_to_current_image_frame()
            current_image_frame = self.app_state.get_current_image_frame()
            if current_image_frame > len(self.image_files) - 1:
                self.app_state.set_current_image_frame(len(self.image_files) - 1)
        elif direction == "previous":
            # Go to the previous image
            self.app_state.subtract_ten_to_current_image_frame()
            current_image_frame = self.app_state.get_current_image_frame()
            if current_image_frame <= 1:
                self.app_state.set_current_image_frame(1)

        current_image_frame = self.app_state.get_current_image_frame()
        self.update_slider(current_image_frame)
        self.show_all_windows()
        self.time_tracker.record_image_change(current_image_frame)

    def change_image_by_frame(self, frame):
        """
        Change the image by the frame number.

        Parameters:
        - frame: int, the frame number

        Returns:
        None
        """
        self.app_state.set_current_image_frame(frame)
        current_image_frame = self.app_state.get_current_image_frame()
        self.update_slider(current_image_frame)
        self.show_all_windows()
