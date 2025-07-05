/**
 * MathMistress - Mathematical Engine
 * Greek Mathematical Wisdom System
 * 
 * This engine generates mathematical problems and provides step-by-step solutions
 * with philosophical insights from Greek mathematics tradition.
 */

class MathEngine {
    constructor() {
        this.levels = {
            'Novice': { name: 'Novice', difficulty: 1, maxNumber: 20 },
            'Apprentice': { name: 'Apprentice', difficulty: 2, maxNumber: 50 },
            'Disciple': { name: 'Disciple', difficulty: 3, maxNumber: 100 },
            'Scholar': { name: 'Scholar', difficulty: 4, maxNumber: 200 },
            'Sage': { name: 'Sage', difficulty: 5, maxNumber: 500 },
            'Master': { name: 'Master', difficulty: 6, maxNumber: 1000 }
        };
        
        this.problemTypes = {
            'addition': { weight: 3, complexity: 1 },
            'subtraction': { weight: 3, complexity: 1 },
            'multiplication': { weight: 2, complexity: 2 },
            'division': { weight: 2, complexity: 2 },
            'mixed': { weight: 1, complexity: 3 }
        };
        
        this.philosophicalQuotes = [
            "Number is the within of all things - Pythagoras",
            "Mathematics is the alphabet with which God has written the universe - Galileo",
            "The essence of mathematics is not to make simple things complicated - Eudoxus",
            "Geometry is knowledge of the eternally existent - Plato",
            "Number rules the universe - Aristotle",
            "All is number - Pythagoras",
            "The diagonal of a square is incommensurable with its side - Hippasus",
            "Mathematics is the music of reason - Proclus",
            "In mathematics, the art of proposing a question must be held of higher value than solving it - Apollonius",
            "The laws of nature are but the mathematical thoughts of God - Euclid",
            "What is sought is found by calculation - Archimedes",
            "The moving power of mathematical invention is not reasoning but imagination - Hipparchus",
            "Mathematics is the door and key to the sciences - Thales",
            "The mathematician's patterns, like the painter's or poet's, must be beautiful - Eratosthenes",
            "Perfect numbers like perfect men are very rare - Nicomachus"
        ];
        
        this.currentProblem = null;
        this.currentSolution = null;
        this.currentLevel = 'Novice';
        this.mistakeCount = 0;
        this.maxMistakes = 20;
        this.revealedChars = new Set();
        this.helpButtonClicked = false;
        this.completedProblems = 0;
    }
    
    /**
     * Generate a new problem based on current level and difficulty
     */
    generateProblem() {
        const level = this.levels[this.currentLevel];
        const maxNum = level.maxNumber;
        const difficulty = level.difficulty;
        
        // Select problem type based on difficulty
        const availableTypes = Object.keys(this.problemTypes).filter(type => 
            this.problemTypes[type].complexity <= difficulty
        );
        
        const weights = availableTypes.map(type => this.problemTypes[type].weight);
        const selectedType = this.weightedRandom(availableTypes, weights);
        
        let problem;
        switch(selectedType) {
            case 'addition':
                problem = this.generateAdditionProblem(maxNum);
                break;
            case 'subtraction':
                problem = this.generateSubtractionProblem(maxNum);
                break;
            case 'multiplication':
                problem = this.generateMultiplicationProblem(maxNum);
                break;
            case 'division':
                problem = this.generateDivisionProblem(maxNum);
                break;
            case 'mixed':
                problem = this.generateMixedProblem(maxNum);
                break;
            default:
                problem = this.generateAdditionProblem(maxNum);
        }
        
        this.currentProblem = problem;
        this.currentSolution = this.generateSolutionSteps(problem);
        this.revealedChars.clear();
        this.helpButtonClicked = false;
        
        return {
            problem: problem,
            solution: this.currentSolution,
            quote: this.getRandomQuote()
        };
    }
    
