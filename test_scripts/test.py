import os
import import_root_path
from manganloader.docbuilder import Document

OP_TEST = True
OP_LATEST_CHAPTER = True

if __name__ == '__main__':
    if OP_TEST:
        if OP_LATEST_CHAPTER:
            chapter_title = None
            url = None
        else:
            chapter_title = "One Piece 1140 (ENG)"
            url = 'https://mangaplus.shueisha.co.jp/viewer/1023496'
    else:
        chapter_title = "One Piece 1061 colored (ENG)"
        url = 'https://ww11.readonepiece.com/index.php/chapter/one-piece-digital-colored-comics-chapter-1061/'
    doc = Document(
        name=chapter_title,
        source_url=url,
        output_dir='output_docs',
        document_type='pdf')
    
    doc.clean_working_dir()
    doc.clean_output_dir()

    doc_pdf = doc.build_from_url()
    message_pdf = f"Generated manga {os.path.basename(doc_pdf)} for {doc.get_device_name()} now available! ARRRWWW!"
    doc.set_double_spread_version(want_double_spread_version=True)
    doc.build_from_url()

    doc.set_type('epub')
    doc_epub = doc.build_from_url()
    message_epub = f"Generated manga {os.path.basename(doc_epub)} for {doc.get_device_name()} now available! ARRRWWW!"

    doc.set_type('cbz')
    doc_cbz = doc.build_from_url()
    message_cbz = f"Generated manga {os.path.basename(doc_cbz)} for {doc.get_device_name()} now available! ARRRWWW!"

    doc.set_kcc_option('--profile', 'K11')
    doc_cbz = doc.build_from_url() # file will be overwritten, CBZ files are device-agnostic
    message_cbz = f"Generated manga {os.path.basename(doc_cbz)} for {doc.get_device_name()} now available! ARRRWWW!"

    doc.set_type('epub')
    doc_epub = doc.build_from_url()
    message_epub = f"Generated manga {os.path.basename(doc_epub)} for {doc.get_device_name()} now available! ARRRWWW!"

    doc.set_type('raw')
    doc.build_from_url()

    doc.set_type('epub')
    doc.set_kcc_option('--profile', 'OBC') # OBC is a custom device, not natively supported by KCC
    doc.build_from_url()