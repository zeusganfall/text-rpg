class Character:
    def __init__(self, name, hp=0, attack_power=0, inventory=None):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.inventory = inventory if inventory is not None else []

    def is_alive(self):
        return self.hp > 0

class NPC(Character):
    def __init__(self, name, dialogue, hp=0, attack_power=0, inventory=None):
        super().__init__(name, hp, attack_power, inventory)
        self.dialogue = dialogue

class Monster(Character):
    def __init__(self, name, monster_type, hp, attack_power, drops=None):
        super().__init__(name, hp, attack_power)
        self.monster_type = monster_type
        self.drops = drops if drops is not None else []

class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value

    def use(self, target):
        return f"You can't use {self.name}."

class Potion(Item):
    def __init__(self, name, description, value, heal_amount):
        super().__init__(name, description, value)
        self.heal_amount = heal_amount

    def use(self, target):
        target.hp += self.heal_amount
        return f"{target.name} uses the {self.name} and heals for {self.heal_amount} HP."

class Location:
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None):
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.npcs = npcs if npcs is not None else []
        self.monsters = monsters if monsters is not None else []
        self.items = items if items is not None else []

    def describe(self):
        description = f"**{self.name}**\n"
        description += f"{self.description}\n"
        if self.npcs:
            description += "You see: " + ", ".join(npc.name for npc in self.npcs) + "\n"
        if self.monsters:
            description += "DANGER: " + ", ".join(monster.name for monster in self.monsters) + " is here!\n"
        if self.items:
            description += "On the ground: " + ", ".join(item.name for item in self.items) + "\n"
        return description

class Player(Character):
    def __init__(self, name, current_location, hp=20, attack_power=5):
        super().__init__(name, hp, attack_power)
        self.current_location = current_location
        self.previous_location = current_location

    def move(self, direction):
        if direction in self.current_location.exits:
            self.previous_location = self.current_location
            self.current_location = self.current_location.exits[direction]
            return True
        else:
            return False

    def retreat(self):
        self.current_location = self.previous_location

import os
import platform
import json

