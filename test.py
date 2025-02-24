import re
import os
from manganloader.docbuilder import Document

if __name__ == '__main__':
    chapter_title = "One Piece 1140 (ENG)"
    chapter_number = re.search(r'\d+', chapter_title).group()
    doc = Document(
        chapter_nunber=chapter_number,
        name=chapter_title,
        source_url='https://mangaplus.shueisha.co.jp/viewer/1023496',
        output_dir='output_docs',
        document_type='pdf')
    doc_pdf = doc.build_from_url()
    doc_pdf_name = os.path.basename(doc_pdf)
    message_pdf = f"Generated manga {doc_pdf_name} now available! ARRRWWW!" # TODO insert link in the message

    doc.set_type('epub')
    doc_epub = doc.build_from_url()
    doc_epub_name = os.path.basename(doc_epub)
    doc.clean_working_dir()