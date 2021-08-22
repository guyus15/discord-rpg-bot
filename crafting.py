from bot_info import BotInfo
from item import Item
from json_handler import JsonHandler

class CraftingSystem:

    @staticmethod
    def get_craftable_items():

        has_crafting_table = False

        craftable_items = []
        unique_items = {}

        for item in BotInfo.current_player.inventory.get_items():

            if item.get_tool_type() == "crafting-table":
                has_crafting_table = True

            if item.get_id() in unique_items:
                unique_items[item.get_id()] += 1
            else:
                unique_items[item.get_id()] = 1 

        for recipe in JsonHandler.get_recipes():
            valid_recipe = True
            num_can_make = 0
            current_items = unique_items.copy()
            unique_recipe_items = {}

            if recipe["craft-required"] != "none":
                if recipe["craft-required"] == "table" and not has_crafting_table:
                    valid_recipe = False

            for recipe_item in recipe["required-items"]:
                if recipe_item["id"] in unique_recipe_items:
                    unique_recipe_items[recipe_item["id"]] += 1
                else:
                    unique_recipe_items[recipe_item["id"]] = 1

            for recipe_item in unique_recipe_items:
                if valid_recipe == False:
                    break
                elif recipe_item not in unique_items:
                    valid_recipe = False
                    break
                elif unique_recipe_items[recipe_item] > unique_items[recipe_item]:
                    valid_recipe = False
                    break

            can_craft = True

            if valid_recipe:

                while can_craft:

                    for recipe_item in unique_recipe_items:
                        if recipe_item not in current_items:
                            can_craft = False
                            break
                        elif current_items[recipe_item] < 0:
                            can_craft = False
                            break
                        elif current_items[recipe_item] < unique_recipe_items[recipe_item]:
                            can_craft = False
                            break
                    
                    if can_craft == False:
                        break 

                    num_can_make += 1

                    current_items[recipe_item] -= unique_recipe_items.get(recipe_item)

                craftable_item = {}

                craftable_item["id"] = recipe["id"]
                craftable_item["name"] = recipe["name"]
                craftable_item["quantity"] = num_can_make
                craftable_item["command-name"] = recipe["command-name"]

                craftable_items.append(craftable_item)

        return craftable_items


    @staticmethod
    def craft_item(command_name, amount = None):

        command_name = command_name.lower().strip()

        craft_item_found = False
        craft_item = None

        for item in JsonHandler.get_recipes():
            if item["command-name"] == command_name:
                craft_item_found = True
                break

        if not craft_item_found:
            return f"**{BotInfo.last_message_received.author.mention} could not find an item with the name `{command_name}`.**"

        items_can_craft = []

        for recipes_item in JsonHandler.get_recipes():
            for item in CraftingSystem.get_craftable_items():
                if recipes_item["id"] == item["id"]:
                    recipes_item["quantity"] = item["quantity"]
                    items_can_craft.append(recipes_item)

        for item in items_can_craft:
            if item["command-name"] == command_name:
                craft_item = item
                break

        if not craft_item is None:

            print("Craft item!: {}".format(craft_item))

            # The amount of times to craft an item
            loop_amount = 1

            if not amount is None:
                if not amount.isnumeric():
                    return f"**{BotInfo.last_message_received.author.mention} the amount of items specified was not a valid number.**"

                elif int(amount) <= 0:
                    return f"**{BotInfo.last_message_received.author.mention} the amount specified must be a positive number.**"

                elif int(amount) > craft_item["quantity"]:
                    return f"**{BotInfo.last_message_received.author.mention} you do not have enough resources to craft this many items.**"
                
                else:
                    loop_amount = int(amount)

            for i in range(loop_amount):
                for item in craft_item["required-items"]:
                    BotInfo.current_player.inventory.remove_item(item["id"])

                item_to_add = None

                item_to_add = Item.get_item_by_id(craft_item["id"])

                if item_to_add is None:
                    print("Could not find the crafted item in the items list.")
                    return "This is broken. Inform my master Guigger"

                BotInfo.current_player.inventory.add_item(item_to_add)
                    
            JsonHandler.save_json(BotInfo.current_player)

            if loop_amount > 1:
                return "{} you have successfully crafted **{} {}s**".format(BotInfo.last_message_received.author.mention, str(loop_amount), craft_item["name"])
            else:
                return "{} you have successfully crafted **{}**".format(BotInfo.last_message_received.author.mention, craft_item["name"])

        else:
            return "**{} you do not have the resources to craft this item.**".format(BotInfo.last_message_received.author.mention)


    @staticmethod
    def get_smeltable_items():

        smeltable_items = {}

        for item in BotInfo.current_player.inventory.get_items():
            
            if item.is_smeltable():
                if item.get_id() in smeltable_items:
                    smeltable_items[item.get_id()] += 1
                else:
                    smeltable_items[item.get_id()] = 1

        return smeltable_items



    @staticmethod
    def smelt_item(command_name, amount = None):
        
        can_smelt = False

        for item in BotInfo.current_player.inventory.get_items():
            if item.get_tool_type() == "furnace":
                can_smelt = True
                break

        if not can_smelt:
            return "**{} you cannot perform this action without a furnace.**".format(BotInfo.last_message_received.author.mention)

        command_name = command_name.lower().strip()

        smelt_item_found = False
        smelt_item = None

        for item in JsonHandler.get_items():
            if item["command-name"] == command_name and item["is-smeltable"] == "yes":
                smelt_item_found = True
                break

        if not smelt_item_found:
            return f"**{BotInfo.last_message_received.author.mention} could not find a smeltable item with the name `{command_name}`.**"

        for smeltable_item in CraftingSystem.get_smeltable_items():

            current_item = Item.get_item_by_id(smeltable_item)

            if current_item.command_name == command_name:
                smelt_item = current_item
                break

        if not smelt_item is None:

            # The amount of times to smelt an item
            loop_amount = 1

            if not amount is None:
                if not amount.isnumeric():
                    return f"**{BotInfo.last_message_received.author.mention} the amount of items specified was not a valid number.**"

                elif int(amount) <= 0:
                    return f"**{BotInfo.last_message_received.author.mention} the amount specified must be a positive number.**"
                
                elif int(amount) > BotInfo.current_player.get_fuel_amount() // smelt_item.get_fuel_required():
                    return f"**{BotInfo.last_message_received.author.mention} you do not have enough resources to smelt this many items.**"
                    
                else:
                    loop_amount = int(amount)

            for i in range(loop_amount):

                if smelt_item.get_fuel_required() > BotInfo.current_player.get_fuel_amount():
                    return f"**{BotInfo.last_message_received.author.mention} you do not have enough fuel to smelt this item.**"

                item_to_add = Item.get_item_by_id(smelt_item.get_smelted_item_id())

                BotInfo.current_player.inventory.add_item(item_to_add)

                BotInfo.current_player.remove_fuel(smelt_item.get_fuel_required())

                BotInfo.current_player.inventory.remove_item(smelt_item.get_id())

            JsonHandler.save_json(BotInfo.current_player)
        
            if loop_amount > 1:
                return "{} you have successfully smelted **{} {}** into **{}**".format(BotInfo.last_message_received.author.mention, str(loop_amount), smelt_item.get_name(), item_to_add.get_name())
            else:
                return "{} you have successfully smelted **{}** into **{}**".format(BotInfo.last_message_received.author.mention, smelt_item.get_name(), item_to_add.get_name())
        else:
            return "**{} you do not have the resources to smelt this item.**".format(BotInfo.last_message_received.author.mention)


    @staticmethod
    def get_fuel_items():

        fuel_items = {}

        for item in BotInfo.current_player.inventory.get_items():
            if item.is_fuel():
                if item.get_id() in fuel_items:
                    fuel_items[item.get_id()] += 1
                else:
                    fuel_items[item.get_id()] = 1

        print("Fuel items {}".format(fuel_items))
        return fuel_items


    @staticmethod
    def add_fuel(command_name, amount=None):

        command_name = command_name.lower().strip()

        fuel_item_found = False
        fuel_item = None

        for item in JsonHandler.get_items():
            if item["command-name"] == command_name and item["is-fuel"] == "yes":
                fuel_item_found = True
                break

        if not fuel_item_found:
            return f"**{BotInfo.last_message_received.author.mention} could not find a fuel item with the name `{command_name}`.**"

        for item in CraftingSystem.get_fuel_items():

            current_fuel_item = Item.get_item_by_id(item)

            if current_fuel_item.get_command_name() == command_name:
                fuel_item = item
                break


        if not fuel_item is None:

             # The amount of times to craft an item
            loop_amount = 1

            if not amount is None:
                if not amount.isnumeric():
                    return f"**{BotInfo.last_message_received.author.mention} the amount of items specified was not a valid number.**"

                elif int(amount) <= 0:
                    return f"**{BotInfo.last_message_received.author.mention} the amount specified must be a positive number.**"

                elif int(amount) > CraftingSystem.get_fuel_items()[fuel_item]:
                    return f"**{BotInfo.last_message_received.author.mention} you do not have enough resources to craft this many items.**"
                
                else:
                    loop_amount = int(amount)

            for i in range(loop_amount):

                item_to_add = Item.get_item_by_id(fuel_item)

                BotInfo.current_player.add_fuel(item_to_add.get_fuel_amount())
                BotInfo.current_player.inventory.remove_item(item_to_add.get_id())

            JsonHandler.save_json(BotInfo.current_player)

            if loop_amount > 1:
                return "{} you have successfully added **{} {}** to your fuel".format(BotInfo.last_message_received.author.mention, str(loop_amount), item_to_add.get_name())
            else:
                return "{} you have successfully added **{}** to your fuel".format(BotInfo.last_message_received.author.mention, item_to_add.get_name())
        
        else:
            return "**{} you do not have the resources to add this item to your fuel.**".format(BotInfo.last_message_received.author.mention)


    @staticmethod
    def get_item_command_name(id):

        for item in JsonHandler.get_recipes():
            if item["id"] == str(id):
                return item["command"]