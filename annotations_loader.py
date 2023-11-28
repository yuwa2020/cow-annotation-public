import numpy as np

# Load annotations data from the specified file into dictionaries:
# - 'annotations': Dictionary with frames as keys and lists of cow annotations as values.
# - 'individual_cow_annotations': Dictionary with cow tags as keys and lists of annotations including transformed dimensions.
# - 'individual_identification_annotations': Dictionary with frames as keys and lists of cow annotations as values.


class AnnotationsLoader:
    def __init__(self):
        pass

    def load_annotations(self, file_path):
        """
        Load annotations from a given file.

        Parameters:
        - file_path: str, path to the annotations file

        Returns:
        - annotations: dict, dictionary of annotations
        - individual_cow_annotations: dict, dictionary of annotations
        """
        with open(file_path, "r") as file:
            lines = file.readlines()

        annotations = {}
        individual_cow_annotations = {}
        for line in lines:
            values = line.strip().split(",")
            frame, cow_tag, x, y, w, h, camera_num = map(float, values[:7])
            frame = int(frame)
            # annotations
            if frame not in annotations:
                annotations[frame] = []
            annotations[frame].append(
                (int(cow_tag), int(x), int(y), int(w), int(h), int(camera_num))
            )
            # individual_cow_annotations
            if cow_tag not in individual_cow_annotations:
                individual_cow_annotations[cow_tag] = []
            if w > h:
                transform_dimensions = 0
            else:
                transform_dimensions = 1

            individual_cow_annotations[cow_tag].append(
                (
                    int(frame),
                    int(x),
                    int(y),
                    int(w),
                    int(h),
                    int(camera_num),
                    transform_dimensions,
                )
            )
        # Find the largest bounding box for each cow
        # largest_bbox_per_cow = (
        #     {}
        # )  # Dictionary to store largest bounding box for each cow

        # for cow_tag, info_annotations in individual_cow_annotations.items():
        #     largest_bbox = {}  # Dictionary to store largest bounding box for each frame
        #     for annotation in info_annotations:
        #         frame, x, y, w, h, _, _ = annotation
        #         size = w * h
        #         if frame not in largest_bbox or size > largest_bbox[frame][0]:
        #             largest_bbox[frame] = (size, (x, y, w, h))

        #     largest_bbox_per_cow[cow_tag] = largest_bbox

        nearest_bbox_per_cow = (
            {}
        )  # Dictionary to store nearest bounding box for each cow

        for cow_tag, info_annotations in individual_cow_annotations.items():
            nearest_bbox = {}  # Dictionary to store nearest bounding box for each frame
            prev_bbox = None  # Store the previous selected bounding box
            for annotation in sorted(info_annotations):
                frame, x, y, w, h, _, _ = annotation
                bbox = (x, y, w, h)
                if prev_bbox is None:  # first frame
                    nearest_bbox[frame] = (0, bbox)  # distance is 0 for the first frame
                    prev_bbox = 0, x, y, w, h  # update the previous bounding box
                    current_bbox = 0, x, y, w, h
                else:
                    if current_bbox[0] != frame:
                        prev_bbox = current_bbox
                    distance = np.sqrt(
                        (x - prev_bbox[1]) ** 2 + (y - prev_bbox[2]) ** 2
                    )
                    if frame not in nearest_bbox or distance < nearest_bbox[frame][0]:
                        nearest_bbox[frame] = (distance, bbox)
                        current_bbox = (
                            int(frame),
                            int(x),
                            int(y),
                            int(w),
                            int(h),
                        )  # update the previous bounding box only if it is selected

            nearest_bbox_per_cow[cow_tag] = nearest_bbox

        return (annotations, individual_cow_annotations, nearest_bbox_per_cow)

    def load_individual_identification_annotations(self, file_path):
        """
        Load individual identification annotations from a given file.

        Parameters:
        - file_path: str, path to the annotations file

        Returns:
        - data : list, list of annotations
        """
        with open(file_path, "r") as file:
            lines = file.readlines()

        annotations = {}
        for line in lines:
            values = line.strip().split(",")
            (
                frame,
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
            ) = map(float, values[:13])
            frame = int(frame)
            # annotations
            if frame not in annotations:
                annotations[frame] = []
            annotations[frame].append(
                (
                    int(cow_tag),
                    int(query_x),
                    int(query_y),
                    int(query_w),
                    int(query_h),
                    int(cow_id),
                    float(distance),
                    int(top_10_frame),
                    int(x),
                    int(y),
                    int(w),
                    int(h),
                )
            )
        return annotations
