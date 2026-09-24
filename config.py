# ==============================================================================
# DISPLAY & VIDEO SETTINGS
# ==============================================================================
INTERNAL_WIDTH = 1920
INTERNAL_HEIGHT = 1080

DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720

FPS = 60

# ==============================================================================
# GAMEPLAY BALANCE & OPERATING HOURS
# ==============================================================================
DAY_START_HOUR = 10  # 10:00 AM
DAY_END_HOUR = 20    # 08:00 PM
MIN_CUSTOMERS_PER_DAY = 5
MAX_CUSTOMERS_PER_DAY = 7

INITIAL_MONEY = 0
INITIAL_REPUTATION = 100
DEFAULT_PATIENCE_TIME = 25.0

BASE_BOWL_PRICE = 2000
REPUTATION_GAIN = 10
REPUTATION_LOSS = 20

# ==============================================================================
# DAY PROGRESSION UNLOCK SYSTEM
# ==============================================================================
UNLOCKED_ITEMS_BY_DAY = {
    1: {"mi_kuning", "bakso_halus", "kecap"},
    2: {"mi_kuning", "bakso_halus", "kecap", "mi_bihun", "gorengan_panjang"},
    3: {
        "mi_kuning",
        "bakso_halus",
        "kecap",
        "mi_bihun",
        "gorengan_panjang",
        "tahu",
        "saos_sambal",
        "saos_tomat",
    },
    4: {
        "mi_kuning",
        "bakso_halus",
        "kecap",
        "mi_bihun",
        "gorengan_panjang",
        "tahu",
        "saos_sambal",
        "saos_tomat",
        "bawang_goreng",
        "daun_bawang",
    },
}


def get_unlocked_items(day: int) -> set[str]:
    """Returns the set of unlocked item IDs for the given day.

    For days beyond day 4, all items unlocked up to day 4 remain available.
    """
    if day <= 1:
        return set(UNLOCKED_ITEMS_BY_DAY[1])
    if day in UNLOCKED_ITEMS_BY_DAY:
        return set(UNLOCKED_ITEMS_BY_DAY[day])
    max_day = max(UNLOCKED_ITEMS_BY_DAY.keys())
    return set(UNLOCKED_ITEMS_BY_DAY[max_day])

