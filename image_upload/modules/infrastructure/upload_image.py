import os
import uuid

from typing import TypedDict, Optional

from django.core.files.uploadedfile import UploadedFile

IMAGE_ROOT = "files/images"

class UploadedImage(TypedDict):
    image_path: str
    image_root: str
    random_name: str

def upload_image(image: UploadedFile) -> tuple[bool, str, Optional[UploadedImage]]:
    #
    # Validate image exists
    #
    if not image:
        return False, "Image not found!", None
    
    #
    # Validate image size under 10MB
    #
    if image.size > 10485760:
        return False, "Image size exceeds 10MB limit!", None
    
    #
    # Validate image format is jpg or png
    #
    if image.content_type not in ["image/jpeg", "image/png"]:
        return False, "Image format must be jpg or png!", None
    
    #
    # Validate image is not empty
    #
    if image.size == 0:
        return False, "Image is empty!", None
    
    random_name = uuid.uuid4()
    
    #
    # Change image name by uuid
    #
    image.name = f"{random_name}.jpg"

    #
    # Create folder if not exists
    #
    if not os.path.exists(IMAGE_ROOT):
        os.makedirs(IMAGE_ROOT)
    
    #
    # Create folder with random name if not exists
    #
    if not os.path.exists(f"{IMAGE_ROOT}/{random_name}"):
        os.makedirs(f"{IMAGE_ROOT}/{random_name}")

    #
    # Create and upload file
    #
    with open(f"{IMAGE_ROOT}/{random_name}/{image.name}", "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    

    return True, "Image uploaded successfully!", {
        "image_path": f"{IMAGE_ROOT}/{random_name}/{image.name}",
        "image_root": IMAGE_ROOT,
        "random_name": random_name
    }
    
