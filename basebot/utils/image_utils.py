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


def crop_image(vertical:bool, img:Image, percent:int, verbose:bool=True) -> Image:
    left = 0 
    upper = 0
    right = img.width 
    lower = img.height
    if vertical:
        if verbose:
            print('\tImage:cropping vertical')
        trim = img.height*(percent / 100)
        trim_half = round(trim / 2)
        upper += trim_half
        lower -= trim_half
    elif args.horizontal:
        if verbose:
            print('Image:cropping horizontal')
        trim = img.width*(percent / 100)
        trim_half = round(trim / 2)
        left += trim_half
        right -= trim_half
    img = img.crop((left, upper, right, lower))
    return img


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--path', type=str, help='Path to image file' )
    parser.add_argument('-o','--out', type=str, required=False, help='Path to new image file' )
    parser.add_argument('--vertical', action='store_true')
    parser.add_argument('--horizontal', action='store_true')
    parser.add_argument('--pct', type=int, help='Percent to trim using center crop : (0, 100)')
    args = parser.parse_args()
    img = Image.open(args.path)
    

    img.save(args.path)


