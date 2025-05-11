import uuid
import os

from typing import TypedDict, Optional
from django.core.files.uploadedfile import UploadedFile

VIDEO_ROOT = "files/videos"

class UploadedVideo(TypedDict):
    video_path: str
    video_root: str
    random_name: str


def _make_uploaded_video(video: UploadedFile, random_name: str) -> UploadedVideo:
    return {
        "video_path": f"{VIDEO_ROOT}/{random_name}/{video.name}",
        "video_root": VIDEO_ROOT,
        "random_name": random_name
    }

def upload_video(video: UploadedFile) -> tuple[bool, str, Optional[UploadedVideo]]:
    #
    # Validate video exists
    #
    if not video:
        return False, "Video not found!", None

    #
    # Validate video size under 20MB
    #
    if video.size > 20971520:
        return False, "Video size exceeds 20MB limit!", None

    #
    # Validate video format is mp4
    #
    if not video.name.endswith(".mp4"):
        return False, "Video format must be mp4!", None

    random_name = uuid.uuid4()

    #
    # Change video name by uuid
    #
    video.name = f"{random_name}.mp4"

    #
    # Create folder if not exists
    #
    if not os.path.exists("files"):
        os.makedirs("files")

    #
    # Create folder video if not exists
    #
    if not os.path.exists(VIDEO_ROOT):
        os.makedirs(VIDEO_ROOT)

    #
    # Create folder with random name if not exists
    #
    if not os.path.exists(f"{VIDEO_ROOT}/{random_name}"):
        os.makedirs(f"{VIDEO_ROOT}/{random_name}")

    #
    # Create and upload file
    #
    with open(f"{VIDEO_ROOT}/{random_name}/{video.name}", "wb+") as destination:
        for chunk in video.chunks():
            destination.write(chunk)

    return True, "Video uploaded successfully!", _make_uploaded_video(video, random_name)