    /**
     * Generate addition problems: x + a = b, a + x = b, a + x + c = b
     */
    generateAdditionProblem(maxNum) {
        const patterns = [
            () => { // x + a = b
                const a = this.randomInt(1, maxNum / 2);
                const x = this.randomInt(1, maxNum / 2);
                const b = x + a;
                return { equation: `x + ${a} = ${b}`, answer: x, type: 'x_plus_a' };
            },
            () => { // a + x = b
                const a = this.randomInt(1, maxNum / 2);
                const x = this.randomInt(1, maxNum / 2);
                const b = a + x;
                return { equation: `${a} + x = ${b}`, answer: x, type: 'a_plus_x' };
            },
            () => { // a + x + c = b
                const a = this.randomInt(1, maxNum / 4);
                const c = this.randomInt(1, maxNum / 4);
                const x = this.randomInt(1, maxNum / 4);
                const b = a + x + c;
                return { equation: `${a} + x + ${c} = ${b}`, answer: x, type: 'a_plus_x_plus_c' };
            }
        ];
        
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        return pattern();
    }
    
    /**
     * Generate subtraction problems: x - a = b, a - x = b, a + x - c = b
     */
    generateSubtractionProblem(maxNum) {
        const patterns = [
            () => { // x - a = b
                const a = this.randomInt(1, maxNum / 3);
                const b = this.randomInt(1, maxNum / 3);
                const x = a + b;
                return { equation: `x - ${a} = ${b}`, answer: x, type: 'x_minus_a' };
            },
            () => { // a - x = b
                const a = this.randomInt(maxNum / 2, maxNum);
                const b = this.randomInt(1, maxNum / 3);
                const x = a - b;
                return { equation: `${a} - x = ${b}`, answer: x, type: 'a_minus_x' };
            },
            () => { // a + x - c = b
                const a = this.randomInt(1, maxNum / 4);
                const c = this.randomInt(1, maxNum / 4);
                const b = this.randomInt(1, maxNum / 4);
                const x = b - a + c;
                return { equation: `${a} + x - ${c} = ${b}`, answer: x, type: 'a_plus_x_minus_c' };
            }
        ];
        
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        return pattern();
    }
    
    /**
     * Generate multiplication problems: ax = b, x/a = b
     */
    generateMultiplicationProblem(maxNum) {
        const patterns = [
            () => { // ax = b
                const a = this.randomInt(2, Math.min(10, maxNum / 5));
                const x = this.randomInt(1, maxNum / a);
                const b = a * x;
                return { equation: `${a}x = ${b}`, answer: x, type: 'a_times_x' };
            },
            () => { // x/a = b
                const a = this.randomInt(2, Math.min(10, maxNum / 5));
                const b = this.randomInt(1, maxNum / a);
                const x = a * b;
                return { equation: `x/${a} = ${b}`, answer: x, type: 'x_divided_by_a' };
            }
        ];
        
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        return pattern();
    }
    
    /**
     * Generate division problems: x/a = b, a/x = b
     */
    generateDivisionProblem(maxNum) {
        const patterns = [
            () => { // x/a = b
                const a = this.randomInt(2, Math.min(10, maxNum / 5));
                const b = this.randomInt(1, maxNum / a);
                const x = a * b;
                return { equation: `x ÷ ${a} = ${b}`, answer: x, type: 'x_divided_by_a' };
            },
            () => { // a/x = b
                const b = this.randomInt(2, Math.min(10, maxNum / 5));
                const x = this.randomInt(1, maxNum / b);
                const a = b * x;
                return { equation: `${a} ÷ x = ${b}`, answer: x, type: 'a_divided_by_x' };
            }
        ];
        
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        return pattern();
    }
    
    /**
     * Generate mixed problems with multiple operations
     */
    generateMixedProblem(maxNum) {
        const patterns = [
            () => { // ax + b = c
                const a = this.randomInt(2, Math.min(5, maxNum / 10));
                const b = this.randomInt(1, maxNum / 5);
                const x = this.randomInt(1, maxNum / (a + 1));
                const c = a * x + b;
                return { equation: `${a}x + ${b} = ${c}`, answer: x, type: 'ax_plus_b' };
            },
            () => { // ax - b = c
                const a = this.randomInt(2, Math.min(5, maxNum / 10));
                const b = this.randomInt(1, maxNum / 5);
                const x = this.randomInt(1, maxNum / (a + 1));
                const c = a * x - b;
                return { equation: `${a}x - ${b} = ${c}`, answer: x, type: 'ax_minus_b' };
            }
        ];
        
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        return pattern();
    }
    
