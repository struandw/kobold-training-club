# -*- coding: utf-8 -*-

"""A list of functions for performing encounter maths"""

import contextlib
import os
import sqlite3
from typing import List, Tuple

xp_per_day_per_character_per_level = [
    0,
    300,
    600,
    1200,
    1700,
    3500,
    4000,
    5000,
    6000,
    7500,
    9000,
    10500,
    11500,
    13500,
    15000,
    18000,
    20000,
    25000,
    27000,
    30000,
    40000,
]

xp_thresholds: List[List[int]] = [
    [],
    [25, 50, 75, 100],
    [50, 100, 150, 200],
    [75, 150, 225, 400],
    [125, 250, 375, 500],
    [250, 500, 750, 1100],
    [300, 600, 900, 1400],
    [350, 750, 1100, 1700],
    [450, 900, 1400, 2100],
    [550, 1100, 1600, 2400],
    [600, 1200, 1900, 2800],
    [800, 1600, 2400, 3600],
    [1000, 2000, 3000, 4500],
    [1100, 2200, 3400, 5100],
    [1250, 2500, 3800, 5700],
    [1400, 2800, 4300, 6400],
    [1600, 3200, 4800, 7200],
    [2000, 3900, 5900, 8800],
    [2100, 4200, 6300, 9500],
    [2400, 4900, 7300, 10900],
    [2800, 5700, 8500, 12700],
]

cr_xp_mapping = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000,
}

encounter_xp_multipliers = [1, 1.5, 2, 2.5, 3, 4]

PartyType = List[Tuple[int, int]]
MonstersType = List[Tuple[str, int]]


path_to_database = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "data/monsters.db")
)
db_location = path_to_database


def diff_calc(party: PartyType, enc_xp: int) -> str:
    """Calculate which threshold an encounter meets for a given party"""
    party_thresholds = party_thresholds_calc(party)

    if enc_xp < party_thresholds[0]:
        threshold = "trifling"
    elif enc_xp < party_thresholds[1]:
        threshold = "easy"
    elif enc_xp < party_thresholds[2]:
        threshold = "medium"
    elif enc_xp < party_thresholds[3]:
        threshold = "hard"
    else:
        threshold = "deadly"

    return threshold


def party_thresholds_calc(party: PartyType) -> List[int]:
    """Generates a list of XP thresholds for encounters based on the party

    Args:
        party (PartyType): the party to calculate the thresholds for

    Returns:
        List[int]: a list of xp values where each threshold is
    """
    party_thresholds = [0, 0, 0, 0, 0]
    for tup in party:
        (size, level) = tup
        for i in range(len(party_thresholds) - 1):
            party_thresholds[i] += xp_thresholds[level][i] * size
        party_thresholds[4] += xp_per_day_per_character_per_level[level] * size

    return party_thresholds


# Pass a list of CRs and a list of quantities of monsters
# TODO: refactor to a list of tuples (cr, quantity)
def cr_calc(challenge_ratings: List[str], quantities: List[int]) -> int:
    """Adjust the CR of an encounter to take into account monster quantity multipliers

    Args:
        cr (List[str]): A list of the crs of the monsters in the encounter
        quantities (List[int]): a list of the numbers of each monster

    Returns:
        int: the XP the encounter is worth, adjusted based on the number of enemies
    """
    unadj_cr_total = 0
    for i, monster_cr in enumerate(challenge_ratings):
        unadj_cr_total += cr_xp_mapping[monster_cr] * quantities[i]

    quantity: int = sum(quantities)

    if quantity == 1:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[0]
    elif quantity == 2:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[1]
    elif 3 <= quantity <= 6:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[2]
    elif 7 <= quantity <= 10:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[3]
    elif 11 <= quantity <= 14:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[4]
    else:
        adj_xp_total = unadj_cr_total * encounter_xp_multipliers[5]

    return int(adj_xp_total)


def get_monster_cr(monster: str) -> str:
    """Return the CR of a monster given its name"""
    with contextlib.closing(sqlite3.connect(db_location)) as conn:
        cursor = conn.cursor()
        # conn.set_trace_callback(print)
        cursor.execute(
            """SELECT cr FROM monsters WHERE name = ?""", (monster,))
        monster_cr = cursor.fetchone()[0]
    return monster_cr


def get_encounter_difficulty(party: PartyType, monsters: MonstersType) -> Tuple[int, str]:
    """Return the XP earned in an encounter and which threshold it meets

    Args:
        party (PartyType): The party which will face the monsters
        monsters (MonstersType): The monsters making up the encounter

    Returns:
        Tuple[int, str]: A tuple of the XP earned in an encounter and which threshold it meets
    """
    crs = []
    quantities = []

    for monster_set in monsters:
        crs.append(get_monster_cr(monster_set[0]))
        quantities.append(monster_set[1])

    encounter_exp = cr_calc(crs, quantities)
    diff_level = diff_calc(party, encounter_exp)

    return (
        encounter_exp,
        diff_level,
    )
