import json
from os import cpu_count

from constants import Constants

class JsonHandler:
    
    @staticmethod
    def get_users():

        users_list = []

        with open(Constants.USERS_FILE, "r") as users_file:
            users = json.loads(users_file.read())["users"]

            for user in users:
                users_list.append(user)

        return users_list


    @staticmethod
    def get_items():
        
        items_list = []

        with open(Constants.ITEMS_FILE, "r") as items_file:
            items = json.loads(items_file.read())["items"]

            for item in items:
                items_list.append(item)

        return items_list


    @staticmethod
    def get_recipes():

        recipes_list = []

        with open(Constants.RECIPES_FILE, "r") as recipes_file:
            recipes = json.loads(recipes_file.read())["recipes"]

            for recipe in recipes:
                recipes_list.append(recipe)

        return recipes_list

    @staticmethod
    def save_json(player):

        file_read = open(Constants.USERS_FILE, "r").read()
        file_read = file_read.replace(player.current_json, player.player_to_json())

        with open(Constants.USERS_FILE, "w+") as file:
            file.write(file_read)   

        player.current_json = player.player_to_json()     