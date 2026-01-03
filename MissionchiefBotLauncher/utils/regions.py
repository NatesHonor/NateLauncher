import configparser

INI_FILE = "launcher_settings.ini"

REGIONS = [
    "North America"
]

def list_regions():
    return REGIONS.copy()

def select_region(region):
    config = configparser.ConfigParser()
    config.read(INI_FILE)
    if not config.has_section("Launcher"):
        config.add_section("Launcher")
    config.set("Launcher", "region", region)
    with open(INI_FILE, "w") as f:
        config.write(f)