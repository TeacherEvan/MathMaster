/**
 * MathMistress - Main Game Controller
 * Greek Mathematical Wisdom System
 * 
 * This is the main game controller that coordinates all systems and provides
 * the core gameplay experience focusing on mathematical problem-solving with
 * minimal guidance, encouraging the player to request help rather than providing it.
 */

class MathMistressGame {
    constructor() {
        this.mathEngine = new MathEngine();
        this.characterSystem = null;
        this.canvas = null;
        this.ctx = null;
        this.gameState = 'loading';
        this.currentProblemData = null;
        this.solutionElements = [];
        this.isTransitioning = false;
        this.backgroundAnimations = [];
        this.helpTimer = null;
        this.helpHintDelay = 30000; // 30 seconds before subtle help hint
        this.successTimer = null;
        
        // Game UI elements
        this.elements = {
            currentLevel: document.getElementById('currentLevel'),
            mistakeCount: document.getElementById('mistakeCount'),
            maxMistakes: document.getElementById('maxMistakes'),
            philosophicalQuote: document.getElementById('philosophicalQuote'),
            currentEquation: document.getElementById('currentEquation'),
            solutionSteps: document.getElementById('solutionSteps'),
            helpButton: document.getElementById('helpButton'),
            gameOverModal: document.getElementById('gameOverModal'),
            gameOverMessage: document.getElementById('gameOverMessage'),
            restartButton: document.getElementById('restartButton'),
            nextLevelButton: document.getElementById('nextLevelButton'),
            successOverlay: document.getElementById('successOverlay')
        };
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupBackgroundAnimations();
        this.characterSystem = new CharacterSystem(this.canvas, this.mathEngine);
        this.startNewGame();
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas size
        this.resizeCanvas();

        // Setup resize handler using a stable function reference for proper cleanup
        this.resizeHandler = this.resizeCanvas.bind(this);
        window.addEventListener('resize', this.resizeHandler);
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    setupEventListeners() {
        // Help button
        this.elements.helpButton.addEventListener('click', () => {
            this.handleHelpRequest();
        });
        
        // Modal buttons
        this.elements.restartButton.addEventListener('click', () => {
            this.restartGame();
        });
        
        this.elements.nextLevelButton.addEventListener('click', () => {
            this.progressToNextLevel();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyPress(e);
        });
        
        // Solution character clicks
        this.elements.solutionSteps.addEventListener('click', (e) => {
            this.handleSolutionClick(e);
        });
        
        // Prevent context menu on characters
        document.addEventListener('contextmenu', (e) => {
            if (e.target.classList.contains('character')) {
                e.preventDefault();
            }
        });
    }
    
    setupBackgroundAnimations() {
        // Greek mathematical symbols floating in background
        const symbols = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'λ', 'μ', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ψ', 'ω'];
        
        for (let i = 0; i < 15; i++) {
            const symbol = symbols[Math.floor(Math.random() * symbols.length)];
            this.backgroundAnimations.push({
                symbol: symbol,
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                alpha: 0.1 + Math.random() * 0.1,
                size: 20 + Math.random() * 30,
                rotation: Math.random() * Math.PI * 2,
                rotationSpeed: (Math.random() - 0.5) * 0.01
            });
        }
        
        this.animateBackground();
    }
    
    animateBackground() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw floating symbols
        this.backgroundAnimations.forEach(item => {
            this.ctx.save();
            this.ctx.globalAlpha = item.alpha;
            this.ctx.font = `${item.size}px 'Cinzel', serif`;
            this.ctx.fillStyle = '#d4af37';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            // Apply rotation
            this.ctx.translate(item.x, item.y);
            this.ctx.rotate(item.rotation);
            this.ctx.fillText(item.symbol, 0, 0);
            this.ctx.restore();
            
            // Update position
            item.x += item.vx;
            item.y += item.vy;
            item.rotation += item.rotationSpeed;
            
            // Wrap around screen
            if (item.x < -50) item.x = this.canvas.width + 50;
            if (item.x > this.canvas.width + 50) item.x = -50;
            if (item.y < -50) item.y = this.canvas.height + 50;
            if (item.y > this.canvas.height + 50) item.y = -50;
        });
        
        requestAnimationFrame(() => this.animateBackground());
    }
    
    startNewGame() {
        this.gameState = 'playing';
        this.mathEngine.reset();
        this.characterSystem.reset();
        this.loadNewProblem();
        this.updateUI();
    }
    
    loadNewProblem() {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        
        // Clear previous problem
        this.clearSolutionDisplay();
        
        // Generate new problem
        this.currentProblemData = this.mathEngine.generateProblem();
        
        // Update UI
        this.updateProblemDisplay();
        this.createSolutionDisplay();
        
        // Start help timer
        this.startHelpTimer();
        
        this.isTransitioning = false;
    }
    
