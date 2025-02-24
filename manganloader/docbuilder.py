import os
import shutil
from PIL import Image
from manganloader.pages_downloader import Mangapage
from kcc.kindlecomicconverter import comic2ebook

class Document:
    def __init__(
            self,
            chapter_nunber: int,
            name: str = None,
            source_url: str = None,
            output_dir: str = None,
            working_dir: str = None,
            document_type: str = 'pdf'
            ):
        self.name = None
        self.source_url = None
        self.type = None
        self.supported_types = {
            'pdf',
            'epub',
        }
        self.output_dir = None
        self.working_dir = None
        self.chapter_number = str(chapter_nunber)
        self.images = None
        self.set_name(name)
        self.set_url(source_url)
        self.set_type(document_type)
        self.set_output_dir(output_dir)
        self.set_working_dir(working_dir)
    
    def set_url(self, url: str) -> None:
        if url is None or not Mangapage.is_valid_url(url):
            print("Invalid URL!")
            return
        self.source_url = url

    def set_type(self, document_type: str) -> None:
        if self._is_supported_type(document_type):
            self.type = document_type
        else:
            print(f"Type {document_type} not supported for the {self.__class__.__name__} class!")

    def set_output_dir(self, output_dir: str):
        if output_dir is None:
            print("Invalid output directory specified!")
            return
        self.output_dir =os.path.abspath(output_dir)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def set_working_dir(self, working_dir: str):
        if working_dir is None:
            self.working_dir = os.path.abspath(os.path.join(os.getcwd(), "temp"))
            print(f"Working directory not specified, using {self.working_dir} ...")
        
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

    def set_name(self, name: str):
        if name is None:
            print("Invalid name for the manga!")
            return
        self.name = name
    
    def get_supported_types(self):
        return self.supported_types

    def build_from_url(self):
        if self._is_supported_type(self.type):
            page = Mangapage(self.source_url)
            self.images = page.fetch_images(self.working_dir)

            print(f"Generating {self.type} document from {self.source_url}...")
            if self.type == 'pdf':
                generated_doc = self._generate_pdf()
            elif self.type == 'epub':
                generated_doc = self._generate_epub()
            print(f"{self.type.upper()} document generation concluded: created file is {generated_doc}!")
            return generated_doc
        else:
            print(f"Unsupported type for the {self.__class__.__name__} class, no documents will be generated")
            return None

    def clean_working_dir(self):
        print(f"Cleaning working directory {self.working_dir}...")
        shutil.rmtree(self.working_dir)
        print(f"Working directory {self.working_dir} cleaned!")

    def _is_supported_type(self, type: str) -> bool:
        return type in self.supported_types
    
    def _generate_pdf(self):
        images = []
        self.images.sort() # assuming naming convention in increasing order for pages
        for img_path in self.images:
            try:
                img = Image.open(img_path)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                images.append(img)
            except Exception as exc:
                print(f"Skipping {img_path} with exception: {exc}")
        
        if images:
            pdf_name = self._new_pdf_name()
            images[0].save(
                pdf_name,
                save_all = True,
                append_images=images[1:],
                resolution=100.0,
            )
            print(f"Generated PDF file: {pdf_name}")
            return pdf_name
        else:
            print("No images available to generate the PDF!")
            return ''

    def _generate_epub(self):
        input_folder_images = self._get_common_path_images()
        comic2ebook.main([
            '--manga-style',
            '--upscale',
            '--profile', 'KoCC', # Kobo Clara Colour, Gabriele's manga machine
            '--format', 'EPUB',
            '--splitter', '2', # rotate
            '--output', self.output_dir,
            input_folder_images,
            ])
        
        epub_generated = self._get_file_names_with_extension(self.output_dir, '.epub', first_file_only=True)
        epub_newname = self._new_epub_name(epub_generated)
        os.rename(
            epub_generated,
            epub_newname
        )
        print(f"Generated EPUB file: {epub_newname}")
        return epub_newname

    def _new_pdf_name(self):
        doc_name = "MANGANAME" if self.name is None else self.name
        return os.path.abspath(os.path.join(
            self.output_dir,
            doc_name + ".pdf"
        ))

    def _get_common_path_images(self):
        return os.path.commonpath(self.images)
    
    def _get_file_names_with_extension(
            self,
            folder: str,
            extension: str,
            first_file_only: False):
        files_with_extension = []
        if not os.path.exists(folder):
            print(f"Invalid folder where to search files: {folder}")
        else:
            for file in os.listdir(folder):
                if file.endswith(extension):
                    full_file_path = os.path.abspath(os.path.join(folder, file))
                    if first_file_only:
                        return full_file_path
                    else:
                        files_with_extension.append(full_file_path)
        return files_with_extension
    
    def _new_epub_name(self, old_epub_name: str):
        doc_name = "MANGANAME" if self.name is None else self.name
        extensions = self._extract_extensions(old_epub_name)
        return os.path.abspath(os.path.join(
            self.output_dir,
            doc_name + "".join(extensions),
        ))
    
    @staticmethod
    def _extract_extensions(filename: str):
        extensions = []
        while True:
            filename, ext = os.path.splitext(filename)
            if not ext:
                break
            extensions.append(ext)
        
        return [s for s in reversed(extensions)]