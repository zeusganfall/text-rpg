class Location:
    def __init__(self, name, description, exits=None, npcs=None, monsters=None, items=None):
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.npcs = npcs if npcs is not None else []
        self.monsters = monsters if monsters is not None else []
        self.items = items if items is not None else []

    def describe(self):
        print(f"**{self.name}**")
        print(self.description)
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Player:
    def __init__(self, name, current_location):
        self.name = name
        self.current_location = current_location

    def move(self, direction):
        if direction in self.current_location.exits:
            self.current_location = self.current_location.exits[direction]
            print(f"You go {direction}.")
            self.current_location.describe()
        else:
            print("You can't go that way.")

import json

def load_game_data(filepath):
    """Loads game data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    game_data = load_game_data("game_data.json")

    # Create location objects
    locations = {}
    for loc_id, loc_data in game_data["locations"].items():
        locations[loc_id] = Location(loc_data["name"], loc_data["description"])

    # Link locations
    for loc_id, loc_data in game_data["locations"].items():
        location = locations[loc_id]
        for direction, dest_id in loc_data["exits"].items():
            location.exits[direction] = locations[dest_id]

    # Player
    start_location_id = game_data["start_location"]
    player = Player("Hero", locations[start_location_id])
    player.current_location.describe()

    # Game Loop
    while True:
        command = input("> ").lower().strip()
        if not command:
            continue

        parts = command.split()
        verb = parts[0]

        if verb == "quit":
            print("Thanks for playing!")
            break
        elif verb == "look":
            player.current_location.describe()
        elif verb == "go":
            if len(parts) > 1:
                direction = parts[1]
                player.move(direction)
            else:
                print("Go where?")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