def clear_screen():
    """Clears the console screen."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def display_menu_and_state(player, message, actions):
    """Clears the screen, displays player status, a message, and a numbered action menu."""
    clear_screen()

    # Status Panel
    print("=" * 40)
    print(f"| Player: {player.name:<10} | HP: {player.hp:<3} | Location: {player.current_location.name:<10} |")
    print("=" * 40)

    # Message
    print(f"\n{message}\n")

    # Action Menu
    print("-" * 40)
    print("What do you do?")
    for i, action in enumerate(actions):
        print(f"  {i + 1}. {action['text']}")
    print("-" * 40)

def get_available_actions(player, game_mode):
    """Generates a list of available actions for the player."""
    actions = []
    if game_mode == "explore":
        actions.append({'text': 'Look around', 'command': 'look'})
        actions.append({'text': 'View inventory', 'command': 'inventory'})
        for direction in player.current_location.exits:
            actions.append({'text': f'Go {direction}', 'command': f'go {direction}'})
        for npc in player.current_location.npcs:
            actions.append({'text': f"Talk to {npc.name}", 'command': f"talk to '{npc.name}'"})
        for item in player.current_location.items:
            actions.append({'text': f"Get {item.name}", 'command': f"get '{item.name}'"})
        for item in player.inventory:
            if isinstance(item, Potion):
                actions.append({'text': f"Use {item.name}", 'command': f"use '{item.name}'"})
    elif game_mode == "encounter":
        actions.append({'text': 'Attack', 'command': 'attack'})
        actions.append({'text': 'Retreat', 'command': 'retreat'})
    elif game_mode == "combat":
        actions.append({'text': 'Attack', 'command': 'attack'})

    actions.append({'text': 'Quit game', 'command': 'quit'})
    return actions

def load_game_data(filepath):
    """Loads game data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    game_data = load_game_data("game_data.json")

    # Create location objects
    locations = {}
    for loc_id, loc_data in game_data["locations"].items():
        npc_objects = [NPC(npc["name"], npc["dialogue"]) for npc in loc_data.get("npcs", [])]
        monster_objects = [Monster(m["name"], m["monster_type"], m["hp"], m["attack_power"], drops=m.get("drops", [])) for m in loc_data.get("monsters", [])]
        locations[loc_id] = Location(loc_data["name"], loc_data["description"], npcs=npc_objects, monsters=monster_objects)

    # Link locations
    for loc_id, loc_data in game_data["locations"].items():
        location = locations[loc_id]
        for direction, dest_id in loc_data["exits"].items():
            location.exits[direction] = locations[dest_id]

    # Initialize Player and Game State
    player = Player("Hero", locations[game_data["start_location"]])
    game_mode = "explore"
    message = player.current_location.describe()

    # Main Game Loop
    while player.is_alive():
        available_actions = get_available_actions(player, game_mode)
        display_menu_and_state(player, message, available_actions)

        # Get player's choice
        choice = input("> ")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(available_actions):
                command = available_actions[choice_index]['command']
            else:
                message = "Invalid choice."
                continue
        except ValueError:
            message = "Please enter a number."
            continue

        # Process the command
        parts = command.split()
        verb = parts[0]

        if verb == "quit":
            print("Thanks for playing!")
            break
        elif verb == "look":
            message = player.current_location.describe()
        elif verb == "go":
            direction = parts[1]
            if player.move(direction):
                if player.current_location.monsters:
                    game_mode = "encounter"
                    message = f"You go {direction}, but a wild {player.current_location.monsters[0].name} blocks your path!"
                else:
                    message = f"You go {direction}.\n\n{player.current_location.describe()}"
            else:
                message = "You can't go that way." # Should not happen with menu
        elif verb == "talk":
            target_name = " ".join(parts[2:]).strip("'")
            npc = next((n for n in player.current_location.npcs if n.name.lower() == target_name.lower()), None)
            message = f'**{npc.name} says:** "{npc.dialogue}"' if npc else "There is no one here by that name."
        elif verb == "get":
            item_name = " ".join(parts[1:]).strip("'")
            item_to_get = next((i for i in player.current_location.items if i.name.lower() == item_name.lower()), None)
            if item_to_get:
                player.inventory.append(item_to_get)
                player.current_location.items.remove(item_to_get)
                message = f"You pick up the {item_to_get.name}."
            else:
                message = "You don't see that here."
        elif verb == "inventory":
            message = f"You are carrying:\n" + "\n".join(f"- {item.name}" for item in player.inventory) if player.inventory else "Your inventory is empty."
        elif verb == "use":
            item_name = " ".join(parts[1:]).strip("'")
            item_to_use = next((i for i in player.inventory if i.name.lower() == item_name.lower()), None)
            if item_to_use:
                message = item_to_use.use(player)
                if isinstance(item_to_use, Potion):
                    player.inventory.remove(item_to_use)
            else:
                message = "You don't have that item."
        elif verb == "attack":
            if game_mode == "encounter":
                game_mode = "combat"

            monster = player.current_location.monsters[0]
            monster.hp -= player.attack_power
            combat_message = f"You attack the {monster.name}, dealing {player.attack_power} damage."

            if monster.is_alive():
                player.hp -= monster.attack_power
                combat_message += f"\nThe {monster.name} attacks you, dealing {monster.attack_power} damage."
            else:
                combat_message += f"\nYou have defeated the {monster.name}!"
                if monster.drops:
                    for drop_data in monster.drops:
                        if drop_data["item_type"] == "Potion":
                            item = Potion(drop_data["name"], drop_data["description"], drop_data["value"], drop_data["heal_amount"])
                            player.current_location.items.append(item)
                            combat_message += f"\nThe {monster.name} dropped a {item.name}!"
                player.current_location.monsters.remove(monster)
                game_mode = "explore"
            message = combat_message
        elif verb == "retreat":
            if game_mode == "encounter":
                player.retreat()
                message = f"You retreat to {player.current_location.name}."
                game_mode = "explore"
        else:
            message = "Unknown action."

    if not player.is_alive():
        print("\nYou have been defeated. Game Over.")

if __name__ == "__main__":
    main()
