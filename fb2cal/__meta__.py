__author__ = "Alessandro Digilio"
__copyright__ = "Copyright 2019-2020 Mo Beigi; fork maintained by Alessandro Digilio"
__description__ = "Fetch Facebook birthdays and export calendar/contact files"
__email__ = ""
__keywords__ = ["facebook", "birthday", "calendar", "export", "ics"]
__license__ = "GPLv3"
__maintainer__ = "Alessandro Digilio"
__status__ = "Production"
__title__ = "fb2cal"
__version_info__ = (2, 0, 0)
__version__ = ".".join(map(str, __version_info__))

__github_url__ = "https://github.com/alsd4git/fb2cal"
__github_short_url__ = __github_url__
__github_assets_absolute_url__ = (
    "https://raw.githubusercontent.com/alsd4git/fb2cal/main"
)
__download_url__ = f"https://github.com/alsd4git/fb2cal/archive/v{__version__}.tar.gz"
__upstream_url__ = "https://github.com/mobeigi/fb2cal"


# Make metadata public to script
__all__ = [
    "__author__",
    "__copyright__",
    "__description__",
    "__download_url__",
    "__email__",
    "__github_assets_absolute_url__",
    "__github_short_url__",
    "__github_url__",
    "__license__",
    "__maintainer__",
    "__status__",
    "__title__",
    "__upstream_url__",
    "__version__",
    "__version_info__",
]
