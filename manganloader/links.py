source_list = {
    'mangaplus': {
        'url': 'https://jumpg-webapi.tokyo-cdn.com/api/title_detailV3?title_id=100020',
        'base_url': None,
        'has_color': False,
        'reverse_order': True,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        },
    'readonepiece': {
        'url': 'https://ww11.readonepiece.com/index.php/manga/one-piece-digital-colored-comics/',
        'base_url': 'https://ww11.readonepiece.com/index.php/chapter/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'url_removal',
            'url_to_remove': 'https://ww11.readonepiece.com/index.php/chapter/one-piece-digital-colored-comics-chapter-',
            },
        },
    'dbsmanga_bw': {
        'url': 'https://ww9.dbsmanga.com/manga/dragon-ball-super/',
        'base_url': 'https://ww9.dbsmanga.com/chapter/',
        'has_color': False,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'url_removal',
            'url_to_remove': 'https://ww9.dbsmanga.com/chapter/dragon-ball-super-chapter-',
            },
        },
    'dbsmanga_col': {
        'url': 'https://ww9.dbsmanga.com/manga/dragon-ball-super-colored/',
        'base_url': 'https://ww9.dbsmanga.com/chapter/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'url_removal',
            'url_to_remove': 'https://ww9.dbsmanga.com/chapter/dragon-ball-super-colored-chapter-',
            },
        },
    'weebcentral_dbs_col': {
        'url': 'https://weebcentral.com/series/01J76XYEWEQKT8DFAMV2S1Z883/Dragon-Ball-Super-Color',
        'base_url': 'https://weebcentral.com/chapters/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {
            'buttons': ['Show All Chapters'],
        },
        'javascript_args_chapter': {
            'scrolls': 2,
        },
        },
    'mangatoto_dbs_col': {
        'url': 'https://mangatoto.net/title/86383',
        'base_url': 'https://mangatoto.net/title/86383-dragon-ball-super-digital-colored-official-tl-overlaid/',
        'has_color': True,
        'reverse_order': True,
        'javascript_args_mainpage': {
            'buttons_xpath': ['/html/body/div/main/div[3]/astro-island/div/div[1]/div[1]/span'],
        },
        'javascript_args_chapter': {
            'buttons': ['load all pages'],
        },
        'naming_strategy': {
            'strategy': 'from_substring',
            'start_substring': 'vol',
            },
        },
    'mangareader_dbs_col': {
        'url': 'https://mangareader.to/dragon-ball-super-color-edition-55928',
        'base_url': 'https://mangareader.to/read/dragon-ball-super-color-edition-55928/en/chapter',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {
            'dummy': [],
        },
        'javascript_args_chapter': {
            'buttons_xpath': [
                "/html/body/div[1]/div[4]/div/div[1]/div/div[3]/a[1]", # Vertical Follow
                "/html/body/div[1]/div[1]/div/div[1]/div[3]/div[2]", # Settings
                "/html/body/div[1]/div[3]/div/div/div[1]/div[3]/button", # Quality
                "/html/body/div[1]/div[3]/div/div/div[1]/div[3]/div/a[1]", # High
            ],
            'scrolls': 2,
        },
        'naming_strategy': {
            'strategy': 'url_removal',
            'url_to_remove': 'https://mangareader.to/read/dragon-ball-super-color-edition-55928/en/chapter-',
            },
        },
    'mangaberri_dbs_col': {
        'url': 'https://mangaberri.com/dbs-colored-manga',
        'base_url': 'https://mangaberri.com/dbs-colored-manga/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {
            "dummy": [],
        },
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'from_webpage',
            'css_selector': 'span.text.default.normal'
        }
        },
    'mangaberri_chainsaw_bw': {
        'url': 'https://mangaberri.com/chainsaw-man-manga',
        'base_url': 'https://mangaberri.com/chainsaw-man-manga/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {
            "dummy": [],
        },
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'from_webpage',
            'css_selector': 'span.text.default.normal'
        }
        },
    'zbato_hxh_col': {
        'url': 'https://zbato.org/title/174873',
        'base_url': 'https://zbato.org/title/174873-hunter-x-hunter-official-colored-pzg/',
        'has_color': True,
        'reverse_order': True,
        'javascript_args_mainpage': {
            'buttons_xpath': ['/html/body/div/main/div[3]/astro-island/div/div[1]/div[1]/span'],
        },
        'javascript_args_chapter': {
            'buttons': ['load all pages'],
        },
        'naming_strategy': {
            'strategy': 'from_substring',
            'start_substring': 'vol',
            },
    },
    'kaiju_no_8_bw': {
        'url': 'https://kaiju-no-8manga.com/',
        'base_url': 'https://kaiju-no-8manga.com/manga/',
        'has_color': False,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        'naming_strategy': {
            'strategy': 'url_removal',
            'url_to_remove': 'https://kaiju-no-8manga.com/manga/kaiju-no-8-chapter-',
            },
        },
}