import os
from functools import partial
from mloader.exporter import RawExporter, CBZExporter
from mloader.loader import MangaLoader

class MloaderWrapper:
    def __init__(self, output_directory: str = None):
        self.raw = True
        self.out_dir = None
        self.add_chapter_title = True
        self.add_chapter_subdir = True
        self.quality = "super_high"
        self.split = True
        self.begin = 0
        self.end = float('inf')
        self.last = True

        self.set_output_directory(output_directory)
        exporter = RawExporter if self.raw else CBZExporter
        self.exporter = partial(
            exporter,
            destination=self.out_dir,
            # add_chapter_title=self.add_chapter_title,
            # add_chapter_subdir=self.add_chapter_subdir,
        )

        self.loader = MangaLoader(
            self.exporter,
            self.quality,
            self.split,
            )
        
    def set_output_directory(self, output_directory: str):
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        self.out_dir = os.path.abspath(output_directory)

    def download_chapters(self, chapters: list[int] | int):
        if type(chapters) == int:
            chapters = [chapters]

        self.loader.download(
            chapter_ids=chapters,
            min_chapter=self.begin,
            max_chapter=self.end,
            last_chapter=self.last,
        )

        return self.scan_folder_for_images(self.out_dir)

    @staticmethod
    def scan_folder_for_images(folder: str):
        image_extensions = {'.jpg', '.jpeg'}
        image_paths = []
        for root, _, files in os.walk(folder):
            for file in files:
                extension = os.path.splitext(file)[1].lower()
                if extension in image_extensions:
                    image_paths.append(os.path.join(root, file))
        return image_paths