import re
import os
from manganloader.docbuilder import Document

if __name__ == '__main__':
    chapter_title = "One Piece 1140 (ENG)"
    chapter_number = re.search(r'\d+', chapter_title).group()
    url = 'https://mangaplus.shueisha.co.jp/viewer/1023496'
    doc = Document(
        chapter_nunber=chapter_number,
        name=chapter_title,
        source_url=url,
        output_dir='output_docs',
        document_type='pdf')
    
    doc.clean_working_dir()
    doc.clean_output_dir()

    doc_pdf = doc.build_from_url()
    doc_pdf_name = os.path.basename(doc_pdf)
    message_pdf = f"Generated manga {doc_pdf_name} now available! ARRRWWW!"

    doc.set_type('epub')
    doc_epub = doc.build_from_url()
    doc_epub_name = os.path.basename(doc_epub)
    message_epub = f"Generated manga {doc_epub_name} now available! ARRRWWW!"

    doc.set_type('cbz')
    doc_cbz = doc.build_from_url()
    doc_cbz_name = os.path.basename(doc_cbz)
    message_epub = f"Generated manga {doc_cbz_name} now available! ARRRWWW!"

    doc.set_kcc_option('--profile', 'K11')
    doc.build_from_url() # file will be overwritten, CBZ files are device-agnostic
    doc.set_type('epub')
    doc.build_from_url()