    /**
     * Generate step-by-step solution for a problem
     */
    generateSolutionSteps(problem) {
        const steps = [];
        const { equation, answer, type } = problem;
        
        // Always start with the original equation
        steps.push(equation);
        
        switch(type) {
            case 'x_plus_a':
                this.solveXPlusA(steps, equation, answer);
                break;
            case 'a_plus_x':
                this.solveAPlusX(steps, equation, answer);
                break;
            case 'a_plus_x_plus_c':
                this.solveAPlusXPlusC(steps, equation, answer);
                break;
            case 'x_minus_a':
                this.solveXMinusA(steps, equation, answer);
                break;
            case 'a_minus_x':
                this.solveAMinusX(steps, equation, answer);
                break;
            case 'a_plus_x_minus_c':
                this.solveAPlusXMinusC(steps, equation, answer);
                break;
            case 'a_times_x':
                this.solveATimesX(steps, equation, answer);
                break;
            case 'x_divided_by_a':
                this.solveXDividedByA(steps, equation, answer);
                break;
            case 'a_divided_by_x':
                this.solveADividedByX(steps, equation, answer);
                break;
            case 'ax_plus_b':
                this.solveAXPlusB(steps, equation, answer);
                break;
            case 'ax_minus_b':
                this.solveAXMinusB(steps, equation, answer);
                break;
            default:
                steps.push(`x = ${answer}`);
        }
        
        return steps;
    }
    
