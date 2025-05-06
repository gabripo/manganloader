import os
import import_root_path
from manganloader.docbuilder import Document

if __name__ == "__main__":
    images_path = os.path.abspath('/Users/gabripo/Downloads/Chainsaw Man Colored/Vol 1/Chapter 1')
    manga_name = "Chainsaw_Man"
    chapter_name = manga_name + "_" + os.path.basename(images_path).replace(" ", "_")
    doc = Document(
        name=chapter_name,
        source_url=images_path,
        output_dir='output_docs',
        document_type='pdf')
    
    doc.clean_working_dir()
    doc.clean_output_dir()

    doc.build_from_url()

    doc.set_type('epub')
    doc.set_kcc_option('--profile', 'KoCC')
    doc.set_kcc_option('--forcecolor')
    doc.build_from_url()