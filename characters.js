/**
 * MathMistress - Character System
 * Dionysus and Quetzalcoatl - Distracting Characters
 * 
 * These characters attempt to break the player's focus with various distractions
 * and temptations, embodying the philosophical struggle between discipline and temptation.
 */

class CharacterSystem {
    constructor(canvas, gameEngine) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.gameEngine = gameEngine;
        this.characters = new Map();
        this.activeAnimations = new Map();
        this.distractionTimer = null;
        this.distractionInterval = 8000; // 8 seconds between distractions
        this.isActive = true;
        
        // Character personalities and behaviors
        this.characterData = {
            dionysus: {
                name: 'Dionysus',
                element: document.getElementById('dionysus'),
                bubble: document.getElementById('dionysusBubble'),
                color: '#8b0000',
                personality: 'celebratory',
                distractions: [
                    '🍷 Why solve equations when you can solve life?',
                    '🎭 Mathematics is boring! Let\'s celebrate!',
                    '🍇 Come, drink wine and forget your troubles!',
                    '🎪 The festival awaits! Leave these numbers behind!',
                    '🎵 Dance to the rhythm of chaos, not order!',
                    '🌪️ Embrace the wild side of life!',
                    '🎨 Art is more beautiful than mathematics!',
                    '🍯 Sweet pleasures over bitter calculations!',
                    '🌙 The night calls for revelry, not study!',
                    '🎲 Take risks! Click me instead!'
                ],
                position: { x: 0.8, y: 0.2 },
                movements: [
                    { type: 'bounce', amplitude: 30, frequency: 0.003 },
                    { type: 'sway', amplitude: 20, frequency: 0.002 },
                    { type: 'pulse', amplitude: 1.2, frequency: 0.004 }
                ]
            },
            quetzalcoatl: {
                name: 'Quetzalcoatl',
                element: document.getElementById('quetzalcoatl'),
                bubble: document.getElementById('quetzalcoatlBubble'),
                color: '#6b8e23',
                personality: 'cunning',
                distractions: [
                    '🐍 The serpent knows all shortcuts to wisdom...',
                    '🌟 Why work when you can have instant answers?',
                    '⚡ Lightning quick solutions await you here!',
                    '🔮 The crystal ball shows the answer... click me!',
                    '🌀 Spiral into easy solutions, avoid the hard path!',
                    '🗝️ I hold the key to effortless knowledge!',
                    '💎 Precious gems of wisdom, no effort required!',
                    '🌊 Flow with the current, resist the struggle!',
                    '🕊️ Freedom from mathematical chains!',
                    '✨ Magic reveals what effort cannot!'
                ],
                position: { x: 0.1, y: 0.7 },
                movements: [
                    { type: 'slither', amplitude: 40, frequency: 0.0025 },
                    { type: 'circle', radius: 25, frequency: 0.003 },
                    { type: 'fade', amplitude: 0.3, frequency: 0.0035 }
                ]
            }
        };
        
