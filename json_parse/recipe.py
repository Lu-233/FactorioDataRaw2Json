"""
    convert data.raw json data to DIY json format

    ref:
    - wiki.factorio.com/Prototype/Recipe

    json to lua table:
    - mageddo.com/tools/json-to-lua-converter


    要调整配方分解级别，如铁板不分解为铁矿，请检查和添加 parse_recipe_raw 函数中的 stop_list
    for set ingredients_raw level, such as stop in iron-plate, not iron-ore. please check stop_list in parse_recipe_raw

"""
import json
from typing import Union
from pathlib import Path

ver = "1.1.61"
data_folder = Path(f"../json_data/v_{ver}_data")


def main():
    """ main func """

    json_file = data_folder / "recipe.json"
    json_recipes = json.loads(json_file.read_text())

    # base recipe 从原始 json 中解析成 ItemRecipe 类
    recipes = {}
    for item_name, item_recipes in json_recipes.items():
        recipes[item_name] = ItemRecipe(item_recipes)

    # raw recipe 原材料
    for name, recipe in recipes.items():
        # 要分别处理普通和昂贵配方，因为即使配方不区分，其子配方也可能不同
        normal_raw = parse_recipe_raw(recipes, recipe, is_expensive=False)
        expensive_raw = parse_recipe_raw(recipes, recipe, is_expensive=True)

        if normal_raw == expensive_raw:
            recipe.ingredients_raw = normal_raw
        else:
            recipe.ingredients_raw = [normal_raw, expensive_raw]

    # recipes to dict, then can dump to json
    for name, recipe in recipes.items():
        recipes[name] = recipe.to_dict()

    json_str = json.dumps(recipes, indent=2)
    Path("parsed_recipe.json").write_text(json_str)


class ItemRecipe:
    """ item recipe
        for DIY format json
        target: easy handle recipe data with js / wiki lua
    """
    def __init__(self, recipe_data: dict = None):
        # set default value
        self.name = ""
        self.energy_required: float = 0.5
        self.category: str = "crafting"
        self.subgroup: str = ""
        self.ingredients: Union[dict, list] = {}  # list is [dict,dict], for expensive mode
        self.ingredients_raw: Union[dict, list] = {}
        self.results: Union[dict, list] = {}

        if recipe_data:
            self._from_source_recipe_dict(recipe_data)

    @property
    def has_expensive(self) -> bool:
        """ is ingredients has expensive """
        return isinstance(self.ingredients, list)

    @property
    def has_expensive_raw(self) -> bool:
        """ is ingredients_raw has expensive """
        return isinstance(self.ingredients_raw, list)

    @property
    def has_expensive_result(self) -> bool:
        """ is results has expensive, always true for now(1.1.61) """
        return isinstance(self.results, list)

    def _from_source_recipe_dict(self, recipe_data: dict):
        """ 从原始配方转换为 ItemRecipe 类 """
        # 配方名 name
        self.name = recipe_data["name"]

        # 时间 energy_required
        if "energy_required" in recipe_data:
            self.energy_required = recipe_data["energy_required"]

        # 分类 category
        if "category" in recipe_data:
            self.category = recipe_data["category"]

        # 子分类 subgroup
        if "subgroup" in recipe_data:
            self.subgroup = recipe_data["subgroup"]

        # 配方 ingredients
        if "expensive" in recipe_data:  # for normal and expensive
            normal = recipe_data["normal"]["ingredients"]
            expensive = recipe_data["expensive"]["ingredients"]
            self.ingredients = [normal, expensive]
        elif "ingredients" in recipe_data:
            self.ingredients = recipe_data["ingredients"]
        else:
            print(json.dumps(recipe_data, ensure_ascii=False, indent=4))
            raise ValueError("can not find ingredients in recipe_data")

        # result 产物，全部转换为 results dict, key=产物名 value=产量
        # case: result，results，（normal or expensive）
        if "result" in recipe_data:
            result_name = recipe_data["result"]
            if "result_count" in recipe_data:
                self.results[result_name] = recipe_data["result_count"]
            else:
                self.results[result_name] = 1
        elif "results" in recipe_data:
            for item in recipe_data["results"]:
                if "name" in item:
                    self.results[item["name"]] = item["amount"]
                else:
                    self.results[item["1"]] = item["2"]
        else:  # normal or expensive
            if "result" not in recipe_data["normal"] or "result" not in recipe_data["expensive"]:
                raise NotImplementedError("尚未支持 recipe.expensive 中带 results 或其他情况")

            # for normal
            normal_result_name = recipe_data["normal"]["result"]
            if "result_count" in recipe_data:
                normal_result_count = recipe_data["normal"]["result_count"]
            else:
                normal_result_count = 1

            normal_result = {normal_result_name: normal_result_count}

            # for expensive
            expensive_result_name = recipe_data["expensive"]["result"]
            if "result_count" in recipe_data:
                expensive_result_count = recipe_data["expensive"]["result_count"]
            else:
                expensive_result_count = 1

            expensive_result = {expensive_result_name: expensive_result_count}

            # 如果 result 相同， 保留一个即可
            if normal_result == expensive_result:
                self.results = normal_result
            else:
                self.results = [normal_result, expensive_result]

    def to_dict(self):
        """ convert class to dict, then can convert to json """
        return {
            "name": self.name,
            "energy_required": self.energy_required,
            "category": self.category,
            "results": self.results,
            "subgroup": self.subgroup,
            "ingredients": self.ingredients,
            "ingredients_raw": self.ingredients_raw,
            "has_expensive": self.has_expensive,
            "has_expensive_raw": self.has_expensive_raw,
            "has_expensive_result": self.has_expensive_result,
        }