    updateProblemDisplay() {
        // Update equation
        this.elements.currentEquation.textContent = this.currentProblemData.problem.equation;
        
        // Update philosophical quote
        this.elements.philosophicalQuote.textContent = this.currentProblemData.quote;
        
        // Add fade-in animation
        this.elements.currentEquation.classList.add('fade-in');
        this.elements.philosophicalQuote.classList.add('fade-in');
        
        // Remove animation class after animation
        setTimeout(() => {
            this.elements.currentEquation.classList.remove('fade-in');
            this.elements.philosophicalQuote.classList.remove('fade-in');
        }, 500);
    }
    
    createSolutionDisplay() {
        const solutionContainer = this.elements.solutionSteps;
        solutionContainer.innerHTML = '';
        this.solutionElements = [];
        
        this.currentProblemData.solution.forEach((step, stepIndex) => {
            const stepElement = document.createElement('div');
            stepElement.className = 'solution-step';
            stepElement.dataset.stepIndex = stepIndex;
            
            const stepContent = document.createElement('div');
            stepContent.className = 'step-content';
            
            // Create individual character elements
            const characters = [];
            for (let charIndex = 0; charIndex < step.length; charIndex++) {
                const char = step[charIndex];
                const charElement = document.createElement('span');
                charElement.className = 'clickable-char';
                charElement.textContent = char === ' ' ? '\u00A0' : char; // Non-breaking space
                charElement.dataset.stepIndex = stepIndex;
                charElement.dataset.charIndex = charIndex;
                charElement.dataset.char = char;
                
                // Initially hide all characters
                charElement.style.opacity = '0.3';
                charElement.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                
                characters.push(charElement);
                stepContent.appendChild(charElement);
            }
            
            stepElement.appendChild(stepContent);
            solutionContainer.appendChild(stepElement);
            
            this.solutionElements.push({
                element: stepElement,
                characters: characters,
                step: step,
                stepIndex: stepIndex
            });
        });
    }
    
    clearSolutionDisplay() {
        this.elements.solutionSteps.innerHTML = '';
        this.solutionElements = [];
    }
    
    handleSolutionClick(event) {
        const target = event.target;
        
        if (target.classList.contains('clickable-char')) {
            const stepIndex = parseInt(target.dataset.stepIndex);
            const charIndex = parseInt(target.dataset.charIndex);
            const char = target.dataset.char;
            
            this.handleCharacterClick(stepIndex, charIndex, char, target);
        }
    }
    
    handleCharacterClick(stepIndex, charIndex, char, element) {
        // Check if this is the correct next character
        const nextChar = this.mathEngine.getNextCharacter();
        
        if (!nextChar) {
            // Problem already solved
            return;
        }
        
        const result = this.mathEngine.checkCharacterClick(stepIndex, charIndex, char);
        
        if (result.correct) {
            // Correct character clicked
            this.revealCharacter(element, true);
            
            // Check if problem is solved
            if (this.mathEngine.isProblemSolved()) {
                this.handleProblemSolved();
            }
        } else {
            // Incorrect character clicked
            this.handleIncorrectClick(element, result.message);
            
            // Check if game is over
            if (this.mathEngine.isGameOver()) {
                this.handleGameOver();
            }
        }
        
        this.updateUI();
    }
    
    revealCharacter(element, isCorrect) {
        if (isCorrect) {
            element.style.opacity = '1';
            element.style.backgroundColor = 'rgba(212, 175, 55, 0.3)';
            element.style.color = '#d4af37';
            element.classList.add('revealed');
            
            // Add success animation
            element.classList.add('fade-in');
            setTimeout(() => {
                element.classList.remove('fade-in');
            }, 300);
            
            // Create success particles
            this.createSuccessParticles(element);
        } else {
            element.classList.add('shake-effect');
            setTimeout(() => {
                element.classList.remove('shake-effect');
            }, 500);
        }
    }
    
