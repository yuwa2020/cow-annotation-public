import tkinter as tk
import tkinter.font as tkFont


class CheatMode:
    def __init__(
        self,
        right_canvas,
        show_all_windows,
        app_state,
        time_tracker,
    ):
        self.show_all_windows = show_all_windows
        self.app_state = app_state
        self.time_tracker = time_tracker
        self.setup_cheat_mode(right_canvas)

    def setup_cheat_mode(self, right_canvas):
        self.cheat_input_value = tk.StringVar()
        self.evaluation_mode = tk.IntVar()
        cheat_mode = tk.Frame(right_canvas)
        cheat_mode.pack(side=tk.LEFT)

        check_button = tk.Checkbutton(
            cheat_mode,
            text="Evaluation Mode",
            variable=self.evaluation_mode,
            command=self.on_check,
        )
        check_button.grid(row=4, column=0)

        customFont = tkFont.Font(family="Helvetica", size=10, weight="bold")
        cheat_mode_label = tk.Label(
            cheat_mode,
            text="Cheat Mode: Manual Select Cow#",
            font=customFont,
            fg="red",
        )
        cheat_mode_label.grid(row=0, column=0)

        # Define a validation command
        vcmd = (cheat_mode.register(lambda P: len(P) <= 2), "%P")

        cheat_mode_input_field = tk.Entry(
            cheat_mode,
            textvariable=self.cheat_input_value,
            highlightthickness=0,
            bd=0,
            highlightbackground="#FFFFFF",
            highlightcolor="#FFFFFF",
            validate="key",
            validatecommand=vcmd,
            width=2,
        )
        cheat_mode_input_field.grid(row=1, column=0)

        confirm_button = tk.Button(
            cheat_mode,
            text="Confirm",
            command=self.cheat_mode_show,
        )
        confirm_button.grid(row=2, column=0)

    def cheat_mode_check_input(self):
        value = self.cheat_input_value.get()
        if not value:
            print("Input field is empty")
            self.cheat_selected_cow = None
        else:
            print(f"Input value is: {value}")
            if 1 <= int(value) <= 65:
                self.cheat_selected_cow = int(value)

    def cheat_mode_show(self):
        value = self.cheat_input_value.get()
        if not value:
            print("Input field is empty")
            self.cheat_selected_cow = None
        else:
            print(f"Input value is: {value}")
            if 1 <= int(value) <= 65:
                self.cheat_selected_cow = int(value)

        self.app_state.set_selected_cow(self.cheat_selected_cow)
        self.show_all_windows()

    # Evaluation Mode
    def on_check(self):
        if self.evaluation_mode.get() == 1:
            print("Checkbutton is checked")
            self.app_state.change_evaluation_mode()
        else:
            print("Checkbutton is unchecked")
            self.app_state.change_evaluation_mode()
        self.show_all_windows()
