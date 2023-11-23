import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

from PIL import Image, ImageFont, ImageDraw, ImageEnhance


def plot_rectangle_on_image(image_file_name, rectangle_coords, color='green'):
    if len(rectangle_coords) == 4:
        point1 = (rectangle_coords[0])
        point2 = (rectangle_coords[2])
        width = rectangle_coords[2][0] - rectangle_coords[0][0]
        height = rectangle_coords[1][1] - rectangle_coords[0][1]
        source_img = Image.open(image_file_name)

        draw = ImageDraw.Draw(source_img)
        draw.rectangle((point1, point2), fill=None, outline=color, width=5)

        source_img.save(image_file_name, "JPEG")

def plot_rectangle_on_image_obj(image, rectangle_coords, color='green'):
    if len(rectangle_coords) == 4:
        point1 = (rectangle_coords[0])
        point2 = (rectangle_coords[2])
        draw = ImageDraw.Draw(image)
        draw.rectangle((point1, point2), fill=None, outline=color, width=5)
    return image

def plot_polygon_on_image_obj(image, polygon_coords, color='green'):
    draw = ImageDraw.Draw(image)
    draw.polygon(polygon_coords, fill=None, outline=color, width=5)
    return image


def plot_lines_on_image(image_file_name, lines_coords, color='green'):
    image = Image.open(image_file_name)
    for line_coords in lines_coords:
        image = plot_polygon_on_image_obj(image, line_coords, color)
    image.save(image_file_name, "JPEG")

# def plot_on_image(image_file_name, output_file_name, lines,)

