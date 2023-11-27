We introduce the first Russian Handwritten dataset on paragraph level.The dataset preparation involved an extensive process leveraging Python scripts and computational methods. Initially, the source dataset—Russian school notebooks' dataset—was chosen for its content suitability and accessibility. 

The link to the source dataset: https://huggingface.co/datasets/ai-forever/school_notebooks_RU

The materials used primarily included this dataset, which contained handwritten texts from contemporary Russian student notebooks. The method involved the extraction of ground truth information initially available at the word level from the source dataset.
Through a systematic approach, this word-level data was meticulously analyzed, processed, and adapted to construct a comprehensive ground truth at the paragraph level. The procedure consisted of defining text lines, splitting the content into pages, and further segmenting the pages into paragraphs. This process was guided by a robust methodology, ensuring accurate delineation of paragraphs within the handwritten documents.

The ground truth annotations, prepared in PAGEXML format, stood as a cornerstone in this preparation process. The PAGEXML annotation format is known for providing a structured representation of the layout regions within the handwritten documents.PAGEXML provides an organized layout region explanation, offering insights into paragraph structures, text alignments, indentation, and other layout-related information. It allows for a detailed delineation of various elements within the document, such as text lines, thereby enhancing the dataset's utility for training and evaluating recognition models. 
Overall, this methodological approach allowed for the creation of a valuable dataset at the paragraph level, serving as a robust foundation for advancing research in layout-aware handwritten paragraph recognition for Russian documents.


The Dataset in PAGEXML format is available in folder Dataset_PAGE XML files.

Images could be uploaded directly from the source dataset, all filenames of the proposed dataset corresponds to the source files and can be matched directly. 

Alternatively, you can re-create the dataset by running scropt main.py with the command: 

python main.py


