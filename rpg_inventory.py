import json
from rpg_json_handler import JsonHandler
from rpg_item import Item

class Inventory:
    def __init__(self, player_inventory = None):
        self.items = []
        
        if player_inventory != None:
            # Create items from the items within the JSON file.
            for item in player_inventory:
                new_item  = self.find_item(item["id"])

                if new_item != None:
                    for i in range(item["amount"]):
                        self.items.append(new_item)

    def add_item(self, item):
        # Handle adding items here
        self.items.append(item)

    def remove_item(self, id):
        # Handle removing item here

        item_to_remove = None

        for item in self.items:
            if item.get_id() == id:
                item_to_remove = item

        if item_to_remove == None:
            return

        self.items.remove(item_to_remove)

    def get_items(self):
        return self.items

    def get_items_dict(self):
        items_dict = {}

        for item in self.items:
            if item.get_id() in items_dict:
                items_dict[item.get_id()] += 1
            else:
                items_dict[item.get_id()] = 1
        
        return items_dict


    def find_item(self, id):
        for item_lookup in JsonHandler.get_items():
            if item_lookup["id"] == id:
                return Item(item_lookup)

    def __str__(self):

        items_dict = self.get_items_dict()

        string = "\"inventory\": ["

        if len(items_dict) > 0:
            for item in items_dict:
                string += "{"
                string += "\"id\": \"{}\", \"amount\": {}".format(item, items_dict.get(item))
                string += "}, "

            string = string[:-2] # Removing excess comma and space

        string += "]"

        return string
