import time
import random

from bot_info import BotInfo
from json_handler import JsonHandler
from inventory import Inventory
from item import Item
from constants import Constants

class Player:
    def __init__(self, name, user=None):
        self.name = name
        self.max_health = Constants.MAX_HEALTH
        self.max_armour = Constants.MAX_ARMOUR
        self.cooldown_duration = Constants.COOLDOWN_SECONDS

        if user == None: # Consider this as a new user.
            self.current_health = self.max_health
            self.current_armour = 0
            self.inventory = Inventory()
            wooden_axe = Item(JsonHandler.get_items()[26])
            self.inventory.add_item(wooden_axe)
            self.current_cooldown_time = time.time() - self.cooldown_duration
            self.current_fuel_amount = 0
        else:
            self.current_health = user["health"]
            self.current_armour = user["armour"]
            self.inventory = Inventory(user["inventory"])
            self.current_cooldown_time = float(user["cooldown-time"])
            self.current_fuel_amount = int(user["current-fuel-amount"])

        self.current_json = self.player_to_json()

        self.last_message_received = None
        #self.crafting_system = crafting_system

    def player_to_json(self):

        string = "{"

        string += "\"name\": \"{}\", ".format(self.name)
        string += str(self.inventory) + ", "
        string += "\"health\": {}, ".format(str(self.current_health))
        string += "\"armour\": {}, ".format(str(self.current_armour))
        string += "\"cooldown-time\": {}, ".format(str(self.current_cooldown_time))
        string += "\"current-fuel-amount\": {}".format(str(self.current_fuel_amount))

        string += "}"

        return string


    def add_health(self, amount):

        self.current_health += amount
        
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def remove_health(self, amount):

        self.current_health -= amount

        if self.current_health < 0:
            self.current_health = 0

    def set_last_received_message(self, message):
        self.last_message_received = message

    def set_cooldown_time(self):
        self.current_cooldown_time = time.time()

    def can_do_action(self):

        # Let me do this without cooldown for testing purposes.
        if "guyus" in self.name:
            return True

        if time.time() - self.current_cooldown_time >= self.cooldown_duration:
            return True
        
        return False

    def get_time_to_wait(self):
        
        time_in_seconds =  round(self.cooldown_duration - (time.time() - self.current_cooldown_time))

        if time_in_seconds // 60 > 0:
            return "{}min {}s".format(str(time_in_seconds // 60), str(time_in_seconds % 60))
        else:
            return "{}s".format(str(time_in_seconds % 60))


    def get_action_items(self, type):

        action_items = []

        for item in JsonHandler.get_items():
            if item["action-type"] == type:
                action_items.append(Item(item))

        return action_items

    def get_item_by_name(self, name):

        item_found = None

        for item in JsonHandler.get_items():
            if item["name"].lower() == name.lower():
                item_found = Item(item)

        if item_found == None:
            print("Could not find item with the name {}".format(name))
            return

        return item_found

    def get_fuel_amount(self):
        return self.current_fuel_amount

    def add_fuel(self, amount):
        self.current_fuel_amount += amount

    def remove_fuel(self, amount):
        self.current_fuel_amount -= amount

        if self.current_fuel_amount < 0:
            self.current_fuel_amount = 0

    #TODO fix this; does not work correctly
    def clear_inventory(self):

        items = self.inventory.get_items()

        for item in items:
            print("removing item {}".format(item.get_id()))
            self.inventory.remove_item(item.get_id())

        JsonHandler.save_json(self)

    def chop(self):

        can_chop = False

        for item in self.inventory.get_items():
            if item.get_tool_type() == "axe":
                can_chop = True

        if can_chop == False:
            return "**{} you cannot perform this action without an axe.**".format(BotInfo.last_message_received.author.mention)

        choppable_items = self.get_action_items("choppable")

        num_items = 0
        choice = None

        if self.can_do_action():
            choice = random.choice(choppable_items)

            for i in range(1, random.randint(2, choice.max_number)):
                num_items += 1
                self.inventory.add_item(choice)

            self.set_cooldown_time()

            JsonHandler.save_json(self)

            return "{} has chopped **{} {}**".format(BotInfo.last_message_received.author.mention, str(num_items), choice.name)
        else:
            return "{} you must wait **{}** seconds before you can do this action.".format(BotInfo.last_message_received.author.mention, str(self.get_time_to_wait()))

    def dig(self):

        can_dig = False

        for item in self.inventory.get_items():
            if item.get_tool_type() == "shovel":
                can_dig = True

        if can_dig == False:
            return "**{} you cannot perform this action without a shovel.**".format(BotInfo.last_message_received.author.mention)

        diggable_items = self.get_action_items("diggable")

        num_items = 0
        choice = None

        if self.can_do_action():
            choice = random.choice(diggable_items)

            random_value = random.randint(0, choice.max_number)

            if random_value == 0:
                random_value = 1

            for i in range(random_value):
                num_items += 1
                self.inventory.add_item(choice)

            self.set_cooldown_time()

            JsonHandler.save_json(self)

            return "{} has dug **{} {}**".format(BotInfo.last_message_received.author.mention, str(num_items), choice.name)
        else:
            return "{} you must wait **{}** seconds before you can do this action.".format(BotInfo.last_message_received.author.mention, str(self.get_time_to_wait()))

    def mine(self):

        can_mine = False

        for item in self.inventory.get_items():
            if item.get_tool_type() == "pickaxe":
                can_mine = True

        if can_mine == False:
            return "**{} you cannot perform this action without a pickaxe.**".format(BotInfo.last_message_received.author.mention)

        stone = Item.get_item_by_id("0")
        coal = Item.get_item_by_id("5")
        iron = Item.get_item_by_id("6")
        gold = Item.get_item_by_id("7")
        diamond = Item.get_item_by_id("8")

        num_items = 0
        choice = None

        if self.can_do_action():
            rand_num = random.randint(1,100)

            if rand_num < 50:
                choice = stone

                for i in range(1, random.randint(2, choice.max_number)):
                    num_items += 1
                    self.inventory.add_item(choice)
            elif rand_num < 75:
                choice = coal

                for i in range(1, random.randint(2, choice.max_number)):
                    num_items += 1
                    self.inventory.add_item(choice)
            elif rand_num < 90:
                choice = iron

                for i in range(1, random.randint(2, choice.max_number)):
                    num_items += 1
                    self.inventory.add_item(choice)
            elif rand_num < 98:
                choice = gold

                for i in range(1, random.randint(2, choice.max_number)):
                    num_items += 1
                    self.inventory.add_item(choice)
            else:
                choice = diamond

                for i in range(1, random.randint(2, choice.max_number)):
                    num_items += 1
                    self.inventory.add_item(choice)

            self.set_cooldown_time()

            JsonHandler.save_json(self)

            return "{} has mined **{} {}**".format(BotInfo.last_message_received.author.mention, str(num_items), choice.name)
        else:
            return "{} you must wait **{}** seconds before you can do this action.".format(BotInfo.last_message_received.author.mention, str(self.get_time_to_wait()))
    
    def fish(self):

        can_fish = False        

        for item in self.inventory.get_items():
            if item.get_tool_type() == "fishingrod":
                can_fish = True

        if can_fish == False:
            return "**{} you cannot perform this action without a fishing rod.**".format(BotInfo.last_message_received.author.mention)

        fishable_items = self.get_action_items("fishable")

        num_items = 0
        choice = None

        if self.can_do_action():
            choice = random.choice(fishable_items)

            for i in range(random.randint(0, choice.max_number)):
                num_items += 1
                self.inventory.add_item(choice)

            self.set_cooldown_time()

            JsonHandler.save_json(self)

            if num_items > 0:
                return "{} has caught **{} {} fish!**".format(BotInfo.last_message_received.author.mention, str(num_items), choice.name)

            return "**{} has not caught anything**".format(BotInfo.last_message_received.author.mention)   
        else:
            return "{} you must wait **{}** seconds before you can do this action.".format(BotInfo.last_message_received.author.mention, str(self.get_time_to_wait()))


    def hunt(self):
        
        can_hunt = False
        
        for item in self.inventory.get_items():
            if item.is_weapon():
                can_hunt = True

        if can_hunt == False:
            return "**{} you cannot hunt without a weapon!**".format(BotInfo.last_message_received.author.mention)

        huntable_items = self.get_action_items("huntable")
        
        choice = None
        final_string = ""

        if self.can_do_action():

            # Key = ITEM, Value = QUANTITY
            items_collected = {}

            for i in range(random.randint(1, 4)):
                choice = random.choice(huntable_items)
                
                items_collected[choice] = random.randint(1, choice.max_number)

            for item in items_collected:
                for i in range(items_collected.get(item)):
                    self.inventory.add_item(item)
                
                final_string += "- **{}**: {}\n".format(item.get_name(), items_collected.get(item))
                
            final_string += "\n" # Add some spacing in embed

            health_lost = random.choice([True, False])
            health_to_remove = None

            if health_lost:
                health_to_remove = random.randint(10, 51)
                self.remove_health(health_to_remove)

            self.set_cooldown_time()

            JsonHandler.save_json(self)

            if self.current_health <= 0:
                return self.die()
            elif health_lost:
                final_string += "\nYou were attacked on your hunting trip and have lost **{}** health.".format(health_to_remove)

            return "{} after your hunting trip you have received:\n\n{}".format(BotInfo.last_message_received.author.mention, final_string)

        else:
            return "{} you must wait **{}** seconds before you can do this action.".format(BotInfo.last_message_received.author.mention, str(self.get_time_to_wait()))


    def die(self):
        return "**{} YOU ARE DEAD IDIOT! Making funeral arrangements as we speak.**".format(BotInfo.last_message_received.author.mention)