    /**
     * Solve x + a = b
     */
    solveXPlusA(steps, equation, answer) {
        const matches = equation.match(/x \+ (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${b} - ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve a + x = b
     */
    solveAPlusX(steps, equation, answer) {
        const matches = equation.match(/(\d+) \+ x = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${b} - ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve a + x + c = b
     */
    solveAPlusXPlusC(steps, equation, answer) {
        const matches = equation.match(/(\d+) \+ x \+ (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const c = parseInt(matches[2]);
            const b = parseInt(matches[3]);
            const sum = a + c;
            steps.push(`x + (${a} + ${c}) = ${b}`);
            steps.push(`x + ${sum} = ${b}`);
            steps.push(`x = ${b} - ${sum}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve x - a = b
     */
    solveXMinusA(steps, equation, answer) {
        const matches = equation.match(/x - (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${b} + ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve a - x = b
     */
    solveAMinusX(steps, equation, answer) {
        const matches = equation.match(/(\d+) - x = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${a} - ${b}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve a + x - c = b
     */
    solveAPlusXMinusC(steps, equation, answer) {
        const matches = equation.match(/(\d+) \+ x - (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const c = parseInt(matches[2]);
            const b = parseInt(matches[3]);
            steps.push(`x - ${c} = ${b} - ${a}`);
            steps.push(`x - ${c} = ${b - a}`);
            steps.push(`x = ${b - a} + ${c}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve ax = b
     */
    solveATimesX(steps, equation, answer) {
        const matches = equation.match(/(\d+)x = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${b} ÷ ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve x/a = b
     */
    solveXDividedByA(steps, equation, answer) {
        const matches = equation.match(/x[\/÷](\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`x = ${b} × ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve a/x = b
     */
    solveADividedByX(steps, equation, answer) {
        const matches = equation.match(/(\d+)[\/÷]x = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            steps.push(`${a} = ${b}x`);
            steps.push(`x = ${a} ÷ ${b}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve ax + b = c
     */
    solveAXPlusB(steps, equation, answer) {
        const matches = equation.match(/(\d+)x \+ (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            const c = parseInt(matches[3]);
            steps.push(`${a}x = ${c} - ${b}`);
            steps.push(`${a}x = ${c - b}`);
            steps.push(`x = ${c - b} ÷ ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Solve ax - b = c
     */
    solveAXMinusB(steps, equation, answer) {
        const matches = equation.match(/(\d+)x - (\d+) = (\d+)/);
        if (matches) {
            const a = parseInt(matches[1]);
            const b = parseInt(matches[2]);
            const c = parseInt(matches[3]);
            steps.push(`${a}x = ${c} + ${b}`);
            steps.push(`${a}x = ${c + b}`);
            steps.push(`x = ${c + b} ÷ ${a}`);
            steps.push(`x = ${answer}`);
        }
    }
    
    /**
     * Check if a character click is correct
     */
    checkCharacterClick(stepIndex, charIndex, expectedChar) {
        const stepKey = `${stepIndex}-${charIndex}`;
        
        if (this.revealedChars.has(stepKey)) {
            return { correct: false, message: 'Already revealed' };
        }
        
        const step = this.currentSolution[stepIndex];
        if (!step || charIndex >= step.length) {
            return { correct: false, message: 'Invalid position' };
        }
        
        const actualChar = step[charIndex];
        if (actualChar === expectedChar || (actualChar === ' ' && expectedChar === ' ')) {
            this.revealedChars.add(stepKey);
            return { correct: true, message: 'Correct!' };
        } else {
            this.mistakeCount++;
            return { correct: false, message: 'Incorrect character' };
        }
    }
    
    /**
     * Get the next character that should be revealed
     */
    getNextCharacter() {
        if (!this.currentSolution || this.currentSolution.length === 0) {
            return null;
        }
        
        for (let stepIndex = 0; stepIndex < this.currentSolution.length; stepIndex++) {
            const step = this.currentSolution[stepIndex];
            for (let charIndex = 0; charIndex < step.length; charIndex++) {
                const stepKey = `${stepIndex}-${charIndex}`;
                if (!this.revealedChars.has(stepKey)) {
                    return {
                        stepIndex,
                        charIndex,
                        char: step[charIndex],
                        step: step
                    };
                }
            }
        }
        
        return null; // All characters revealed
    }
    
    /**
     * Check if the current problem is solved
     */
    isProblemSolved() {
        if (!this.currentSolution || this.currentSolution.length === 0) {
            return false;
        }
        
        // Check if all characters are revealed
        for (let stepIndex = 0; stepIndex < this.currentSolution.length; stepIndex++) {
            const step = this.currentSolution[stepIndex];
            for (let charIndex = 0; charIndex < step.length; charIndex++) {
                const stepKey = `${stepIndex}-${charIndex}`;
                if (!this.revealedChars.has(stepKey)) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    /**
     * Check if game is over (too many mistakes)
     */
    isGameOver() {
        return this.mistakeCount >= this.maxMistakes;
    }
    
    /**
     * Progress to next level
     */
    levelUp() {
        const levelNames = Object.keys(this.levels);
        const currentIndex = levelNames.indexOf(this.currentLevel);
        if (currentIndex < levelNames.length - 1) {
            this.currentLevel = levelNames[currentIndex + 1];
            this.completedProblems = 0;
            return true;
        }
        return false; // Already at max level
    }
    
    /**
     * Reset game state
     */
    reset() {
        this.currentLevel = 'Novice';
        this.mistakeCount = 0;
        this.completedProblems = 0;
        this.revealedChars.clear();
        this.helpButtonClicked = false;
        this.currentProblem = null;
        this.currentSolution = null;
    }
    
    /**
     * Get random philosophical quote
     */
    getRandomQuote() {
        return this.philosophicalQuotes[Math.floor(Math.random() * this.philosophicalQuotes.length)];
    }
    
    /**
     * Utility functions
     */
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    
    weightedRandom(items, weights) {
        const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
        let random = Math.random() * totalWeight;
        
        for (let i = 0; i < items.length; i++) {
            random -= weights[i];
            if (random <= 0) {
                return items[i];
            }
        }
        
        return items[items.length - 1]; // fallback
    }
    
    /**
     * Get current game state
     */
    getGameState() {
        return {
            level: this.currentLevel,
            mistakeCount: this.mistakeCount,
            maxMistakes: this.maxMistakes,
            completedProblems: this.completedProblems,
            revealedChars: Array.from(this.revealedChars),
            helpButtonClicked: this.helpButtonClicked,
            currentProblem: this.currentProblem,
            currentSolution: this.currentSolution
        };
    }
    
    /**
     * Calculate completion percentage
     */
    getCompletionPercentage() {
        if (!this.currentSolution || this.currentSolution.length === 0) {
            return 0;
        }
        
        let totalChars = 0;
        let revealedCount = 0;
        
        for (let stepIndex = 0; stepIndex < this.currentSolution.length; stepIndex++) {
            const step = this.currentSolution[stepIndex];
            totalChars += step.length;
            
            for (let charIndex = 0; charIndex < step.length; charIndex++) {
                const stepKey = `${stepIndex}-${charIndex}`;
                if (this.revealedChars.has(stepKey)) {
                    revealedCount++;
                }
            }
        }
        
        return totalChars > 0 ? (revealedCount / totalChars) * 100 : 0;
    }
}

// Make it globally available
window.MathEngine = MathEngine;