import asyncio
import numpy as np

# Note: winsdk OCR requires Windows 10/11 and async.
# We'll use a wrapper since it's a bit verbose.
try:
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder, SoftwareBitmap
    from winsdk.windows.storage.streams import DataWriter, InMemoryRandomAccessStream
    WIN_OCR_AVAILABLE = True
except ImportError:
    WIN_OCR_AVAILABLE = False

async def extract_text(image_bytes: bytes):
    if not WIN_OCR_AVAILABLE:
        raise RuntimeError("winsdk not installed or not supported on this OS")
    
    # Write bytes to random access stream
    stream = InMemoryRandomAccessStream()
    writer = DataWriter(stream)
    writer.write_bytes(image_bytes)
    await writer.store_async()
    await writer.flush_async()
    stream.seek(0)
    
    # Decode image
    decoder = await BitmapDecoder.create_async(stream)
    software_bitmap = await decoder.get_software_bitmap_async()
    
    # Setup OCR Engine
    lang = Language("en-US")
    if not OcrEngine.is_language_supported(lang):
        engine = OcrEngine.try_create_from_user_profile_languages()
    else:
        engine = OcrEngine.try_create_from_language(lang)
        
    if not engine:
        raise RuntimeError("No suitable OCR engine found.")
        
    result = await engine.recognize_async(software_bitmap)
    
    lines = []
    for line in result.lines:
        for word in line.words:
            rect = word.bounding_rect
            lines.append({
                "text": word.text,
                "rect": {
                    "x": rect.x,
                    "y": rect.y,
                    "width": rect.width,
                    "height": rect.height
                }
            })
    return lines
