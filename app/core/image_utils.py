from PIL import Image
import io
import os
from typing import Optional

def resize_image(image_data: bytes, size: tuple[int, int] = (256, 256)) -> bytes:
    """
    Resize an image to the specified size while maintaining aspect ratio (thumbnail).
    Returns the resized image data as bytes (format: PNG).
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (Alpha channel handles RGBA)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
            
        # Use thumbnail method to resize maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to buffer
        output = io.BytesIO()
        img.save(output, format="PNG", optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_data  # Return original if resizing fails

def save_thumbnail(image_data: bytes, filename: str, upload_dir: str) -> str:
    """
    Resize and save a thumbnail to the specified directory.
    Returns the relative path to the saved thumbnail.
    """
    resized_data = resize_image(image_data)
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(resized_data)
        
    return filename  # Or full relative URL depends on how app handles static files
