"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from game_entities import Location, Item, Player
from event_logger import Event, EventList

# Note: You may add in other import statements here as needed

MENU_COMMANDS = ["look", "inventory", "score", "log", "quit"]
WINNING_LOCATION = 0  # Dorm room where items must be deposited

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The ID of the player's current location.
        - ongoing: Whether the game is still in progress.
        - player: The Player object tracking inventory, score, and moves.
        - max_moves: The maximum number of moves allowed before losing.
        - winning_items: List of item names required to win the game.

    Representation Invariants:
        - self.current_location_id in self._locations
        - self.max_moves > 0
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed
    player: Player
    max_moves: int
    winning_items: list[str]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        self._locations, self._items, self.max_moves, self.winning_items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True
        self.player = Player(inventory=[], score=0, moves_remaining=self.max_moves)

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item], int, list[str]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        (2) a list of all Item objects, (3) max moves, and (4) winning items list."""

        with open(filename, 'r') as f:
            data = json.load(f)

        locations = {}
        for loc_data in data['locations']:
            location_obj = Location(
                loc_data['id'],
                loc_data['brief_description'],
                loc_data['long_description'],
                loc_data['available_commands'],
                loc_data['items'].copy(),
                False,  # visited
                loc_data.get('locked', False)
            )
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:
            item_obj = Item(
                item_data['name'],
                item_data.get('description', ''),
                item_data['start_position'],
                item_data['target_position'],
                item_data['target_points']
            )
            items.append(item_obj)

        max_moves = data.get('max_moves', 40)
        winning_items = data.get('winning_items', [])

        return locations, items, max_moves, winning_items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        # YOUR CODE BELOW
        if loc_id is None:
            return self._locations[self.current_location_id]
        return self._locations[loc_id]

    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Return the Item object with the given name, or None if not found."""
        for item in self._items:
            if item.name == name:
                return item
        return None

    def get_inventory_names(self) -> list[str]:
        """Return a list of names of items in the player's inventory."""
        return [item.name for item in self.player.inventory]

    def check_win_condition(self) -> bool:
        """Return True if the player has won the game (all required items deposited at dorm)."""
        # Player wins if all winning items have been deposited at the winning location
        # and player is at winning location
        if self.current_location_id != WINNING_LOCATION:
            return False

        # Check if all winning items are no longer in play (deposited)
        for item_name in self.winning_items:
            item = self.get_item_by_name(item_name)
            if item is None:
                continue
            # Item should not be in inventory or at any location
            if item_name in self.get_inventory_names():
                return False
            for loc in self._locations.values():
                if item_name in loc.items:
                    return False
        return True

    def check_lose_condition(self) -> bool:
        """Return True if the player has lost the game (no moves remaining)."""
        return self.player.moves_remaining <= 0

    def decrement_moves(self) -> None:
        """Decrement the player's remaining moves by 1."""
        self.player.moves_remaining -= 1


def handle_take_command(game: AdventureGame, item_name: str) -> str:
    """Handle the take command, picking up an item from the current location.
    Returns a message describing the result.
    """
    location = game.get_location()

    if item_name not in location.items:
        return f"There is no {item_name} here."

    item = game.get_item_by_name(item_name)
    if item is None:
        return f"Unknown item: {item_name}"

    # Remove from location and add to inventory
    location.items.remove(item_name)
    game.player.inventory.append(item)
    return f"You picked up the {item_name}."


def handle_drop_command(game: AdventureGame, item_name: str) -> str:
    """Handle the drop command, dropping an item at the current location.
    Awards points if dropped at the target location.
    Returns a message describing the result.
    """
    inventory_names = game.get_inventory_names()

    if item_name not in inventory_names:
        return f"You don't have a {item_name} in your inventory."

    item = game.get_item_by_name(item_name)
    location = game.get_location()

    # Remove from inventory
    game.player.inventory = [i for i in game.player.inventory if i.name != item_name]

    # Check if this is the target location
    if location.id_num == item.target_position:
        game.player.score += item.target_points
        return f"You deposited the {item_name}. +{item.target_points} points!"
    else:
        # Just drop at current location
        location.items.append(item_name)
        return f"You dropped the {item_name}."


