import json

USERS_FILE = "rpg_users.json"
ITEMS_FILE = "rpg_items.json"
RECIPES_FILE = "rpg_crafting_recipes.json"
COMMANDS_FILE = "rpg_commands.json"

class JsonHandler:
    
    @staticmethod
    def get_users():

        users_list = []

        with open(USERS_FILE, "r") as users_file:
            users = json.loads(users_file.read())["users"]

            for user in users:
                users_list.append(user)

        return users_list


    @staticmethod
    def get_items():
        
        items_list = []

        with open(ITEMS_FILE, "r") as items_file:
            items = json.loads(items_file.read())["items"]

            for item in items:
                items_list.append(item)

        return items_list


    @staticmethod
    def get_recipes():

        recipes_list = []

        with open(RECIPES_FILE, "r") as recipes_file:
            recipes = json.loads(recipes_file.read())["recipes"]

            for recipe in recipes:
                recipes_list.append(recipe)

        return recipes_list


    @staticmethod
    def get_commands():

        command_list = []

        with open(COMMANDS_FILE, "r") as commands_file:
            commands = json.loads(commands_file.read())["commands"]

            for command in commands:
                command_list.append(command)

        return command_list