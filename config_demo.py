class Config:
    IMAGE_DIR = "cow-obhiro-videos/images/2021071511-1"
    DATABASE_IMAGE_DIR = "cow-obhiro-videos/images/2021071511-2"
    ANNOTATION_FILE = "cow-obhiro-videos/txt/2021071511-1/2021071511-1-multicam.txt"
    IDENTIFICATION_FILE = "cow-obhiro-videos/cropped_img_txt_result/2021051711-1/2021071511-1_2021071511-2.txt"

    # Multi_view_window
    SELECTED_COW_DEFAULT = "selected_cow_default.jpg"
    SELECTED_COW_NO_PHOTO = "no_data.png"
    MULTI_WINDOW_DEFAULT = "default_multi_view_frame.jpg"
    # Maximum dimensions for Selected_cow image
    SELECTED_COW_FRAME_WIDTH = 300
    SELECTED_COW_FRAME_HEIGHT = 205
    # Maximum dimensions for Multi-view images
    MULTI_WINDOW_FRAME_WIDTH = 215
    MULTI_WINDOW_FRAME_HEIGHT = 185

    # Top_k_view_window
    TOP10_IMAGE_DIR_DEFAULT = "cow-obhiro-videos/cropped_img_by_ID/default_path"
    TOP10_IMAGE_DIR = "cow-obhiro-videos/cropped_img_by_ID/2022040205-2"

    OUTPUT_NAME = "annotation_result.csv"
    # Maximum dimensions for Top10 images
    TOP10_FRAME_WIDTH = 200
    TOP10_FRAME_HEIGHT = 200

    # Evaluation
    eval_cow = list(range(1, 64))
