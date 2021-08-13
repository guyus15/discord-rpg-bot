class Item:
    def __init__(self, item):
        
        self.id = item["id"]
        self.name = item["name"]
        self.command_name = item["command-name"]
        self.description = item["description"]
        self.value = item["value"]
        self.max_number = item["max-number"]
        self.action_type = item["action-type"]
        self.tool_type = item["tool-type"]
        self.weapon = item["is-weapon"]
        self.fuel = item["is-fuel"]
        self.fuel_amount = item["fuel-amount"]
        self.smeltable = item["is-smeltable"]
        self.fuel_required = item["fuel-required"] 
        self.smelted_item = item["smelted-item"]

    def get_details(self):
        return self.id, self.name, self.description, self.value, self.max_number, self.action_type, self.tool_type

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_command_name(self):
        return self.command_name

    def get_decription(self):
        return self.description

    def get_value(self):
        return self.value

    def get_max_number(self):
        return self.max_number

    def get_action_type(self):
        return self.action_type

    def get_tool_type(self):
        return self.tool_type

    def is_weapon(self):
        if self.weapon == "yes":
            return True

        return False

    def is_fuel(self):
        if self.fuel == "yes":
            return True
        
        return False

    def get_fuel_amount(self):
        # If item is fuel, this returns the amount of fuel that this item will have.
        return self.fuel_amount

    def is_smeltable(self):
        if self.smeltable == "yes":
            return True
        
        return False

    def get_fuel_required(self):
        # Returns the amount of fuel required to smelt.
        return self.fuel_required

    def get_smelted_item_id(self):
        # Returns the item id of the item which this item will smelt into.
        return self.smelted_item