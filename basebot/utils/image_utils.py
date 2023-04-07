from PIL import Image
import numpy as np 
import io, base64




def resize_frame_with_aspect_ratio(im, max_pixels):
    im = Image.fromarray(im)
    width = im.width
    height = im.height
    pixels = width*height
    if pixels > max_pixels:
        factor = np.sqrt(max_pixels / pixels)
        # print(factor, max_pixels, pixels)
        width = round(width * factor)
        height = round(height * factor)
        width = width - (width % 8)
        height = height - (height % 8) 
        im = im.resize((width, height))
    return np.array(im)


def img_to_b64_string(img: Image) -> str:
    im_file = io.BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  
    im_b64 = base64.b64encode(im_bytes)
    im_b64 = im_b64.decode('utf-8')
    return im_b64


def b64_string_to_img(im_b64: str) -> Image:
    im_bytes = base64.b64decode(im_b64)  
    im_file = io.BytesIO(im_bytes)  
    img2 = Image.open(im_file)   
    return img2

