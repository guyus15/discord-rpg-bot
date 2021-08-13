import json

users_file = "rpg_users.json"
items_file = "rpg_items.json"
recipes_file = "rpg_crafting_recipes.json"
commands_file = "rpg_commands.json"

class JsonHandler:
    @staticmethod
    def get_users():
        users = json.loads(open(users_file, "r").read())["users"]

        users_list = []

        for user in users:
            users_list.append(user)

        return users_list

    @staticmethod
    def get_items():
        items = json.loads(open(items_file, "r").read())["items"]

        items_list = []

        for item in items:
            items_list.append(item)

        return items_list

    @staticmethod
    def get_recipes():
        recipes = json.loads(open(recipes_file, "r").read())["recipes"]

        recipes_list = []

        for recipe in recipes:
            recipes_list.append(recipe)

        return recipes_list

    @staticmethod
    def get_commands():
        commands = json.loads(open(commands_file, "r").read())["commands"]

        commands_list = []

        for command in commands:
            commands_list.append(command)

        return commands_list