def parse_recipe_raw(all_recipe: dict, recipe: ItemRecipe, is_expensive=False):

    # 先 copy 一份配方，不断分解最后成为原料
    if recipe.has_expensive:
        if is_expensive:
            ingredients = recipe.ingredients[1].copy()
        else:
            ingredients = recipe.ingredients[0].copy()
    else:
        ingredients = recipe.ingredients.copy()

    # 这个列表里的配方不再分解
    # 铁板钢材铜板，还有硫酸润滑油
    stop_list = ["iron-plate", "steel-plate", "copper-plate", "sulfuric-acid", "lubricant", "null"]

    # 遍历所有配方项，如果该项有配方，将该配方分解为原料
    not_done = True
    while not_done:
        # print("not done ingredients ",ingredients)

        # while 循环条件:  if any key in all_recipe
        not_done = False
        for raw_name in ingredients.keys():
            if raw_name in stop_list:  # 如果任何配方在停止列表中，忽略
                continue
            if raw_name in all_recipe:  # 如果有配方可以分解，标记 not_done 为 True
                not_done = True

        # 遍历配方， 如果有配方可以分解，就分解
        for raw_name, raw_amount in ingredients.items():
            if raw_name in stop_list:  # 如果任何配方在停止列表中，忽略
                continue
            if raw_name not in all_recipe:  # 如果当前原料没有配方，忽略
                continue

            # 分解当前物品， 即要将子配方增加到配方中
            # print("split ", raw_name)
            sub_recipe: ItemRecipe = all_recipe[raw_name]

            # 获取当前物品的子配方
            if sub_recipe.has_expensive:
                if is_expensive:
                    sub_ingredients: dict = sub_recipe.ingredients[1]
                else:
                    sub_ingredients: dict = sub_recipe.ingredients[0]
            else:
                sub_ingredients: dict = sub_recipe.ingredients

            # 获取子配方中当前物品的产量
            if sub_recipe.has_expensive_result:
                if is_expensive:
                    sub_recipe_result_amount = sub_recipe.results[1][sub_recipe.name]
                else:
                    sub_recipe_result_amount = sub_recipe.results[0][sub_recipe.name]
            else:
                sub_recipe_result_amount = sub_recipe.results[sub_recipe.name]

            # 将子配方的每一项增加到配方中
            for sub_raw_name, sub_raw_amount in sub_ingredients.items():
                if sub_raw_name == "null":
                    raise ValueError("发现配方中有 null 请检查生成的配方json是否正确。")

                # 子配方项的数量 = 配料需要数量 * 子配料需要的数量 / 子配料的产量
                amount = sub_raw_amount * raw_amount / sub_recipe_result_amount

                # 检查配方中有没有该子项，如果有就加数量，没有就新增项
                if sub_raw_name in ingredients:
                    # print("add ", sub_raw_name, sub_raw_amount, raw_amount, sub_recipe.results[sub_recipe.name])
                    ingredients[sub_raw_name] += amount
                else:
                    # print("new ", sub_raw_name, sub_raw_amount, raw_amount, sub_recipe.results[sub_recipe.name])
                    ingredients[sub_raw_name] = amount
            # print("remove ", raw_name)
            del ingredients[raw_name]
            break  # 需要 break，因为 del 改变了 dict 的 key。 多循环几次就好

    return ingredients


if __name__ == '__main__':
    main()
