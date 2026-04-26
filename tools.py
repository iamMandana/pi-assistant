from actions.notes import write_note, read_notes
from actions.system_tools import get_time_date, system_health
from actions.utils import calculate
from actions.network import wifi_scan, public_ip
from actions.camera import camera
from actions.vision_tools import vision_describe, describe_saved_image, describe_last_image, describe_saved_video
from actions.media_viewer import open_file_async

# Central tool registry used by controller to map parsed actions to execution functions
TOOLS = {
    "write_note": lambda args: write_note(args),
    "read_note": lambda args: read_notes(),
    "time_date": lambda args: get_time_date(),
    "calculate": lambda args: calculate(args),
    "system_health": lambda args: system_health(),
    "wifi_scan": lambda args: wifi_scan(),
    "public_ip": lambda args: public_ip(),
    "describe_saved_image": describe_saved_image,
    "take_picture": lambda _: f"Image saved as {camera.take_picture()}",
    "record_video": lambda duration: f"Video saved: {camera.record_video(duration)}",
    "vision_describe": vision_describe,
    "describe_last_image": describe_last_image,
    "open_image": lambda image_id: open_file_async(image_id),
    "open_video": lambda video_id: open_saved_video(video_id),
    "describe_saved_video": describe_saved_video,
}
