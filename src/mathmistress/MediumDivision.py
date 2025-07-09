# MediumDivision: Division Math Problems for MathMaster
# This file documents division problems.
# Formats: a/x=b or x/a=b

problems = [
    # Division problems (formerly 51-100 from the combined list)
    # Format: equation string only
    "18/x=6",   # x=3
    "24/x=8",   # x=3
    "27/x=9",   # x=3
    "32/x=8",   # x=4
    "36/x=6",   # x=6
    "40/x=8",   # x=5
    "45/x=9",   # x=5
    "48/x=6",   # x=8
    "50/x=10",  # x=5
    "54/x=9",   # x=6
    "56/x=7",   # x=8
    "63/x=9",   # x=7
    "64/x=8",   # x=8
    "72/x=9",   # x=8
    "81/x=9",   # x=9
    "90/x=10",  # x=9
    "96/x=12",  # x=8
    "x/2=6",    # x=12
    "x/3=5",    # x=15
    "x/4=6",    # x=24
    "x/5=8",    # x=40
    "x/6=7",    # x=42
    "x/7=8",    # x=56
    "x/8=9",    # x=72
    "x/9=10",   # x=90
    "x/2=8",    # x=16
    "x/3=7",    # x=21
    "x/4=8",    # x=32
    "x/5=10",   # x=50
    "x/6=9",    # x=54
    "x/7=6",    # x=42
    "x/8=7",    # x=56
    "x/9=8",    # x=72
    "100/x=4",  # x=25
    "120/x=6",  # x=20
    "144/x=12", # x=12
    "150/x=5",  # x=30
    "160/x=8",  # x=20
    "180/x=6",  # x=30
    "200/x=8",  # x=25
    "216/x=9",  # x=24
    "225/x=9",  # x=25
    "240/x=8",  # x=30
    "250/x=10", # x=25
    "270/x=9",  # x=30
    "280/x=7",  # x=40
    "288/x=12", # x=24
    "294/x=7",  # x=42
    "296/x=8",  # x=37
    "300/x=10"  # x=30
]

# Optional: Function to display problems for testing
def display_problems():
    for idx, problem in enumerate(problems, 1):
        print(f"Problem {idx}: {problem}")

if __name__ == '__main__':
    display_problems() 