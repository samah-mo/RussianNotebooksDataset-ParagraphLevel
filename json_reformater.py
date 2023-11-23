import json
import shutil
import draw_on_image
import os
from scipy.spatial import ConvexHull

def reformat_coords(points):
    points_number = int(len(points) / 2)
    return " ".join([",".join([str(points[2 * i]), str(points[2 * i + 1])]) for i in range(points_number)])

def coords_from_text(coord_text):
    try:
        return [(float(point.split(",")[0]), float(point.split(",")[1])) for point in coord_text.split(" ")]
    except:
        print("[coords_from_text] text is not well formatted")
        print(coord_text)
        return []

def words_sorrounding_rectangle(words):
    points = []
    for word in words:
        points.extend(word["segmentation"][0])
    points_number = int(len(points) / 2)
    if points_number == 0:
        return reformat_coords([0 for i in range(8)])
    x = [points[2 * i] for i in range(points_number)]
    y = [points[2 * i + 1] for i in range(points_number)]
    rectangle = []
    rectangle.extend([min(x), min(y)])
    rectangle.extend([min(x), max(y)])
    rectangle.extend([max(x), max(y)])
    rectangle.extend([max(x), min(y)])
    return reformat_coords(rectangle)

def polygon_merge(polygon, word_polygon):
    if len(polygon) < 3 or len(word_polygon) < 3:
        print("[error] polygon_merge expected polygons with more than 3 points")
        print(polygon)
        print(word_polygon)
    polygon_right = word_left = 0
    polygon_points_number = int(len(polygon) / 2)
    xs = [polygon[2 * i] for i in range(polygon_points_number)]
    ys = [polygon[2 * i + 1] for i in range(polygon_points_number)]
    for i,x in enumerate(xs):
        if x > xs[polygon_right]:
            polygon_right = i
    if xs[(polygon_right -1 + polygon_points_number) % polygon_points_number] > xs[(polygon_right + 1 + polygon_points_number) % polygon_points_number]:
        polygon_right -= 1
    polygon_right *= 2
        
    word_points_number = int(len(word_polygon) / 2)
    xs = [word_polygon[2 * i] for i in range(word_points_number)]
    ys = [word_polygon[2 * i + 1] for i in range(word_points_number)]
    for i,x in enumerate(xs):
        if x < xs[word_left]:
            word_left = i
    if xs[(word_left -1 + word_points_number) % word_points_number] < xs[(word_left + 1 + word_points_number) % word_points_number]:
        word_left -= 1
    word_left *= 2
    coords = []
    
    coords.extend(polygon[:polygon_right + 2])
    if word_left + 2 != len(word_polygon) / 2: # the last point in the word polygon
        coords.extend(word_polygon[word_left + 2:])
    coords.extend(word_polygon[:word_left + 2])
    if polygon_right + 2 != len(polygon) / 2: # the last point in the polygon
        coords.extend(polygon[polygon_right + 2:])
    
    return coords

def words_sorrounding_polygon(words):
    if len(words) == 0:
        return reformat_coords([0 for i in range(8)])
    polygon = words[0]["segmentation"][0]
    if len(words) > 1:
        for word in words[1:]:
            polygon = polygon_merge(polygon, word["segmentation"][0]) 
    return reformat_coords(polygon)

def lines_sorrounding_rectangle(lines):
    points = []
    for line in lines:
        points.extend(coords_from_text(line["Coords"]["_points"]))
    x = [point[0] for point in points]
    y = [point[1] for point in points]

    rectangle = []
    rectangle.extend([min(x), min(y)])
    rectangle.extend([min(x), max(y)])
    rectangle.extend([max(x), max(y)])
    rectangle.extend([max(x), min(y)])
    return reformat_coords(rectangle)

def lines_sorrounding_convex_polygon(lines):
    points = []
    for line in lines:
        points.extend(coords_from_text(line["Coords"]["_points"]))
    hull = ConvexHull(points)

    polygon_points = []
    for vertix in hull.vertices:
        polygon_points.append(points[vertix][0])
        polygon_points.append(points[vertix][1])

    return reformat_coords(polygon_points)

def sort_words(words):
    sorted_words = words.copy()
    for i in range(len(sorted_words)):
        for j in range(i, len(sorted_words)):
            word1 = sorted_words[i].copy()
            word2 = sorted_words[j].copy()
            word1_points_number = int(len(word1["segmentation"][0]) / 2)
            word2_points_number = int(len(word2["segmentation"][0]) / 2)
            if min([word2["segmentation"][0][2 * k] for k in range(word2_points_number)]) <\
               min([word1["segmentation"][0][2 * k] for k in range(word1_points_number)]):
                sorted_words[i] = word2
                sorted_words[j] = word1
    return sorted_words

