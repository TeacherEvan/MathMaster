# Medium: Multiplication Math Problems for MathMaster Python
# This file documents 50 medium math problems focusing on multiplication with one variable.
# Format: ax = b (where x = b // a)
# - a: integer factor (2-20)
# - x: integer solution (2-15)
# - b: product (a * x), not exceeding 300
#
# All answers are integers and within the specified range.

problems = [
    # Example: 5x = 20 (x = 4)
]

# Generate problems
for a in range(2, 21):
    for x_val in range(2, 16): # Renamed x to x_val to avoid conflict
        b = a * x_val
        if b > 300:
            continue
        # Format problem as just the equation string
        problem_str = f"{a}x = {b}"
        problems.append(problem_str)
        if len(problems) >= 50:
            break
    if len(problems) >= 50:
        break


def display_problems():
    for idx, problem in enumerate(problems, 1):
        print(f"Problem {idx}: {problem}")

if __name__ == '__main__':
    display_problems()
