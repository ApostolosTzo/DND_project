import random


# The format: NdX+Y
#     * N	Number of dice to roll	2 = roll two dice
#     * d	Dice separator	just notation
#     * X	Number of sides per die	d6 = 6-sided die (1-6)
#     * +Y	Flat bonus added after the roll	+3 = add 3 to total 
#     ```
#     Examples
#     Roll	What happens	Range
#     1d6	Roll one 6-sided die	1–6
#     2d6	Roll two 6-sided dice, sum them	2–12
#     1d20+3	Roll one 20-sided die, add 3	4–23
#     3d4+2	Roll three 4-sided dice, add 2	5–14 


def roll(dice_str: str) -> int: # Rolls dice based on the given string format and returns the total. Takes a string like "2d6" or "1d20+3" and returns the result as an integer.
    if "+" in dice_str: # If the string contains a "+", split it into the dice part and the bonus, and convert the bonus to an integer.
        dice_part, bonus = dice_str.split("+")
        bonus = int(bonus)
    elif "-" in dice_str: # If the string contains a "-", split it into the dice part and the bonus, and convert the bonus to a negative integer.
        dice_part, bonus = dice_str.split("-")
        bonus = -int(bonus)
    else: # no bonus, just roll the dice
        dice_part = dice_str
        bonus = 0
    # Split the dice part into the number of dice and the number of sides, and convert them to integers.
    num, sides = dice_part.split("d") # Split the dice part into the number of dice and the number of sides, and convert them to integers.
                # generates a ranfom integer between 1 and the number of sides for each die, sums them up, and adds any bonus.
    total = sum(random.randint(1, int(sides)) for _ in range(int(num))) # Does this num times (e.g., 2 times for "2d6")
            # Adds all the individual die rolls together
    return total + bonus

# Used for character stat generation. 
# The D&D method: roll 4 six-sided dice, drop the lowest, sum the rest.
def roll_4d6_drop_lowest() -> int:
    # Roll 4 six-sided dice.
    # Creates a list of 4 random numbers, each between 1 and 6.
    rolls = [random.randint(1, 6) for _ in range(4)]
    # Finds the smallest number in the list and removes it.
    rolls.remove(min(rolls))
    return sum(rolls)


# roll("1d20")        # 1–20 (single d20)
# roll("2d6+3")       # 5–15 (two d6 + 3)
# roll("3d4-1")       # 2–11 (three d4 - 1)
# roll_4d6_drop_lowest()  # 3–18 (for character stats)
