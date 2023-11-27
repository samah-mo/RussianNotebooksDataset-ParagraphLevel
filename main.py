from huggingface_hub import hf_hub_download
from parse_annotations import parse_annotations
import os
import shutil
import zipfile

def download_school_notebooks_datasets(config):
    files_names = [config["images_file_name"]]
    files_names.extend(config["json_files"])
    for file_name in files_names:
        hf_hub_download(repo_id=config["repository"], filename=file_name, repo_type="dataset",
                        local_dir=config["download_dir"], revision=config["revision"])

def process_dataset(config):

    with zipfile.ZipFile(os.path.join(config["download_dir"], config["images_file_name"]), 'r') as zip_ref:
        zip_ref.extractall(config["download_dir"])

    for annotations_json_file in config["json_files"]:
        json_file = os.path.join(config["download_dir"], annotations_json_file)

        if "train" in annotations_json_file.lower():
            config["output_sub_folder"] = os.path.join(config["output_folder_name"], "train")
        elif "test" in annotations_json_file.lower():
            config["output_sub_folder"] = os.path.join(config["output_folder_name"], "test")
        elif "val" in annotations_json_file.lower():
            config["output_sub_folder"] = os.path.join(config["output_folder_name"], "val")
        else:
            config["output_sub_folder"] = os.path.join(config["output_folder_name"], "other")

        parse_annotations(json_file, config)

    shutil.rmtree(os.path.join(config["download_dir"], "images"))
    shutil.rmtree(os.path.join(config["download_dir"], "__MACOSX"))

if __name__ == '__main__':
    config = {
    "repository": "ai-forever/school_notebooks_RU",
    "revision": "a10cd26104f054dc116a9dbc4a29c34b494eb9ae",
    "download_dir": "school_notebook",
    "images_file_name": "images.zip",
    "json_files": ["annotations_val.json", "annotations_test.json", "annotations_train.json"],
    "output_folder_name": "Russian_notebooks_paragraph/",
    "draw_on_image_flag": False,

    }
    download_school_notebooks_datasets(config)

    process_dataset(config)