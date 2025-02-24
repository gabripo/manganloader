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
            'cbz',
        }
        Document.valid_kcc_options = {
            '--profile': {'K1', 'K11', 'K2', 'K34', 'K578', 'KDX', 'KPW', 'KV', 'KPW5', 'KO', 'KS', 'KoMT', 'KoG', 'KoGHD', 'KoA', 'KoAHD', 'KoAH2O', 'KoAO', 'KoN', 'KoC', 'KoCC', 'KoL', 'KoLC', 'KoF', 'KoS', 'KoE', 'Rmk1', 'Rmk2', 'RmkPP', 'OTHER'},
            '--manga-style': None,
            '--hq': None,
            '--two-panel': None,
            '--webtoon': None,
            '--targetsize': {100, 400},
            '--noprocessing': None,
            '--upscale': None,
            '--stretch': None,
            '--splitter': {'0', '1', '2'},
            '--gamma': {'Auto'},
            '--cropping': {'0', '1', '2'},
            '--interpanelcrop': {'0', '1', '2'},
            '--blackborders': None,
            '--whiteborders': None,
            '--forcecolor': None,
            '--forcepng': None,
            '--mozjpeg': None,
            '--maximizestrips': None,
            '--delete': None,
            '--format': {'Auto', 'MOBI', 'EPUB', 'CBZ', 'KFX', 'MOBI+EPUB'},
            '--nokepub': None,
            '--batchsplit': {'0', '1', '2'},
            '--spreadshift': None,
            '--norotate': None,
            '--reducerainbow': None,
        }
        self.kcc_options = [
            '--manga-style',
            '--upscale',
            '--profile', 'KoCC', # Kobo Clara Colour, Gabriele's manga machine
            '--format', 'EPUB',
            '--splitter', '2', # rotate
        ]
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

    def set_kcc_option(self, option_name: str, option_val: str = None):
        if option_val is None:
            if option_name in set(self.kcc_options):
                print(f"Option {option_name} already present!")
                return
            elif option_name in Document.valid_kcc_options.keys():
                self.kcc_options.append(option_name)
                print(f"Option {option_name} for KCC added!")
                return
        
        for idx, option in enumerate(self.kcc_options):
            if option == option_name and idx < len(self.kcc_options)-1:
                if option_name not in Document.valid_kcc_options.keys():
                    print(f"Invalid option {option_name} for KCC specified!")
                    return
                if option_val not in Document.valid_kcc_options[option_name]:
                    print(f"Invalid option value {option_val} for option {option_name} for KCC specified!")
                    return
                
                self.kcc_options[idx+1] = option_val
                print(f"Option {option_name} for KCC set as {option_val} !")
                return

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
            elif self.type == 'epub' or self.type == 'cbz':
                generated_doc = self._generate_ebook()
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

    def _generate_ebook(self):
        input_folder_images = self._get_common_path_images()
        self.set_kcc_option('--format', self.type.upper())
        if self._valid_kcc_options():
            comic2ebook.main([
                *self.kcc_options,
                '--output', self.output_dir,
                input_folder_images,
                ])
        
            ebook_generated = self._get_file_names_with_extension(
                self.output_dir,
                '.' + self.type,
                first_file_only=True
                )
            ebook_newname = self._new_ebook_name(ebook_generated)
            os.rename(
                ebook_generated,
                ebook_newname
            )
            print(f"Generated {self.type.upper()} file: {ebook_newname}")
            return ebook_newname
        else:
            print(f"Invalid options for KCC: no files will be generated!")
            return ''

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
    
    def _new_ebook_name(self, old_epub_name: str):
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
    
    def _valid_kcc_options(self) -> bool:
        n_options = len(self.kcc_options)
        kcc_iterator = self.kcc_options.__iter__()
        for idx, opt in enumerate(kcc_iterator):
            if opt not in Document.valid_kcc_options.keys():
                print(f"Option {opt} for KCC is invalid!")
                return False
            elif idx < n_options-1:
                valid_args_for_option = Document.valid_kcc_options[opt]
                if valid_args_for_option is not None:
                    curr_arg = kcc_iterator.__next__() # jumps the argument
                    if curr_arg not in valid_args_for_option:
                        print(f"Argument {curr_arg} for option {opt} for KCC is invalid!")
                        return False
        return True