def handle_use_command(game: AdventureGame, item_name: str) -> str:
    """Handle the use command for special items like keys.
    Returns a message describing the result.
    """
    if item_name not in game.get_inventory_names():
        return f"You don't have a {item_name} in your inventory."

    if item_name == "key":
        # Check if at a location adjacent to the locked T.A. office (location 8)
        location = game.get_location()
        if location.id_num == 5:  # Coffee shop, adjacent to office
            office = game.get_location(8)
            if office.locked:
                office.locked = False
                # Remove key from inventory
                game.player.inventory = [i for i in game.player.inventory if i.name != "key"]
                game.player.score += 10  # Bonus for solving puzzle
                return "You unlock the T.A. office door with the key. The door swings open! +10 points!"
            else:
                return "The office door is already unlocked."
        else:
            return "There's nothing to unlock here."
    else:
        return f"You can't use the {item_name} here."


def print_location_description(location: Location, full: bool = False) -> None:
    """Print the location description. If full=True or not visited before, print long description."""
    if full or not location.visited:
        print(location.long_description)
        location.visited = True
    else:
        print(location.brief_description)

    # Show items at this location
    if location.items:
        print("\nYou see the following items here:")
        for item in location.items:
            print(f"  - {item}")


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your mark will be based on how well-organized your code is.

        location = game.get_location()

        # Add new Event to game log to represent current game location
        #  Note that the <choice> variable should be the command which led to this event
        event = Event(location.id_num, location.long_description)
        game_log.add_event(event, choice)

        # Depending on whether or not it's been visited before,
        #  print either full description (first time visit) or brief description (every subsequent visit) of location
        print()
        print_location_description(location)

        # Win condition
        if game.check_win_condition():
            print("You win!")
            print("You found all your items and made it back to your dorm!")
            print("With your USB drive, charger, and lucky mug, you submit your project on time.")
            print(f"Final Score: {game.player.score}")
            game.ongoing = False
            break

        # Display possible actions at this location
        print(f"\n[Moves remaining: {game.player.moves_remaining}] [Score: {game.player.score}]")
        print("What to do? Choose from: look, inventory, score, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Show item-related commands
        if location.items:
            print("  - take [item name]")
        if game.player.inventory:
            print("  - drop [item name]")
            if "key" in game.get_inventory_names():
                print("  - use key")

        # Get and validate choice
        choice = input("\nEnter action: ").lower().strip()

        # Parse and validate command
        valid_command = False
        if choice in menu:
            valid_command = True
        elif choice in location.available_commands:
            valid_command = True
        elif choice.startswith("take ") or choice.startswith("drop ") or choice.startswith("use "):
            valid_command = True

        while not valid_command:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()
            if choice in menu:
                valid_command = True
            elif choice in location.available_commands:
                valid_command = True
            elif choice.startswith("take ") or choice.startswith("drop ") or choice.startswith("use "):
                valid_command = True

        print("========")
        print("You decided to:", choice)

        # Handle menu commands
        if choice == "log":
            print("\n--- Game Log ---")
            game_log.display_events()
        elif choice == "look":
            print_location_description(location, full=True)
        elif choice == "inventory":
            if not game.player.inventory:
                print("Your inventory is empty.")
            else:
                print("You are carrying:")
                for item in game.player.inventory:
                    print(f" - {item.name}: {item.description}")
        elif choice == "score":
            print(f"Your current score is: {game.player.score}")
        elif choice == "quit":
            print("Bye")
            game.ongoing = False

        # Handle movement commands
        elif choice in location.available_commands:
            # TODO: handle movement commands
            pass

        # Handle take command
        elif choice.startswith("take "):
            item_name = choice[5:].strip()
            result = handle_take_command(game, item_name)
            print(result)
            game.decrement_moves()

        # Handle drop command
        elif choice.startswith("drop "):
            item_name = choice[5:].strip()
            result = handle_drop_command(game, item_name)
            print(result)
            game.decrement_moves()

        # Handle use command
        elif choice.startswith("use "):
            item_name = choice[4:].strip()
            result = handle_use_command(game, item_name)
            print(result)
            game.decrement_moves()

        # Check lose condition
        if game.check_lose_condition() and game.ongoing:
            print("GAME OVER")
            print("You ran out of moves.")
            print(f"Final Score: {game.player.score}")
            game.ongoing = False
