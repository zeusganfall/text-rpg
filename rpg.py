class Character:
    def __init__(self, name, hp=0, attack_power=0, inventory=None):
        self.name = name
        self.hp = hp
        self.attack_power = attack_power
        self.inventory = inventory if inventory is not None else []

class NPC(Character):
    def __init__(self, name, dialogue, hp=0, attack_power=0, inventory=None):
        super().__init__(name, hp, attack_power, inventory)
        self.dialogue = dialogue

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
        return description

class Player:
    def __init__(self, name, current_location):
        self.name = name
        self.current_location = current_location

    def move(self, direction):
        if direction in self.current_location.exits:
            self.current_location = self.current_location.exits[direction]
            return f"You go {direction}.\n\n{self.current_location.describe()}"
        else:
            return "You can't go that way."

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
    """Clears the screen and displays the game state."""
    clear_screen()

    # Status Panel
    print("=" * 40)
    print(f"| Player: {player.name:<10} | Location: {player.current_location.name:<10} |")
    print("=" * 40)

    # Action Result
    print(f"\n{message}\n")

    # Command Menu
    print("-" * 40)
    commands = "[look] "
    for direction in player.current_location.exits:
        commands += f"[go {direction}] "
    for npc in player.current_location.npcs:
        commands += f"[talk to '{npc.name}'] "
    print(commands)
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
        # Create NPC objects for the location
        npc_objects = []
        if "npcs" in loc_data:
            for npc_data in loc_data["npcs"]:
                npc_objects.append(NPC(npc_data["name"], npc_data["dialogue"]))

        locations[loc_id] = Location(
            loc_data["name"],
            loc_data["description"],
            npcs=npc_objects
        )

    # Link locations
    for loc_id, loc_data in game_data["locations"].items():
        location = locations[loc_id]
        for direction, dest_id in loc_data["exits"].items():
            location.exits[direction] = locations[dest_id]

    # Player
    start_location_id = game_data["start_location"]
    player = Player("Hero", locations[start_location_id])

    # Game Loop
    message = player.current_location.describe()
    while True:
        display_game_state(player, message)
        command = input("> ").lower().strip()
        if not command:
            continue

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
                message = player.move(direction)
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
        else:
            message = "Unknown command."

if __name__ == "__main__":
    main()
