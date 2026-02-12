"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate
an entire playthrough of the game. Please consult the project handout for
instructions and details.

You can copy/paste your code from Assignment 1 into this file, and modify it as
needed to work with your game.

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
from event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # Hint: self._game.get_location() gives you back the current location
        initial_location = self._game.get_location()
        first_event = Event(initial_location.id_num, initial_location.long_description)
        self._events.add_event(first_event, None)

        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, initial_location)

    def _handle_take(self, command: str, current_location: Location) -> None:
        """Handle a 'take' command during simulation, picking up an item at the current location."""
        item_name = command[5:].strip()
        if item_name in current_location.items:
            current_location.items.remove(item_name)
            item = self._game.get_item_by_name(item_name)
            if item:
                self._game.player.inventory.append(item)
        if self._events.last is not None:
            self._events.last.next_command = command

    def _handle_drop(self, command: str, current_location: Location) -> None:
        """Handle a 'drop' command during simulation, dropping an item at the current location."""
        item_name = command[5:].strip()
        inventory_names = self._game.get_inventory_names()
        if item_name in inventory_names:
            self._game.player.inventory = [i for i in self._game.player.inventory if i.name != item_name]
            item = self._game.get_item_by_name(item_name)
            if item and current_location.id_num != item.target_position:
                current_location.items.append(item_name)
        if self._events.last is not None:
            self._events.last.next_command = command

    def _handle_use(self, command: str, current_location: Location) -> None:
        """Handle a 'use' command during simulation, using a special item like a key."""
        item_name = command[4:].strip()
        if item_name == "key" and current_location.id_num == 5:
            office = self._game.get_location(8)
            office.locked = False
            self._game.player.inventory = [i for i in self._game.player.inventory if i.name != "key"]
        if self._events.last is not None:
            self._events.last.next_command = command

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """

        for command in commands:
            # Handle movement commands (go north/south/east/west)
            if command in current_location.available_commands:
                next_location_id = current_location.available_commands[command]
                self._game.current_location_id = next_location_id
                current_location = self._game.get_location()

                new_event = Event(current_location.id_num, current_location.long_description)
                self._events.add_event(new_event, command)

            # Handle non-movement menu commands
            elif command in ["look", "inventory", "score", "log", "quit"]:
                if self._events.last is not None:
                    self._events.last.next_command = command

            # Handle item commands via helper methods
            elif command.startswith("take "):
                self._handle_take(command, current_location)
            elif command.startswith("drop "):
                self._handle_drop(command, current_location)
            elif command.startswith("use "):
                self._handle_use(command, current_location)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and log location descriptions.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    win_walkthrough = [
        "go east",           # 0 -> 1 (Residence Hallway)
        "go south",          # 1 -> 4 (Bahen Centre)
        "go west",           # 4 -> 3 (Robarts Library)
        "go south",          # 3 -> 6 (Robarts Study Room) - USB drive here
        "take usb drive",
        "go north",          # 6 -> 3
        "go east",           # 3 -> 4
        "go south",          # 4 -> 7 (Lecture Hall) - Laptop charger here
        "take laptop charger",
        "go north",          # 7 -> 4
        "go east",           # 4 -> 5 (Coffee Shop) - Key here
        "take key",
        "use key",           # Unlock the office door
        "go south",          # 5 -> 8 (T.A. Office) - Lucky Mug here
        "take lucky mug",
        "go north",          # 8 -> 5
        "go north",          # 5 -> 2 (Campus Quad)
        "go west",           # 2 -> 1
        "go west",           # 1 -> 0 (Dorm Room)
        "drop usb drive",
        "drop laptop charger",
        "drop lucky mug"
    ]  # Create a list of all the commands needed to walk through your game to win it
    expected_log_win = [0, 1, 4, 3, 6, 3, 4, 7, 4, 5, 8, 5, 2, 1, 0]
    # Uncomment the line below to test your walkthrough
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log_win == sim.get_id_log()

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    lose_demo = [
        "go east", "go west",  # 0 -> 1 -> 0 (2 moves)
        "go east", "go west",  # 0 -> 1 -> 0 (4 moves)
        "go east", "go west",  # 0 -> 1 -> 0 (6 moves)
        "go east", "go west",  # 0 -> 1 -> 0 (8 moves)
        "go east", "go west",  # 0 -> 1 -> 0 (10 moves)
        "go east", "go west",  # (12 moves)
        "go east", "go west",  # (14 moves)
        "go east", "go west",  # (16 moves)
        "go east", "go west",  # (18 moves)
        "go east", "go west",  # (20 moves)
        "go east", "go west",  # (22 moves)
        "go east", "go west",  # (24 moves)
        "go east", "go west",  # (26 moves)
        "go east", "go west",  # (28 moves)
        "go east", "go west",  # (30 moves)
        "go east", "go west",  # (32 moves)
        "go east", "go west",  # (34 moves)
        "go east", "go west",  # (36 moves)
        "go east", "go west",  # (38 moves)
        "go east", "go west",  # (40 moves - game over!)
    ]
    expected_log_lose = [0] + [1, 0] * 20
    # Uncomment the line below to test your demo
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log_lose == sim.get_id_log()

    inventory_demo = [
        "go east",           # 0 -> 1
        "go south",          # 1 -> 4
        "go south",          # 4 -> 7 (Lecture Hall with laptop charger)
        "take laptop charger",
        "inventory",         # Check inventory
        "go north",          # 7 -> 4
        "go west",           # 4 -> 3
        "go south",          # 3 -> 6 (Robarts Study Room with USB drive)
        "take usb drive",
        "inventory"          # Check inventory again
    ]
    expected_log_inventory = [0, 1, 4, 7, 4, 3, 6]
    sim = AdventureGameSimulation('game_data.json', 0, inventory_demo)
    assert expected_log_inventory == sim.get_id_log()

    scores_demo = [
        "go east",           # 0 -> 1
        "go south",          # 1 -> 4
        "go south",          # 4 -> 7 (Lecture Hall)
        "take laptop charger",  # +5 points for pickup
        "score",             # Check score
        "go north",          # 7 -> 4
        "go north",          # 4 -> 1
        "go west",           # 1 -> 0 (Dorm Room)
        "drop laptop charger",  # +30 points for depositing at target
        "score"              # Check score again
    ]
    expected_log_scores = [0, 1, 4, 7, 4, 1, 0]
    sim = AdventureGameSimulation('game_data.json', 0, scores_demo)
    assert expected_log_scores == sim.get_id_log()

    enhancement_demo = [
        "go east",           # 0 -> 1
        "go east",           # 1 -> 2 (Campus Quad)
        "go south",          # 2 -> 5 (Coffee Shop) - Key is here
        "take key",
        "use key",           # Unlock the T.A. Office door
        "go south",          # 5 -> 8 (T.A. Office) - Now unlocked!
        "take lucky mug",
        "go north",          # 8 -> 5
        "go north",          # 5 -> 2
        "go west",           # 2 -> 1
        "go west",           # 1 -> 0 (Dorm Room)
        "drop lucky mug"     # +40 points for depositing
    ]
    expected_log_enhancement = [0, 1, 2, 5, 8, 5, 2, 1, 0]
    sim = AdventureGameSimulation('game_data.json', 0, enhancement_demo)
    assert expected_log_enhancement == sim.get_id_log()