    createSuccessParticles(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Create small golden particles
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'success-particle';
            particle.style.cssText = `
                position: fixed;
                left: ${centerX}px;
                top: ${centerY}px;
                width: 4px;
                height: 4px;
                background: #d4af37;
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                animation: sparkle 1s ease-out forwards;
            `;
            
            document.body.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 1000);
        }
    }
    
    handleIncorrectClick(element, message) {
        // Visual feedback for incorrect click
        element.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
        element.classList.add('shake-effect');
        
        // Reset after delay
        setTimeout(() => {
            element.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            element.classList.remove('shake-effect');
        }, 500);
        
        // Show mistake message briefly
        this.showMistakeMessage(message);
    }
    
    showMistakeMessage(message) {
        const mistakeElement = document.createElement('div');
        mistakeElement.className = 'mistake-message';
        mistakeElement.textContent = message;
        mistakeElement.style.cssText = `
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(139, 0, 0, 0.9);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            font-family: 'Cinzel', serif;
            font-size: 1.1em;
            border: 2px solid #ff6b6b;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            z-index: 1001;
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(mistakeElement);
        
        // Animate in
        setTimeout(() => {
            mistakeElement.style.opacity = '1';
            mistakeElement.style.transform = 'translate(-50%, -50%) scale(1.1)';
        }, 50);
        
        // Remove after delay
        setTimeout(() => {
            mistakeElement.style.opacity = '0';
            mistakeElement.style.transform = 'translate(-50%, -50%) scale(0.8)';
            setTimeout(() => {
                if (mistakeElement.parentNode) {
                    mistakeElement.parentNode.removeChild(mistakeElement);
                }
            }, 300);
        }, 1500);
    }
    
    handleProblemSolved() {
        this.gameState = 'solved';
        this.mathEngine.completedProblems++;
        
        // Stop help timer
        if (this.helpTimer) {
            clearTimeout(this.helpTimer);
        }
        
        // Show success overlay
        this.showSuccessOverlay();
        
        // Prepare for next problem or level up
        setTimeout(() => {
            this.checkLevelProgression();
        }, 2000);
    }
    
    showSuccessOverlay() {
        const overlay = this.elements.successOverlay;
        overlay.classList.remove('hidden');
        
        // Create celebration particles
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                this.createCelebrationParticle();
            }, i * 100);
        }
        
        // Hide overlay after delay
        setTimeout(() => {
            overlay.classList.add('hidden');
        }, 2000);
    }
    
    createCelebrationParticle() {
        const particle = document.createElement('div');
        particle.className = 'celebration-particle';
        particle.style.cssText = `
            position: fixed;
            left: ${Math.random() * window.innerWidth}px;
            top: ${Math.random() * window.innerHeight}px;
            width: 8px;
            height: 8px;
            background: #d4af37;
            border-radius: 50%;
            pointer-events: none;
            z-index: 1000;
            animation: celebrate 3s ease-out forwards;
        `;
        
        document.body.appendChild(particle);
        
        // Remove after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 3000);
    }
    
    checkLevelProgression() {
        // Check if ready to level up (solve 3 problems per level)
        if (this.mathEngine.completedProblems >= 3) {
            if (this.mathEngine.levelUp()) {
                this.showLevelUpMessage();
            } else {
                this.showMasteryMessage();
            }
        }
        
        // Load next problem
        setTimeout(() => {
            this.loadNewProblem();
        }, 1000);
    }
    
    showLevelUpMessage() {
        const message = document.createElement('div');
        message.className = 'level-up-message';
        message.innerHTML = `
            <h2>ΑΝΑΒΑΣΗ!</h2>
            <p>Ascension to ${this.mathEngine.currentLevel}</p>
            <p>The path of wisdom continues...</p>
        `;
        message.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(107, 142, 35, 0.95);
            color: white;
            padding: 30px;
            border-radius: 20px;
            font-family: 'Cinzel', serif;
            text-align: center;
            border: 3px solid #d4af37;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            z-index: 1001;
            opacity: 0;
            transition: all 0.5s ease;
        `;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.opacity = '1';
            message.style.transform = 'translate(-50%, -50%) scale(1.1)';
        }, 50);
        
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translate(-50%, -50%) scale(0.8)';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 500);
        }, 3000);
    }
    
    showMasteryMessage() {
        const message = document.createElement('div');
        message.className = 'mastery-message';
        message.innerHTML = `
            <h2>ΜΑΘΗΤΕΙΑ ΤΕΛΕΙΑ!</h2>
            <p>Perfect Mastery Achieved!</p>
            <p>You have conquered all levels of mathematical wisdom!</p>
        `;
        message.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(212, 175, 55, 0.95);
            color: #1e3a8a;
            padding: 40px;
            border-radius: 25px;
            font-family: 'Cinzel', serif;
            text-align: center;
            border: 4px solid #1e3a8a;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7);
            z-index: 1001;
            opacity: 0;
            transition: all 0.5s ease;
        `;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.opacity = '1';
            message.style.transform = 'translate(-50%, -50%) scale(1.1)';
        }, 50);
        
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translate(-50%, -50%) scale(0.8)';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 500);
        }, 5000);
    }
    
    handleGameOver() {
        this.gameState = 'gameOver';
        this.characterSystem.setActive(false);
        
        // Stop help timer
        if (this.helpTimer) {
            clearTimeout(this.helpTimer);
        }
        
        // Show game over modal
        this.showGameOverModal();
    }
    
    showGameOverModal() {
        const modal = this.elements.gameOverModal;
        const message = this.elements.gameOverMessage;
        
        message.innerHTML = `
            <p>The Oracle speaks: "Through mistakes comes wisdom."</p>
            <p>You made ${this.mathEngine.mistakeCount} mistakes.</p>
            <p>The path of mathematical enlightenment requires patience and focus.</p>
        `;
        
        modal.classList.remove('hidden');
    }
    
    handleHelpRequest() {
        // This is the key feature: help shows the next step, not explanations
        this.mathEngine.helpButtonClicked = true;
        
        const nextChar = this.mathEngine.getNextCharacter();
        if (nextChar) {
            // Find the corresponding UI element
            const stepElement = this.solutionElements[nextChar.stepIndex];
            const charElement = stepElement.characters[nextChar.charIndex];
            
            // Reveal the next character
            this.mathEngine.revealedChars.add(`${nextChar.stepIndex}-${nextChar.charIndex}`);
            this.revealCharacter(charElement, true);
            
            // Add glow effect to help button
            this.elements.helpButton.classList.add('glow-effect');
            setTimeout(() => {
                this.elements.helpButton.classList.remove('glow-effect');
            }, 1000);
            
            // Check if problem is solved
            if (this.mathEngine.isProblemSolved()) {
                this.handleProblemSolved();
            }
        }
        
        // Restart help timer
        this.startHelpTimer();
    }
    
    startHelpTimer() {
        if (this.helpTimer) {
            clearTimeout(this.helpTimer);
        }
        
        // After 30 seconds, give subtle hint about help button
        this.helpTimer = setTimeout(() => {
            if (this.gameState === 'playing' && !this.mathEngine.helpButtonClicked) {
                this.showHelpHint();
            }
        }, this.helpHintDelay);
    }
    
    showHelpHint() {
        const helpButton = this.elements.helpButton;
        helpButton.classList.add('pulse');
        
        setTimeout(() => {
            helpButton.classList.remove('pulse');
        }, 3000);
    }
    
    handleKeyPress(event) {
        switch(event.key) {
            case 'h':
            case 'H':
                if (this.gameState === 'playing') {
                    this.handleHelpRequest();
                }
                break;
            case 'r':
            case 'R':
                if (this.gameState === 'gameOver') {
                    this.restartGame();
                }
                break;
            case 'Escape':
                // Close any open modals
                this.elements.gameOverModal.classList.add('hidden');
                break;
        }
    }
    
    restartGame() {
        this.elements.gameOverModal.classList.add('hidden');
        this.characterSystem.setActive(true);
        this.startNewGame();
    }
    
    progressToNextLevel() {
        this.elements.gameOverModal.classList.add('hidden');
        this.mathEngine.levelUp();
        this.characterSystem.setActive(true);
        this.startNewGame();
    }
    
    updateUI() {
        // Update level indicator
        this.elements.currentLevel.textContent = this.mathEngine.currentLevel;
        
        // Update mistake counter
        this.elements.mistakeCount.textContent = this.mathEngine.mistakeCount;
        this.elements.maxMistakes.textContent = this.mathEngine.maxMistakes;
        
        // Update progress indicator color based on mistakes
        const mistakeRatio = this.mathEngine.mistakeCount / this.mathEngine.maxMistakes;
        const mistakeCounter = this.elements.mistakeCount.parentElement;
        
        if (mistakeRatio > 0.8) {
            mistakeCounter.style.borderColor = '#ff6b6b';
        } else if (mistakeRatio > 0.6) {
            mistakeCounter.style.borderColor = '#ffa500';
        } else {
            mistakeCounter.style.borderColor = '#d4af37';
        }
    }
    
    destroy() {
        if (this.helpTimer) {
            clearTimeout(this.helpTimer);
        }
        
        if (this.characterSystem) {
            this.characterSystem.destroy();
        }
        
        // Clean up event listener for resize
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }
    }
}

// Initialize the game when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add dynamic CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes celebrate {
            0% { transform: scale(1) rotate(0deg); opacity: 1; }
            50% { transform: scale(1.5) rotate(180deg); opacity: 0.7; }
            100% { transform: scale(0) rotate(360deg); opacity: 0; }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .pulse {
            animation: pulse 1s ease-in-out infinite;
        }
        
        .success-particle {
            animation: sparkle 1s ease-out forwards;
        }
        
        .celebration-particle {
            animation: celebrate 3s ease-out forwards;
        }
    `;
    document.head.appendChild(style);
    
    // Start the game
    window.mathMistressGame = new MathMistressGame();
});

// Make the game globally available
window.MathMistressGame = MathMistressGame;