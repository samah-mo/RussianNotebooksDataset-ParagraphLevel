from PIL import Image, ImageDraw

def plot_rectangle_on_image(image_file_name, rectangle_coords, color='green'):
    if len(rectangle_coords) == 4:
        point1 = (rectangle_coords[0])
        point2 = (rectangle_coords[2])
        source_img = Image.open(image_file_name)

        draw = ImageDraw.Draw(source_img)
        draw.rectangle((point1, point2), fill=None, outline=color, width=5)

        source_img.save(image_file_name, "JPEG")

def plot_polygon_on_image_obj(image, polygon_coords, color='green'):
    draw = ImageDraw.Draw(image)
    draw.polygon(polygon_coords, fill=None, outline=color, width=5)
    return image

def plot_lines_on_image(image_file_name, lines_coords, color='green'):
    image = Image.open(image_file_name)
    for line_coords in lines_coords:
        image = plot_polygon_on_image_obj(image, line_coords, color)
    image.save(image_file_name, "JPEG")