        this.particleSystem = [];
        this.maxParticles = 50;
        this.distractionLevel = 1;
        this.lastDistractionTime = 0;
        this.playerFocusLevel = 100;
        this.focusDecayRate = 0.5;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startDistractionCycle();
        this.render();
    }
    
    setupEventListeners() {
        // Dionysus interactions
        const dionysus = this.characterData.dionysus.element;
        const dionysusBubble = this.characterData.dionysus.bubble;
        
        dionysus.addEventListener('click', (e) => {
            this.handleCharacterClick('dionysus', e);
        });
        
        dionysus.addEventListener('mouseenter', () => {
            this.showCharacterBubble('dionysus');
        });
        
        dionysus.addEventListener('mouseleave', () => {
            this.hideCharacterBubble('dionysus');
        });
        
        // Quetzalcoatl interactions
        const quetzalcoatl = this.characterData.quetzalcoatl.element;
        const quetzalcoatlBubble = this.characterData.quetzalcoatl.bubble;
        
        quetzalcoatl.addEventListener('click', (e) => {
            this.handleCharacterClick('quetzalcoatl', e);
        });
        
        quetzalcoatl.addEventListener('mouseenter', () => {
            this.showCharacterBubble('quetzalcoatl');
        });
        
        quetzalcoatl.addEventListener('mouseleave', () => {
            this.hideCharacterBubble('quetzalcoatl');
        });
    }
    
    handleCharacterClick(characterName, event) {
        event.preventDefault();
        event.stopPropagation();
        
        const character = this.characterData[characterName];
        
        // Add mistake to game engine
        this.gameEngine.mistakeCount++;
        
        // Create distraction effect
        this.createDistractionEffect(character);
        
        // Show temptation message
        this.showTemptationMessage(character);
        
        // Increase distraction level
        this.distractionLevel = Math.min(this.distractionLevel + 0.2, 5);
        
        // Reduce player focus
        this.playerFocusLevel = Math.max(this.playerFocusLevel - 10, 0);
        
        // Play distraction sound effect (visual feedback)
        this.playDistractionEffect(characterName);
        
        // Update game UI
        this.updateGameUI();
    }
    
    showCharacterBubble(characterName) {
        const character = this.characterData[characterName];
        const bubble = character.bubble;
        
        // Select random distraction message
        const message = this.getRandomDistraction(character);
        bubble.textContent = message;
        
        // Show bubble with animation
        bubble.style.opacity = '0';
        bubble.style.transform = 'translate(-50%, -120%)';
        
        // Animate in
        setTimeout(() => {
            bubble.style.opacity = '1';
            bubble.style.transform = 'translate(-50%, -140%)';
        }, 50);
    }
    
    hideCharacterBubble(characterName) {
        const character = this.characterData[characterName];
        const bubble = character.bubble;
        
        // Hide bubble with animation
        bubble.style.opacity = '0';
        bubble.style.transform = 'translate(-50%, -120%)';
    }
    
    getRandomDistraction(character) {
        const distractions = character.distractions;
        return distractions[Math.floor(Math.random() * distractions.length)];
    }
    
    createDistractionEffect(character) {
        const element = character.element;
        const rect = element.getBoundingClientRect();
        
        // Create particle burst
        for (let i = 0; i < 10; i++) {
            this.createParticle(
                rect.left + rect.width / 2,
                rect.top + rect.height / 2,
                character.color
            );
        }
        
        // Add shake effect to character
        element.classList.add('shake-effect');
        setTimeout(() => {
            element.classList.remove('shake-effect');
        }, 500);
    }
    
    createParticle(x, y, color) {
        const particle = {
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 10,
            vy: (Math.random() - 0.5) * 10,
            color: color,
            life: 1.0,
            decay: 0.02,
            size: Math.random() * 6 + 2
        };
        
        this.particleSystem.push(particle);
        
        // Remove excess particles
        if (this.particleSystem.length > this.maxParticles) {
            this.particleSystem.shift();
        }
    }
    
    showTemptationMessage(character) {
        const message = this.getRandomDistraction(character);
        
        // Create floating message
        const messageElement = document.createElement('div');
        messageElement.className = 'temptation-message';
        messageElement.textContent = message;
        messageElement.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.9);
            color: ${character.color};
            padding: 20px 30px;
            border-radius: 15px;
            font-family: 'Cinzel', serif;
            font-size: 1.2em;
            font-weight: 600;
            border: 2px solid ${character.color};
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            z-index: 1001;
            max-width: 400px;
            text-align: center;
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(messageElement);
        
        // Animate in
        setTimeout(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translate(-50%, -50%) scale(1.1)';
        }, 50);
        
        // Remove after delay
        setTimeout(() => {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translate(-50%, -50%) scale(0.8)';
            setTimeout(() => {
                document.body.removeChild(messageElement);
            }, 300);
        }, 2000);
    }
    
    playDistractionEffect(characterName) {
        const character = this.characterData[characterName];
        const element = character.element;
        
        // Visual feedback effects
        element.style.filter = 'brightness(1.5) drop-shadow(0 0 20px currentColor)';
        element.style.transform = 'scale(1.3)';
        
        setTimeout(() => {
            element.style.filter = '';
            element.style.transform = '';
        }, 300);
    }
    
    startDistractionCycle() {
        this.distractionTimer = setInterval(() => {
            if (this.isActive && this.gameEngine.currentProblem) {
                this.triggerRandomDistraction();
            }
        }, this.distractionInterval);
    }
    
    triggerRandomDistraction() {
        const characters = Object.keys(this.characterData);
        const randomCharacter = characters[Math.floor(Math.random() * characters.length)];
        const character = this.characterData[randomCharacter];
        
        // Increase distraction intensity based on player's progress
        const completion = this.gameEngine.getCompletionPercentage();
        if (completion > 50) {
            this.distractionLevel = Math.min(this.distractionLevel + 0.1, 5);
        }
        
        // Trigger distraction
        this.createAmbientDistraction(character);
        
        // Adjust interval based on distraction level
        clearInterval(this.distractionTimer);
        const newInterval = Math.max(3000, this.distractionInterval - (this.distractionLevel * 500));
        this.distractionInterval = newInterval;
        this.startDistractionCycle();
    }
    
    createAmbientDistraction(character) {
        const element = character.element;
        
        // Add glow effect
        element.classList.add('glow-effect');
        
        // Show brief message
        this.showCharacterBubble(character.name.toLowerCase());
        
        // Remove glow after delay
        setTimeout(() => {
            element.classList.remove('glow-effect');
            this.hideCharacterBubble(character.name.toLowerCase());
        }, 2000);
        
        // Create ambient particles
        const rect = element.getBoundingClientRect();
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                this.createParticle(
                    rect.left + rect.width / 2 + (Math.random() - 0.5) * 40,
                    rect.top + rect.height / 2 + (Math.random() - 0.5) * 40,
                    character.color
                );
            }, i * 200);
        }
    }
    
    updateCharacterAnimations() {
        const time = Date.now();
        
        for (const [name, character] of Object.entries(this.characterData)) {
            const element = character.element;
            const movements = character.movements;
            
            let transform = '';
            let opacity = 1;
            
            // Apply multiple movement types
            movements.forEach(movement => {
                switch (movement.type) {
                    case 'bounce':
                        const bounceY = Math.sin(time * movement.frequency) * movement.amplitude;
                        transform += `translateY(${bounceY}px) `;
                        break;
                        
                    case 'sway':
                        const swayX = Math.sin(time * movement.frequency) * movement.amplitude;
                        transform += `translateX(${swayX}px) `;
                        break;
                        
                    case 'pulse':
                        const scale = 1 + Math.sin(time * movement.frequency) * (movement.amplitude - 1);
                        transform += `scale(${scale}) `;
                        break;
                        
                    case 'slither':
                        const slitherX = Math.sin(time * movement.frequency) * movement.amplitude;
                        const slitherY = Math.cos(time * movement.frequency * 0.7) * (movement.amplitude * 0.5);
                        transform += `translate(${slitherX}px, ${slitherY}px) `;
                        break;
                        
                    case 'circle':
                        const circleX = Math.cos(time * movement.frequency) * movement.radius;
                        const circleY = Math.sin(time * movement.frequency) * movement.radius;
                        transform += `translate(${circleX}px, ${circleY}px) `;
                        break;
                        
                    case 'fade':
                        opacity = 1 - Math.sin(time * movement.frequency) * movement.amplitude;
                        break;
                }
            });
            
            // Apply distraction level multiplier
            if (this.distractionLevel > 1) {
                const multiplier = 1 + (this.distractionLevel - 1) * 0.3;
                transform += `scale(${multiplier}) `;
            }
            
            element.style.transform = transform;
            element.style.opacity = opacity;
        }
    }
    
    updateParticles() {
        for (let i = this.particleSystem.length - 1; i >= 0; i--) {
            const particle = this.particleSystem[i];
            
            // Update particle physics
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vy += 0.3; // gravity
            particle.life -= particle.decay;
            
            // Remove dead particles
            if (particle.life <= 0) {
                this.particleSystem.splice(i, 1);
            }
        }
    }
    
    renderParticles() {
        const container = document.getElementById('particleContainer');
        if (!container) return;
        
        // Clear existing particles
        container.innerHTML = '';
        
        // Render active particles
        this.particleSystem.forEach(particle => {
            const element = document.createElement('div');
            element.className = 'particle';
            element.style.cssText = `
                position: absolute;
                left: ${particle.x}px;
                top: ${particle.y}px;
                width: ${particle.size}px;
                height: ${particle.size}px;
                background: ${particle.color};
                border-radius: 50%;
                opacity: ${particle.life};
                pointer-events: none;
                transform: translate(-50%, -50%);
            `;
            container.appendChild(element);
        });
    }
    
    updateGameUI() {
        // Update mistake counter
        const mistakeCount = document.getElementById('mistakeCount');
        if (mistakeCount) {
            mistakeCount.textContent = this.gameEngine.mistakeCount;
        }
        
        // Update focus level indicator (visual feedback)
        const focusIndicator = document.querySelector('.focus-indicator');
        if (focusIndicator) {
            focusIndicator.style.width = `${this.playerFocusLevel}%`;
        }
    }
    
    render() {
        this.updateCharacterAnimations();
        this.updateParticles();
        this.renderParticles();
        
        // Update player focus (decays over time)
        this.playerFocusLevel = Math.max(
            this.playerFocusLevel - this.focusDecayRate * (this.distractionLevel / 60),
            0
        );
        
        requestAnimationFrame(() => this.render());
    }
    
    setActive(active) {
        this.isActive = active;
        
        if (!active) {
            // Hide all characters
            Object.values(this.characterData).forEach(character => {
                character.element.style.display = 'none';
            });
            
            // Clear particles
            this.particleSystem = [];

            // Remove all event listeners on character elements by replacing them with clean clones
            Object.values(this.characterData).forEach(({ element }) => {
                if (element && element.parentNode) {
                    const cleanClone = element.cloneNode(true);
                    element.parentNode.replaceChild(cleanClone, element);
                }
            });
        } else {
            // Show all characters
            Object.values(this.characterData).forEach(character => {
                character.element.style.display = 'block';
            });
            
            // Restart distraction cycle
            this.startDistractionCycle();
        }
    }
    
    reset() {
        this.distractionLevel = 1;
        this.playerFocusLevel = 100;
        this.particleSystem = [];
        this.lastDistractionTime = 0;
        this.distractionInterval = 8000;
        
        // Reset character positions and effects
        Object.values(this.characterData).forEach(character => {
            character.element.style.transform = '';
            character.element.style.opacity = '1';
            character.element.classList.remove('glow-effect', 'shake-effect');
        });
        
        // Restart distraction cycle
        if (this.distractionTimer) {
            clearInterval(this.distractionTimer);
        }
        this.startDistractionCycle();
    }
    
    destroy() {
        if (this.distractionTimer) {
            clearInterval(this.distractionTimer);
        }
        
        this.particleSystem = [];

        // Remove all event listeners on character elements by replacing them with clean clones
        Object.values(this.characterData).forEach(({ element }) => {
            if (element && element.parentNode) {
                const cleanClone = element.cloneNode(true);
                element.parentNode.replaceChild(cleanClone, element);
            }
        });

        this.setActive(false);
    }
}

// Make it globally available
window.CharacterSystem = CharacterSystem;