import time


class TimeTracker:
    def __init__(self):
        self.timers = {}  # Dictionary to store timers for individual cows
        self.cow_annnotation_times = (
            []
        )  # New attribute to store the cow annotation times
        self.button_history = []  # New attribute to store the button history

    def start_or_resume_timer(self, cow_id):
        if cow_id in self.timers:
            if "start_time" not in self.timers[cow_id]:
                # If the timer was paused, update start_time to current time
                self.timers[cow_id]["start_time"] = time.time()
                print(f"Resumed timer for cow {cow_id}.")
            else:
                # If the timer was stopped, create a new timer for the cow
                print(
                    f"Timer for cow {cow_id} is already running. Starting a new timer."
                )
                self.timers[cow_id]["start_time"] = time.time()
        else:
            # If there is no timer for the cow, start a new timer
            print(f"Starting a new timer for cow {cow_id}.")
            self.timers[cow_id] = {"start_time": time.time(), "total_time": 0}

    def pause_timer(self, cow_id):
        if cow_id in self.timers and "start_time" in self.timers[cow_id]:
            elapsed_time = time.time() - self.timers[cow_id]["start_time"]
            self.timers[cow_id]["total_time"] += elapsed_time
            del self.timers[cow_id]["start_time"]  # Remove start_time to indicate pause
            print(
                f"Paused timer for cow {cow_id}. Elapsed Time: {elapsed_time} seconds. Total Time: {self.timers[cow_id]['total_time']} seconds"
            )
        else:
            print(f"No active timer found for cow {cow_id}.")

    def stop_timer(self, cow_id):
        if cow_id in self.timers and "start_time" in self.timers[cow_id]:
            elapsed_time = time.time() - self.timers[cow_id]["start_time"]
            self.timers[cow_id]["total_time"] += elapsed_time
            del self.timers[cow_id]["start_time"]  # Remove start_time to indicate stop
            print(
                f"Timer stopped for cow {cow_id}. Total Time: {self.timers[cow_id]['total_time']} seconds"
            )
            self.cow_annnotation_times.append(
                (cow_id, self.timers[cow_id]["total_time"])
            )
        elif cow_id in self.timers and "start_time" not in self.timers[cow_id]:
            print(
                f"Timer for cow {cow_id} is already paused. Use 'resume_timer' to continue."
            )
        else:
            print(f"No active timer found for cow {cow_id}.")  #

    def get_all_cow_times(self):
        return self.cow_annnotation_times

    def start_total_timer(self):
        self.total_time_start = time.time()  # New attribute to store the total time

    def record_button_press(self, button, number=None):
        last_button_press_time = time.time() - self.total_time_start
        print(
            f"Button '{button} {number}' was pressed at {last_button_press_time} seconds"
        )
        self.button_history.append(("Button", button, number, last_button_press_time))

    def record_key_press(self, key):
        last_key_press_time = time.time() - self.total_time_start
        print(f"Key '{key}' was pressed at {last_key_press_time} seconds")
        self.button_history.append(("key", key, "", last_key_press_time))

    def record_image_change(self, image_frame):
        last_image_change_time = time.time() - self.total_time_start
        print(f"Frame changed to {image_frame} at {last_image_change_time} seconds")
        self.button_history.append(
            ("Frame Change", "", image_frame, last_image_change_time)
        )

    def get_all_history(self):
        return (self.button_history, self.cow_annnotation_times)
