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

def main():
    # Locations
    oakhaven = Location(
        "Oakhaven",
        "A peaceful village nestled in a clearing. The smell of fresh bread fills the air."
    )
    whispering_woods = Location(
        "Whispering Woods",
        "A dense forest where the trees seem to whisper secrets. It's easy to get lost here."
    )
    goblin_cave = Location(
        "Goblin Cave",
        "A dark and damp cave, home to a clan of mischievous goblins."
    )

    # Link Locations
    oakhaven.exits["north"] = whispering_woods
    whispering_woods.exits["south"] = oakhaven
    whispering_woods.exits["east"] = goblin_cave
    goblin_cave.exits["west"] = whispering_woods

    # Player
    player = Player("Hero", oakhaven)
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
