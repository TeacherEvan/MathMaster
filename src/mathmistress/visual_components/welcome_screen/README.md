# Welcome Screen Visual Components

This directory contains the visual components used in the MathMaster welcome screen. Each component is responsible for a specific visual aspect of the welcome screen, making the code more modular and easier to maintain.

## Components

### BrainAnimation
- Handles the pulsing brain animation in the center of the screen
- Includes veins and muscular effects
- Located in `brain_animation.py`

### MatrixBackground
- Creates the Matrix-style falling code effect
- Displays semi-transparent algebraic problems
- Located in `matrix_background.py`

### MathSymbols
- Manages floating mathematical symbols
- Handles symbol movement and bouncing
- Located in `math_symbols.py`

### ProgressBar
- Displays the auto-continue progress bar
- Handles progress updates
- Located in `progress_bar.py`

### TitleDisplay
- Renders the title, subtitle, and description
- Includes glow effects and text scaling
- Located in `title_display.py`

### ColorUtils
- Provides shared color manipulation utilities
- Used by other components for alpha blending
- Located in `color_utils.py`

## Usage

Each component is initialized with a canvas and any required data. The components are used by the main `WelcomeScreen` class to create a cohesive visual experience.

Example:
```python
from src.visual_components.welcome_screen import (
    BrainAnimation,
    MatrixBackground,
    MathSymbols,
    ProgressBar,
    TitleDisplay
)

# Initialize components
brain_animation = BrainAnimation(canvas)
matrix_background = MatrixBackground(canvas, math_problems)
math_symbols = MathSymbols(canvas, symbols)
progress_bar = ProgressBar(canvas)
title_display = TitleDisplay(canvas)

# Use components
brain_animation.update_animation()
matrix_background.draw(width, height)
math_symbols.update_positions()
progress_bar.draw(progress)
title_display.draw(width, height)
```

## Benefits

1. **Modularity**: Each visual component is self-contained and can be modified independently
2. **Reusability**: Components can be reused in other parts of the application
3. **Maintainability**: Easier to debug and update individual components
4. **Performance**: Components can be optimized individually
5. **Testing**: Components can be tested in isolation 