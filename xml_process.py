import xml.dom.minidom as xml
import xml.etree.ElementTree as ET

def xml_find_paragraphs(xml_file_path):
    paragraphs = []
    xml_root = ET.parse(xml_file_path).getroot()
    # print(xml_root.tag)
    # print(xml_root.attrib)
    return paragraphs

xml_file_path = 'Train-ICFHR-2016/PublicData/Training/page/5_16.xml'
paragraphs = xml_find_paragraphs(xml_file_path)
