import json
import xml.etree.ElementTree as ET
import traceback

def add_metadata(head, metadata_dict):
  metadata = ET.SubElement(head, "Metadata")
  for key in metadata_dict.keys():
    obj = ET.SubElement(metadata, key)
    obj.text = metadata_dict[key]

def add_reading_order(head, reading_order_dict):
  reading_order = ET.SubElement(head, "ReadingOrder")
  order_group = ET.SubElement(reading_order, "OrderedGroup", id=reading_order_dict["OrderedGroup"]["_id"])
  regions = reading_order_dict["OrderedGroup"]["RegionRefIndexed"]
  for region in regions:
    ET.SubElement(order_group, "RegionRefIndexed", regionRef=region["_regionRef"],
                                       index=region["_index"])

def points_to_xml_string(points):
  points_str = ""
  for point in points:
    points_str = points_str + str(point[0]) + "," + str(point[1]) + " "
  if points_str != "":
    points_str = points_str[:-1]
  return points_str

def add_line(head, line_dict):
  # print(line_dict.keys())
  if "_custom" in line_dict.keys():
    line = ET.SubElement(head, "TextLine", id=line_dict["_id"], custom=line_dict["_custom"])
  else:
    line = ET.SubElement(head, "TextLine", id=line_dict["_id"])
  ET.SubElement(line, "Coords", points=line_dict["Coords"]["_points"])
  if ("BaseLine" in line_dict.keys()):
    ET.SubElement(line, "Baseline", points=line_dict["Baseline"]["_points"])

  text_equiv = ET.SubElement(line, "TextEquiv")
  text = ET.SubElement(text_equiv, "Unicode")
  text.text = line_dict["TextEquiv"]["Unicode"]
  # print(text.text)

def add_paragraph(head, paragraph_dict):
  paragraph = ET.SubElement(head, "TextRegion", id=paragraph_dict["_id"], custom=paragraph_dict["_custom"],
                            type=paragraph_dict["_type"])
  ET.SubElement(paragraph, "Coords", points=paragraph_dict["Coords"]["_points"])
  text_equiv = ET.SubElement(paragraph, "TextEquiv")
  text = ET.SubElement(text_equiv, "Unicode")
  text.text = paragraph_dict["TextEquiv"]["Unicode"]

  lines = paragraph_dict["TextLine"]
  if type(lines) != type(list()):
    lines = [lines]
  for line in lines:
    add_line(paragraph, line)



def add_page(head, page_dict):
  page = ET.SubElement(head, "Page", imageFilename=page_dict["_imageFilename"], imageWidth=page_dict["_imageWidth"],
                       imageHeight=page_dict["_imageHeight"])
  add_reading_order(page, page_dict["ReadingOrder"])
  paragraphs = page_dict["TextRegion"]
  if type(paragraphs) != type(list()):
    paragraphs = [paragraphs]
  for paragraph in paragraphs:
    add_paragraph(page, paragraph)

def create_xml_from_dict(dict, output_file):
  try:
    pcgts = dict["PcGts"]
    root = ET.Element('PcGts', xmlns=pcgts["_xmlns"],
                      xmlnsxsi=pcgts["_xmlns:xsi"],
                      xsischemaLocation=pcgts["_xsi:schemaLocation"])
    add_metadata(root, pcgts["Metadata"])
    add_page(root, pcgts["Page"])
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
  except Exception as e:
    print(output_file)
    print("the dict format is not suitable")
    print(traceback.format_exc())