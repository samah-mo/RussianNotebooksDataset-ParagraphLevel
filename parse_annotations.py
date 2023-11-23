import json
import os.path
import json_reformater
import create_xml
from pprint import pformat
import shutil



from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def read_russian_notebooks_json(json_file):
    with open(json_file) as f:
        data = json.load(f)
    categories = data["categories"]
    images = data["images"]
    annotations = data["annotations"]
    return categories, images, annotations

def get_sorted_lines_of_imageID(annotations, image_id):
    image_lines = [x for x in annotations if x["image_id"] == image_id and x["category_id"] == 4]
    return json_reformater.sort_lines(image_lines)

def get_words_of_imageID(annotations, image_id):
    words = [x for x in annotations if x['image_id'] == image_id and "attributes" in x.keys()]
    return words

def get_pages_of_imageID(annotations, image_id):
    pages = [x for x in annotations if x['image_id'] == image_id and x["category_id"] == 3]
    return pages

def is_any_point_in_polygon(poly_coords, points_coords):
    polygon = Polygon([(poly_coords[2 * i], poly_coords[2 * i + 1]) for i in range(int(len(poly_coords) / 2))])
    points = [Point(points_coords[2 * i], points_coords[2 * i + 1]) for i in range(int(len(points_coords) / 2))]
    for point in points:
        if polygon.contains(point):
            return True

    return False

def get_words_of_line(words, line):
    line_words = set()
    line_coors = line['segmentation'][0]

    for word in words:
        word_coors = word['segmentation'][0]
        if is_any_point_in_polygon(word_coors, line_coors):
            line_words.add(pformat(word))

        # # print(word_coors)
        # word_coors = [(word_coors[2 * i], word_coors[2 * i + 1]) for i in range(int(len(word_coors) / 2))]
        # # print(word_coors)
        # polygon = Polygon(word_coors)
        # for point in [Point(line_coors[2 * i], line_coors[2 * i + 1]) for i in range(int(len(line_coors) / 2))]:
        #     if polygon.contains(point):
        #         line_words.add(pformat(word))
    line_words = list(line_words)
    for i,word in enumerate(line_words):
        line_words[i] = eval(word)

    for i in range(len(line_words)):
        for j in range(i, len(line_words)):
            word1 = line_words[i].copy()
            word2 = line_words[j].copy()
            if (word2["segmentation"][0][0] < (word1["segmentation"][0][0])):
                line_words[i] = word2
                line_words[j] = word1

    return line_words

def calc_begin_end(line):
    coords = line["segmentation"][0]
    points_number = int(len(coords) / 2)
    begin = min([coords[2 * i] for i in range(points_number)])
    end = max([coords[2 * i] for i in range(points_number)])
    return begin, end

def calc_up_down(line):
    coords = line["segmentation"][0]
    points_number = int(len(coords) / 2)
    up = min([coords[2 * i + 1] for i in range(points_number)])
    down = max([coords[2 * i + 1] for i in range(points_number)])
    return up, down

def check_same_paragraph(line, previous_down, image_height, height_ratio=0.05):
    up, _ = calc_up_down(line)
    return (up - previous_down) < image_height * height_ratio

def check_overlapping(line, begin, end):
    begin1, end1 = calc_begin_end(line)
    return (begin1 < end) and (begin < end1)

def print_line_words(line, words):
    line_words = get_words_of_line(words, line)
    line_text = "#".join([word['attributes']['translation'] for word in line_words])
    print(line_text)

def split_lines_to_left_right(lines):
    left = []
    right = []
    if len(lines) == 0:
        return left, right
    x_sorted_lines = json_reformater.sort_lines_by_x(lines)
    begin, end = calc_begin_end(x_sorted_lines[0])
    # print("-------------------------left lines-----------------")
    for i, line in enumerate(x_sorted_lines):
        if check_overlapping(line, begin, end):
            _, end1 = calc_begin_end(line)
            end = max(end, end1)
            left.append(line)
            # print_line_words(line, words)
            # print(end)
        else:
            # print("-------------------------break line-----------------")
            # print(calc_begin_end(line))
            # print_line_words(line, words)
            right = x_sorted_lines[i:]
            break
    left = json_reformater.sort_lines(left)
    right = json_reformater.sort_lines(right)
    return left, right

def split_lines_to_pages(lines, pages):
    def line_in_page(line, page):
        return is_any_point_in_polygon(page["segmentation"][0], line["segmentation"][0])

    left = []
    right = []
    if len(lines) == 0 or len(pages) == 0:
        return left, right

    for line in lines:
        if line_in_page(line, pages[0]):
            left.append(line)
        elif len(pages) > 1 and line_in_page(line, pages[1]):
            right.append(line)
        else:
            print("[error] line doesn't belong to any page")

    left = json_reformater.sort_lines(left)
    right = json_reformater.sort_lines(right)
    return left, right

def split_lines_to_paragraphs(lines, words, image_height):
    paragraphs = []
    if len(lines) == 0:
        return paragraphs
    lines = json_reformater.sort_lines(lines)
    for line in lines:
        line_words = get_words_of_line(words, line)
        line["words"] = line_words
    paragraph = dict()
    paragraph["lines"] = [lines[0].copy()]
    _, down = calc_up_down(lines[0])
    for line in lines[1:]:
        if check_same_paragraph(line, down, image_height):
            paragraph["lines"].append(line.copy())
        else:
            paragraphs.append(paragraph.copy())
            paragraph = dict()
            paragraph["lines"] = [line]
        _, down = calc_up_down(line)
    paragraphs.append(paragraph.copy())
    return paragraphs


def parse_annotations(annotations_json_file, config):
    output_folder_name = config["output_sub_folder"]
    images_data = []
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)
    categories, images, annotations = read_russian_notebooks_json(annotations_json_file)
    for image in images:
        print(image["file_name"])
        image_id = image["id"]
        words = get_words_of_imageID(annotations, image_id)
        sorted_lines = get_sorted_lines_of_imageID(annotations, image_id)
        pages = get_pages_of_imageID(annotations, image_id)

        for i,line in enumerate(sorted_lines):
            line["index"] = i
        left, right = split_lines_to_pages(sorted_lines, pages)
        left_paragraphs = split_lines_to_paragraphs(left, words, image["height"])
        right_paragraphs = split_lines_to_paragraphs(right, words, image["height"])
        image_data = image.copy()
        image_data["pages"] = []
        page_index = 0
        if len(left_paragraphs) > 0:
            page_data = dict()
            page_data["index"] = page_index
            page_index += 1
            page_data["paragraphs"] = left_paragraphs
            image_data["pages"].append(page_data.copy())
        if len(right_paragraphs) > 0:
            page_data = dict()
            page_data["index"] = page_index
            page_index += 1
            page_data["paragraphs"] = right_paragraphs
            image_data["pages"].append(page_data.copy())
        image_data = json_reformater.image_data_reformat(image_data, pages, config)
        images_data.append(image_data.copy())
        with open(os.path.join(output_folder_name, os.path.splitext(image["file_name"])[0] + ".json"), "w") as f:
            json.dump(image_data, f, indent=4, ensure_ascii=False)
        create_xml.create_xml_from_dict(image_data, os.path.join(output_folder_name, os.path.splitext(image["file_name"])[0] + ".xml"))

