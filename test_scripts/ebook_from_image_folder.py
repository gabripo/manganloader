import os
import import_root_path
from manganloader.docbuilder import Document

if __name__ == "__main__":
    manga_name = "Chainsaw_Man"
    manga_root = os.path.abspath('/Users/gabripo/Downloads/Chainsaw Man Colored')
    for dirpath, dirnames, filenames in os.walk(manga_root):
        if len(dirnames) == 0:
            # maximum depth reached, meaning only files are present
            chapter_name = manga_name + "_" + os.path.basename(dirpath).replace(" ", "_")
            doc = Document(
                name=chapter_name,
                source_url=dirpath,
                output_dir='output_docs',
                document_type='pdf')
            
            doc.clean_working_dir()
            # doc.clean_output_dir()

            # doc.build_from_url() # pdf generation

            doc.set_type('epub')
            doc.set_kcc_option('--profile', 'KoCC')
            doc.set_kcc_option('--forcecolor')
            doc.build_from_url()