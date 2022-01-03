from global_helpers import __version__
import random
import shutil

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2022, Martin Woelke'

# Width of the widest logo.
WIDTH_MAX = 108

SMALL_1 = "\n            _                    _        _                                 \n" \
          "  _ __  ___| |_ __ _   _ __  ___| |_ __ _| |  _ __  __ _ _ __ _ __  ___ _ _ \n" \
          " | '  \\/ -_)  _/ _` | | '  \\/ -_)  _/ _` | | | '  \\/ _` | '_ \\ '_ \\/ -_) '_|\n" \
          " |_|_|_\\___|\\__\\__,_| |_|_|_\\___|\\__\\__,_|_| |_|_|_\\__,_| .__/ .__/\\___|_|  \n" \
          f"                                                        |_|  |_|    {__version__}  \n"

SMALL_2 = "\n              __                   __       __                              \n" \
          "   __ _  ___ / /____ _  __ _  ___ / /____ _/ / __ _  ___ ____  ___  ___ ____\n" \
          "  /  ' \\/ -_) __/ _ `/ /  ' \\/ -_) __/ _ `/ / /  ' \\/ _ `/ _ \\/ _ \\/ -_) __/\n" \
          " /_/_/_/\\__/\\__/\\_,_/ /_/_/_/\\__/\\__/\\_,_/_/ /_/_/_/\\_,_/ .__/ .__/\\__/_/   \n" \
          f"                                                       /_/  /_/     {__version__}  \n" \

SMALL_3 = "\n            _                    _       _                              \n" \
          "  _____ ___| |_ ___    _____ ___| |_ ___| |   _____ ___ ___ ___ ___ ___ \n" \
          " |     | -_|  _| .'|  |     | -_|  _| .'| |  |     | .'| . | . | -_|  _|\n" \
          " |_|_|_|___|_| |__,|  |_|_|_|___|_| |__,|_|  |_|_|_|__,|  _|  _|___|_|  \n" \
          f"                                                       |_| |_| {__version__} \n"

LARGE_1 = "\n                 __                           __          __                                               \n" \
    "   _____   _____/  |______      _____   _____/  |______  |  |     _____ _____  ______ ______   ___________ \n" \
    "  /     \\_/ __ \\   __\\__  \\    /     \\_/ __ \\   __\\__  \\ |  |    /     \\\\__  \\ \\____ \\\\____ \\_/ __ \\_  __ \\\n" \
    " |  Y Y  \\  ___/|  |  / __ \\_ |  Y Y  \\  ___/|  |  / __ \\|  |__ |  Y Y  \\/ __ \\|  |_> >  |_> >  ___/|  | \\/\n" \
    " |__|_|  /\\___  >__| (____  / |__|_|  /\\___  >__| (____  /____/ |__|_|  (____  /   __/|   __/ \\___  >__|   \n" \
    f"       \\/     \\/          \\/        \\/     \\/          \\/             \\/     \\/|__|   |__|        \\/ {__version__}\n"

LARGE_2 = "\n █▀▄▀█ ▄███▄     ▄▄▄▄▀ ██       █▀▄▀█ ▄███▄     ▄▄▄▄▀ ██   █         █▀▄▀█ ██   █ ▄▄  █ ▄▄  ▄███▄   █▄▄▄▄ \n" \
    " █ █ █ █▀   ▀ ▀▀▀ █    █ █      █ █ █ █▀   ▀ ▀▀▀ █    █ █  █         █ █ █ █ █  █   █ █   █ █▀   ▀  █  ▄▀ \n" \
    " █ ▄ █ ██▄▄       █    █▄▄█     █ ▄ █ ██▄▄       █    █▄▄█ █         █ ▄ █ █▄▄█ █▀▀▀  █▀▀▀  ██▄▄    █▀▀▌  \n" \
    " █   █ █▄   ▄▀   █     █  █     █   █ █▄   ▄▀   █     █  █ ██▄       █   █ █  █ █     █     █▄   ▄▀ █  █   \n" \
    "    █  ▀███▀    ▀         █        █  ▀███▀    ▀         █     ▀        █     █  █     █    ▀███▀     █   \n" \
    "   ▀                     █        ▀                     █              ▀     █    ▀     ▀            ▀    \n" \
    f"                        ▀                              ▀                    ▀         {__version__}      \n"

# Shorter than 80 columns.
LOGOS_SMALL = [SMALL_1, SMALL_2, SMALL_3]

# A bit wider than 80...
LOGOS_LARGE = [LARGE_1, LARGE_2]

# A list with all logos.
LOGOS = LOGOS_SMALL + LOGOS_LARGE


def get_logo():
    """Randomly selects an ASCII art logo based on the terminal width. Three logos are for standard terminal widths
        of 80 columns, two are for wider terminals.

    :return: A mete metal mapper ASCII art logo.
    """
    size = shutil.get_terminal_size()
    if size[0] > WIDTH_MAX:
        index = random.randint(0, len(LOGOS) - 1)
        return LOGOS[index]
    else:
        index = random.randint(0, len(LOGOS_SMALL) - 1)
        return LOGOS_SMALL[index]
