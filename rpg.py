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

    def move(self, direction):
        if direction in self.current_location.exits:
            self.current_location = self.current_location.exits[direction]
            return True
        else:
            return False

import os
import platform
import json

def clear_screen():
    """Clears the console screen."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def display_game_state(player, message):
    """Clears the screen and displays the game state in explore mode."""
    clear_screen()

    # Status Panel
    print("=" * 40)
    print(f"| Player: {player.name:<10} | HP: {player.hp:<3} | Location: {player.current_location.name:<10} |")
    print("=" * 40)

    # Action Result
    print(f"\n{message}\n")

    # Command Menu
    print("-" * 40)
    commands = "[look] [inventory] "
    for direction in player.current_location.exits:
        commands += f"[go {direction}] "
    for npc in player.current_location.npcs:
        commands += f"[talk to '{npc.name}'] "
    for item in player.current_location.items:
        commands += f"[get '{item.name}'] "
    for item in player.inventory:
        if isinstance(item, Potion):
            commands += f"[use '{item.name}'] "
    print(commands)
    print("-" * 40)

def display_combat_state(player, monster, message):
    """Clears the screen and displays the combat state."""
    clear_screen()

    # Combat Status Panel
    print("=" * 40)
    print(f"| {player.name} HP: {player.hp:<4} | {monster.name} HP: {monster.hp:<4} |")
    print("=" * 40)

    # Action Result
    print(f"\n{message}\n")

    # Command Menu
    print("-" * 40)
    print("[attack]")
    print("-" * 40)

def load_game_data(filepath):
    """Loads game data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    game_data = load_game_data("game_data.json")

    # Create location objects
    locations = {}
    for loc_id, loc_data in game_data["locations"].items():
        # Create NPC objects
        npc_objects = []
        if "npcs" in loc_data:
            for npc_data in loc_data["npcs"]:
                npc_objects.append(NPC(npc_data["name"], npc_data["dialogue"]))

        # Create Monster objects
        monster_objects = []
        if "monsters" in loc_data:
            for m_data in loc_data["monsters"]:
                monster_objects.append(Monster(
                    m_data["name"],
                    m_data["monster_type"],
                    m_data["hp"],
                    m_data["attack_power"],
                    drops=m_data.get("drops", [])
                ))

        locations[loc_id] = Location(
            loc_data["name"], loc_data["description"],
            npcs=npc_objects, monsters=monster_objects
        )

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
        # Display UI based on game mode
        if game_mode == "explore":
            display_game_state(player, message)
        elif game_mode == "combat":
            monster = player.current_location.monsters[0]
            display_combat_state(player, monster, message)

        # Get user input
        command = input("> ").lower().strip()
        if not command:
            continue

        # Process commands based on game mode
        if game_mode == "explore":
            parts = command.split()
            verb = parts[0]

            if verb == "quit":
                print("Thanks for playing!")
                break
            elif verb == "look":
                message = player.current_location.describe()
            elif verb == "go":
                if len(parts) > 1:
                    direction = parts[1]
                    if player.move(direction):
                        # Move successful, now check for monsters
                        if player.current_location.monsters:
                            game_mode = "combat"
                            monster = player.current_location.monsters[0]
                            message = f"You go {direction}, but a wild {monster.name} blocks your path!"
                        else:
                            message = f"You go {direction}.\n\n{player.current_location.describe()}"
                    else:
                        message = "You can't go that way."
                else:
                    message = "Go where?"
            elif verb == "talk":
                if len(parts) > 2 and parts[1] == "to":
                    target_name = " ".join(parts[2:]).strip("'")
                    found_npc = False
                    for npc in player.current_location.npcs:
                        if npc.name.lower() == target_name.lower():
                            message = f'**{npc.name} says:** "{npc.dialogue}"'
                            found_npc = True
                            break
                    if not found_npc:
                        message = "There is no one here by that name."
                else:
                    message = "Talk to whom?"
            elif verb == "get":
                if len(parts) > 1:
                    item_name = " ".join(parts[1:])
                    item_to_get = None
                    for item in player.current_location.items:
                        if item.name.lower() == item_name.lower():
                            item_to_get = item
                            break
                    if item_to_get:
                        player.inventory.append(item_to_get)
                        player.current_location.items.remove(item_to_get)
                        message = f"You pick up the {item_to_get.name}."
                    else:
                        message = "You don't see that here."
                else:
                    message = "Get what?"
            elif verb == "inventory":
                if player.inventory:
                    inventory_list = "\n".join(f"- {item.name}: {item.description}" for item in player.inventory)
                    message = f"You are carrying:\n{inventory_list}"
                else:
                    message = "Your inventory is empty."
            elif verb == "use":
                if len(parts) > 1:
                    item_name = " ".join(parts[1:])
                    item_to_use = None
                    for item in player.inventory:
                        if item.name.lower() == item_name.lower():
                            item_to_use = item
                            break
                    if item_to_use:
                        message = item_to_use.use(player)
                        if isinstance(item_to_use, Potion):
                            player.inventory.remove(item_to_use)
                    else:
                        message = "You don't have that item."
                else:
                    message = "Use what?"
            else:
                message = "Unknown command."

        elif game_mode == "combat":
            monster = player.current_location.monsters[0]
            if command == "attack":
                # Player attacks monster
                monster.hp -= player.attack_power
                combat_message = f"You attack the {monster.name}, dealing {player.attack_power} damage."

                if monster.is_alive():
                    # Monster attacks player
                    player.hp -= monster.attack_power
                    combat_message += f"\nThe {monster.name} attacks you, dealing {monster.attack_power} damage."
                else:
                    # Monster is defeated
                    combat_message += f"\nYou have defeated the {monster.name}!"

                    # Handle loot drops
                    if monster.drops:
                        for drop_data in monster.drops:
                            # This is a simple factory. Could be expanded.
                            if drop_data["item_type"] == "Potion":
                                item = Potion(
                                    drop_data["name"],
                                    drop_data["description"],
                                    drop_data["value"],
                                    drop_data["heal_amount"]
                                )
                                player.current_location.items.append(item)
                                combat_message += f"\nThe {monster.name} dropped a {item.name}!"

                    player.current_location.monsters.remove(monster)
                    game_mode = "explore"

                message = combat_message
            else:
                message = "You can't do that in combat. You must [attack]!"

    # Game Over
    if not player.is_alive():
        print("\nYou have been defeated. Game Over.")

if __name__ == "__main__":
    main()