def sort_lines(lines):
    sorted_lines = lines.copy()
    for i in range(len(sorted_lines)):
        for j in range(i, len(sorted_lines)):
            line1 = sorted_lines[i].copy()
            line2 = sorted_lines[j].copy()
            if (line2["segmentation"][0][1] + line2["segmentation"][0][3]) < (
                    line1["segmentation"][0][1] + line1["segmentation"][0][3]):
                sorted_lines[i] = line2
                sorted_lines[j] = line1
    return sorted_lines

def sort_lines_by_x(lines):
    sorted_lines = lines.copy()
    for i in range(len(sorted_lines)):
        for j in range(i, len(sorted_lines)):
            line1 = sorted_lines[i].copy()
            line2 = sorted_lines[j].copy()
            line1_points_number = int(len(line1["segmentation"][0]) / 2)
            line2_points_number = int(len(line2["segmentation"][0]) / 2)
            if min([line2["segmentation"][0][2 * k] for k in range(line2_points_number)]) <\
               min([line1["segmentation"][0][2 * k] for k in range(line1_points_number)]):
                sorted_lines[i] = line2
                sorted_lines[j] = line1
    return sorted_lines

def line_words_text(words):
    sorted_words = sort_words(words)
    try:
        return " ".join([word["attributes"]["translation"] for word in sorted_words if word["attributes"]["translation"]])
    except Exception as e:
        print(e)
        print("failed for create the text of the line")
        print(sorted_words)
        return ""

def paragraph_text(formated_lines):
    # sorted_lines = sort_lines(formated_lines)
    return "\n".join([line["TextEquiv"]["Unicode"] for line in formated_lines])

def reformat_line(line):
    reformated_line = dict()
    reformated_line["Baseline"] = {"_points": reformat_coords(line["segmentation"][0])}
    reformated_line["_id"] = "l" + str(line["index"])
    reformated_line["_custom"] = "readingOrder {index:" + str(line["index"]) + ";}"
    reformated_line["Coords"] = {"_points": words_sorrounding_polygon(line["words"])}
    reformated_line["TextEquiv"] = {"Unicode": line_words_text(line["words"])}
    return reformated_line


def image_data_reformat(image_data, pages, config):
    output_folder_name = config["output_sub_folder"]
    page_folder = os.path.join(output_folder_name, "page")
    if not os.path.exists(page_folder):
        os.makedirs(page_folder)
    image_path = os.path.join(page_folder, image_data["file_name"])
    shutil.copyfile(os.path.join(config["download_dir"], "images/", image_data["file_name"]), image_path)

    formatted_data = dict()
    with open("template.json") as f:
        formatted_data = json.load(f)
    page = dict()
    page["_imageFilename"] = image_data["file_name"]
    page["_imageWidth"] = str(image_data["width"])
    page["_imageHeight"] = str(image_data["height"])
    paragraphs = []
    for page_data in image_data["pages"]:
        paragraphs.extend(page_data["paragraphs"])
    paragraphs_number = len(paragraphs)
    page["ReadingOrder"] = {
        "OrderedGroup": {
            "RegionRefIndexed": [{"_regionRef": "r" + str(i), "_index": str(i)} for i in range(paragraphs_number)],
            "_id": "ro357564684568544579089_" + str(image_data["id"])
        }
    }
    page["TextRegion"] = []
    for i, paragraph in enumerate(paragraphs):
        text_region = {
            "_id": "r" + str(i),
            "_custom": "readingOrder {index:" + str(i) + ";}",
            "_type": "paragraph"
        }

        # ["TextLine"] add all lines
        paragraph_lines = paragraph["lines"].copy()
        for j, line in enumerate(paragraph_lines):
            paragraph_lines[j] = reformat_line(line)
        text_region["TextLine"] = paragraph_lines

        # ["Coords"] calc rectangle around paragraph
        paragraph_polygon = lines_sorrounding_convex_polygon(paragraph_lines)
        text_region["Coords"] = {"_points": paragraph_polygon}
        # text_region["Coords"] = {"_points": lines_sorrounding_rectangle(paragraph_lines)}
        if config["draw_on_image_flag"]:
            images_folder = os.path.join(output_folder_name, "images")
            if not os.path.exists(images_folder):
                os.makedirs(images_folder)
            image_path = os.path.join(images_folder, image_data["file_name"])
            shutil.copyfile(os.path.join(config["download_dir"], "images/", image_data["file_name"]), image_path)
            draw_on_image.plot_lines_on_image(image_path, [coords_from_text(line["Coords"]["_points"]) for line in paragraph_lines])
            draw_on_image.plot_lines_on_image(image_path, [page["segmentation"][0] for page in pages])
            draw_on_image.plot_lines_on_image(image_path, [coords_from_text(paragraph_polygon)], 'red')

        # ["TextEquiv"] add the combined text
        text_region["TextEquiv"] = {"Unicode": paragraph_text(paragraph_lines)}

        page["TextRegion"].append(text_region)
    formatted_data["PcGts"]["Page"] = page
    return formatted_data