class ApplicationState:
    def __init__(self, config):
        self.selected_cow = None
        self.selected_cow_annotation = None
        self.multi_view_original = None
        self.display_bounding_boxes = True
        self.current_image_frame = 0
        self.top_10_cows_image_page = 1
        self.saved_cows = []
        self.evaluation_mode = False
        self.selected_cow_exist = False
        self.eval_cow = config.eval_cow

    def get_selected_cow(self):
        return self.selected_cow

    def set_selected_cow(self, cow):
        self.selected_cow = int(cow)

    def reset_selected_cow(self):
        self.selected_cow = None

    def save_selected_cow_annotation(self, annotation):
        self.selected_cow_annotation = annotation

    def get_selected_cow_annotation(self):
        return self.selected_cow_annotation

    def get_multi_view_original(self):
        return self.multi_view_original

    def set_multi_view_original(self, frame):
        self.multi_view_original = int(frame)

    def reset_multi_view_original(self):
        self.multi_view_original = None

    def get_display_bounding_boxes(self):
        return self.display_bounding_boxes

    def change_display_bounding_boxes(self):
        if self.display_bounding_boxes:
            self.display_bounding_boxes = False
        else:
            self.display_bounding_boxes = True

    def get_current_image_frame(self):
        return self.current_image_frame

    def set_current_image_frame(self, frame):
        self.current_image_frame = int(frame)

    def add_current_image_frame(self):
        self.current_image_frame += 1

    def subtract_current_image_frame(self):
        self.current_image_frame -= 1

    def add_ten_to_current_image_frame(self):
        self.current_image_frame += 10

    def subtract_ten_to_current_image_frame(self):
        self.current_image_frame -= 10

    def get_top_10_cows_image_page(self):
        return self.top_10_cows_image_page

    def set_top_10_cows_image_page(self, value):
        self.top_10_cows_image_page = int(value)

    def add_top_10_cows_image_page(self):
        self.top_10_cows_image_page += 1

    def subtract_top_10_cows_image_page(self):
        self.top_10_cows_image_page -= 1

    def get_evaluation_mode(self):
        return self.evaluation_mode

    def change_evaluation_mode(self):
        if self.evaluation_mode:
            self.evaluation_mode = False
        else:
            self.evaluation_mode = True

    def get_eval_cow(self):
        return self.eval_cow

    def get_saved_cows(self):
        return self.saved_cows

    def add_saved_cows(self, seleted_cow, seleted_top_k_cow):
        self.saved_cows.append((seleted_cow, seleted_top_k_cow))

    def get_selected_cow_exist(self):
        return self.selected_cow_exist

    def set_selected_cow_exist(self, value):
        self.selected_cow_exist = value
