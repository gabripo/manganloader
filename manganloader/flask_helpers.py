import os
import shutil
from manganloader.pages_downloader import Mangapage
from manganloader.docbuilder import batch_download_chapters
from manganloader.links import source_list

def download_chapters(
        manga: str,
        source: str,
        num_chapters: int,
        format: str,
        output_dir: str,
        device: str,
        gen_double_spread: bool,
        ):
    print(f"Manga: {manga}, Source: {source}, Num chapters to download: {num_chapters}, Format: {format}, Output folder: {output_dir}")
    source_dict = source_list.get(source, None)
    if source_dict is None:
        print("Invalid source specified! Nothing will be downloaded.")
        return
    source_colored = source_dict.pop('has_color', False)
    reverse_order = source_dict.pop('reverse_order', False)
    javascript_args_chapter = source_dict.pop('javascript_args_chapter', {})
    
    chapters_links = Mangapage.fetch_latest_chapters_generic(**source_dict)
    if len(chapters_links) < num_chapters:
        print(f"Number of chapters to download is bigger than the available ones! Only {len(chapters_links)} will be downloaded.")
    elif reverse_order:
        chapters_links = chapters_links[-num_chapters:]
    else:
        chapters_links = chapters_links[:num_chapters]

    batch_download_chapters(
        chapters_links=chapters_links,
        use_color=source_colored,
        prefix=manga,
        output_dir=output_dir,
        output_format=format,
        gen_double_spread=gen_double_spread,
        device=device,
        javascript_args_chapter=javascript_args_chapter,
        )
    
def delete_folder(folder_path):
    if os.path.isdir(folder_path):
        print(f"Deleting content of folder: {folder_path}")
        shutil.rmtree(folder_path, ignore_errors=True)