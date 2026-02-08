"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from dataclasses import dataclass, field


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id_num: The unique numerical identifier for this location.
        - brief_description: A short description shown on subsequent visits.
        - long_description: A detailed description shown on first visit or when using 'look'.
        - available_commands: A mapping from command strings to destination location IDs.
        - items: A list of item names currently present at this location.
        - visited: Whether the player has visited this location before.
        - locked: Whether this location is locked and requires a key to enter.

    Representation Invariants:
        - self.id_num >= 0
        - all(loc_id >= 0 for loc_id in self.available_commands.values())
    """

    id_num: int
    brief_description: str
    long_description: str
    available_commands: dict[str, int]
    items: list[str]
    visited: bool = False
    locked: bool = False


@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - name: The name of the item (lowercase).
        - description: A description of the item shown when examining it.
        - start_position: The location ID where this item starts.
        - target_position: The location ID where depositing this item gives points (-1 if N/A).
        - target_points: The number of points awarded for depositing at target location.

    Representation Invariants:
        - self.start_position >= 0
        - self.target_position >= -1
        - self.target_points >= 0
    """

    name: str
    description: str = ""
    start_position: int = 0
    target_position: int = 0
    target_points: int = 0


@dataclass
class Player:
    """The player in our text adventure game.

    Instance Attributes:
        - inventory: A list of Item objects currently held by the player.
        - score: The player's current score.
        - moves_remaining: The number of moves the player has left before losing.

    Representation Invariants:
        - self.score >= 0
        - self.moves_remaining >= 0
    """

    inventory: list[Item] = field(default_factory=list)
    score: int = 0
    moves_remaining: int = 40


if __name__ == "__main__":
    pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })
