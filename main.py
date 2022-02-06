import json
import shutil
import sys
from pathlib import Path
from lupa import LuaRuntime

from tool import table2dict

def main():
    # get arg
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        version = "1.1.53"

    # check folder
    data_folder = Path(f"version_data/{version}")

    if not data_folder.exists():
        print(f"can not find data folder {data_folder}")
        exit(0)

    # fake to lua
    fake4lua(data_folder)

    # get data
    data: dict = get_data_raw(data_folder)

    # output and finish
    Path("json_data").mkdir(exist_ok=True)
    out_file = Path(f"json_data/v_{version}_data.json")
    out_file.write_text(json.dumps(data), encoding="UTF8")


    out_folder = Path(f"json_data/v_{version}_data")
    out_folder.mkdir(exist_ok=True)
    for key, value in data.items():
        out_file = out_folder / f"{key}.json"
        out_file.write_text(json.dumps(value), encoding="UTF8")

    # To reduce file size, discard some data
    # save json without noise-expression and optimized-particle
    try:
        del data["noise-expression"]
        del data["optimized-particle"]
    except KeyError:
        pass
    out_file = Path(f"json_data/v_{version}_data_part.json")
    out_file.write_text(json.dumps(data), encoding="UTF8")


def fake4lua(data_folder):
    if not (data_folder/"__base__").exists():
        shutil.copytree(data_folder/"base", data_folder/"__base__")

    missing_folder = data_folder/"__base__"/"menu-simulations"
    missing_folder.mkdir(exist_ok=True)
    fake_file = missing_folder / "menu-simulations.lua"
    fake_file.write_text("""
        local menu_simulations = {}
        menu_simulations.forest_fire = {}
        menu_simulations.solar_power_construction = {}
        menu_simulations.lab = {}
        menu_simulations.burner_city = {}
        menu_simulations.mining_defense = {}
        menu_simulations.biter_base_steamrolled = {}
        menu_simulations.biter_base_spidertron = {}
        menu_simulations.biter_base_artillery = {}
        menu_simulations.biter_base_player_attack = {}
        menu_simulations.biter_base_laser_defense = {}
        menu_simulations.artillery = {}
        menu_simulations.train_junction = {}
        menu_simulations.oil_pumpjacks = {}
        menu_simulations.oil_refinery = {}
        menu_simulations.early_smelting = {}
        menu_simulations.train_station = {}
        menu_simulations.logistic_robots = {}
        menu_simulations.nuclear_power = {}
        menu_simulations.chase_player = {}
        menu_simulations.big_defense = {}
        menu_simulations.brutal_defeat = {}
        menu_simulations.spider_ponds = {}
        return menu_simulations
    """)


def get_data_raw(data_path):
    lua = LuaRuntime()

    data_path = str(data_path).replace("\\", "/")
    get_data = lua.eval(f"""
    function()
        package.path = "{data_path}/?.lua;" .. package.path 
        package.path = "{data_path}/core/lualib/?.lua;" .. package.path 

        package.path = "{data_path}/core/?.lua;" .. package.path 
        package.path = "{data_path}/__base__/?.lua;" .. package.path 
    """ + """
        function math.pow(a, b)
            return a ^ b
        end
        defines = {
            direction = {east=2,north=0,northeast=1,northwest=7,south=4,southeast=3,southwest=5,west=6},
            difficulty_settings = {recipe_difficulty={expensive=1,normal=0},technology_difficulty={expensive=1,normal=0}},
        }
        require "util"
        require "dataloader"
        require "prototypes.noise-programs"
        require "core.data"
        require "__base__.data"  
        require "__base__.data-updates"  
        return data
    end
    """)
    data = get_data()

    return table2dict(data["raw"])


if __name__ == '__main__':
    main()