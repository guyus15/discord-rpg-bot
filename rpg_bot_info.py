
class BotInfo:
    current_player = None
    last_message_received = None
    crafting_system = None

    @classmethod
    def set_current_player(cls, player):
        cls.current_player = player

    @classmethod
    def set_last_message(cls, message):
        cls.last_message_received = message

    @classmethod
    def set_crafting_system(cls, system):
        cls.crafting_system = system
