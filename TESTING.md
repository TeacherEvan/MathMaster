# Testing Guide for MathMaster

This document explains how to run tests for the MathMaster project.

## JavaScript Tests (Web Version)

The web version of MathMaster is located in the `MathMistress/` directory and uses Jest for testing.

### Running Tests

```bash
cd MathMistress
npm test
```

### Linting

```bash
cd MathMistress
npm run lint
```

To auto-fix common linting issues:
```bash
cd MathMistress
npm run lint -- --fix
```

### Test Coverage

The JavaScript tests cover:
- **Syntax validation**: Ensures game.js has valid syntax and no merge conflicts
- **Math engine**: Tests the core mathematical problem generation
- **Performance**: Basic performance benchmarks

## Python Tests (Desktop Version)

The desktop Python version is located in `src/mathmistress/` and uses standard Python testing.

### Prerequisites

```bash
# Install tkinter (usually comes with Python)
sudo apt-get install python3-tk  # On Ubuntu/Debian

# For headless testing (CI/CD environments)
sudo apt-get install xvfb
```

### Running Tests

Basic import test (recommended for CI):
```bash
python3 test_imports.py
```

GUI tests (requires display):
```bash
# With virtual display for headless environments
DISPLAY=:99 xvfb-run -a python3 tests/test_lock_animation.py

# Direct run (if you have a display)
python3 tests/test_lock_animation.py
```

### Test Coverage

The Python tests cover:
- **Import validation**: Ensures all core modules can be imported
- **Lock animation**: Tests the visual lock animation system
- **Game features**: Tests worms and quotes functionality

## Known Issues

1. **Linting**: Some ESLint rules about function ordering and import extensions are flagged but don't affect functionality
2. **Python GUI tests**: Require either a display or virtual display setup for headless environments
3. **Module paths**: Tests have been fixed to correctly locate the game.js file in `assets/web/`

## Test Infrastructure Status

✅ JavaScript tests: All passing  
✅ Python import tests: All passing  
✅ Core functionality: Verified working  
⚠️ Some linting warnings remain (non-critical)

## Adding New Tests

### JavaScript Tests
Add test files to `MathMistress/tests/` following the existing pattern:
- `*.test.js` files are automatically discovered by Jest
- Use ES6 modules syntax
- Follow the existing test structure

### Python Tests
Add test files to `tests/` directory:
- Use descriptive names like `test_feature_name.py`
- Import modules correctly using relative paths
- Consider headless compatibility for CI/CD

## Continuous Integration

For CI environments, use:

```bash
# JavaScript tests
cd MathMistress && npm test

# Python import validation  
python3 test_imports.py

# Full Python tests (with virtual display)
DISPLAY=:99 xvfb-run -a python3 tests/test_lock_animation.py
```