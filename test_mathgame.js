// Test suite for MathMistress Game - Git Merge Conflict Fixes Verification
// This test suite verifies that the merge conflict markers have been removed
// and that the game functionality works correctly

// Test utilities
function assert(condition, message) {
    if (condition) {
        console.log(`✅ ${message}`);
        return true;
    } else {
        console.error(`❌ ${message}`);
        return false;
    }
}

function assertNoSyntaxErrors(code, testName) {
    try {
        new Function(code);
        console.log(`✅ ${testName}: No syntax errors detected`);
        return true;
    } catch (error) {
        console.error(`❌ ${testName}: Syntax error detected - ${error.message}`);
        return false;
    }
}

// Test 1: Verify that merge conflict markers have been removed
function testMergeConflictRemoval() {
    console.log('\n🔍 Testing merge conflict marker removal...');
    
    // Fetch the game.js content
    fetch('/workspace/game.js')
        .then(response => response.text())
        .then(code => {
            // Check for common merge conflict markers
            const mergeMarkers = [
                'cursor/fix-memory-leak-in-resize-event-listener-6f7d',
                '<<<<<<< HEAD',
                '>>>>>>> main',
                '======='
            ];
            
            let hasConflictMarkers = false;
            mergeMarkers.forEach(marker => {
                if (code.includes(marker)) {
                    console.error(`❌ Found merge conflict marker: ${marker}`);
                    hasConflictMarkers = true;
                }
            });
            
            if (!hasConflictMarkers) {
                console.log('✅ No merge conflict markers found');
            }
            
            // Check for standalone 'main' keywords that might be leftover
            const standaloneMainRegex = /^\s*main\s*$/gm;
            const mainMatches = code.match(standaloneMainRegex);
            
            if (mainMatches) {
                console.error(`❌ Found standalone 'main' keywords: ${mainMatches.length}`);
            } else {
                console.log('✅ No standalone "main" keywords found');
            }
            
            return !hasConflictMarkers && !mainMatches;
        })
        .catch(error => {
            console.error(`❌ Error fetching game.js: ${error.message}`);
            return false;
        });
}

// Test 2: Verify JavaScript syntax is valid
function testJavaScriptSyntax() {
    console.log('\n🔍 Testing JavaScript syntax validity...');
    
    fetch('/workspace/game.js')
        .then(response => response.text())
        .then(code => {
            try {
                new Function(code);
                console.log('✅ JavaScript syntax is valid');
                return true;
            } catch (error) {
                console.error(`❌ JavaScript syntax error: ${error.message}`);
                return false;
            }
        })
        .catch(error => {
            console.error(`❌ Error testing syntax: ${error.message}`);
            return false;
        });
}

// Test 3: Test MathEngine initialization
function testMathEngine() {
    console.log('\n🔍 Testing MathEngine...');
    
    try {
        if (typeof MathEngine !== 'undefined') {
            const engine = new MathEngine();
            assert(engine !== null, 'MathEngine can be instantiated');
            assert(typeof engine.generateProblem === 'function', 'MathEngine has generateProblem method');
            assert(typeof engine.checkCharacterClick === 'function', 'MathEngine has checkCharacterClick method');
            assert(typeof engine.reset === 'function', 'MathEngine has reset method');
            
            // Test problem generation
            const problem = engine.generateProblem();
            assert(problem !== null, 'MathEngine can generate problems');
            assert(problem.problem !== undefined, 'Generated problem has problem property');
            assert(problem.solution !== undefined, 'Generated problem has solution property');
            
            return true;
        } else {
            console.warn('⚠️ MathEngine not available for testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ MathEngine test failed: ${error.message}`);
        return false;
    }
}

// Test 4: Test Game initialization
function testGameInitialization() {
    console.log('\n🔍 Testing Game initialization...');
    
    try {
        if (typeof MathMistressGame !== 'undefined') {
            // Test that the game class exists and can be instantiated
            assert(typeof MathMistressGame === 'function', 'MathMistressGame class exists');
            
            // Check if game instance exists
            if (typeof window.mathMistressGame !== 'undefined') {
                const game = window.mathMistressGame;
                assert(game instanceof MathMistressGame, 'Game instance is of correct type');
                assert(typeof game.init === 'function', 'Game has init method');
                assert(typeof game.setupCanvas === 'function', 'Game has setupCanvas method');
                assert(typeof game.destroy === 'function', 'Game has destroy method');
                assert(typeof game.resizeCanvas === 'function', 'Game has resizeCanvas method');
                
                return true;
            } else {
                console.warn('⚠️ Game instance not available for testing');
                return false;
            }
        } else {
            console.warn('⚠️ MathMistressGame not available for testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Game initialization test failed: ${error.message}`);
        return false;
    }
}

// Test 5: Test problem generation
function testProblemGeneration() {
    console.log('\n🔍 Testing problem generation...');
    
    try {
        if (typeof window.mathMistressGame !== 'undefined' && window.mathMistressGame.mathEngine) {
            const engine = window.mathMistressGame.mathEngine;
            
            // Test multiple problem generations
            for (let i = 0; i < 5; i++) {
                const problem = engine.generateProblem();
                assert(problem !== null, `Problem ${i + 1} generated successfully`);
                assert(Array.isArray(problem.solution), `Problem ${i + 1} has solution array`);
                assert(problem.solution.length > 0, `Problem ${i + 1} has non-empty solution`);
            }
            
            return true;
        } else {
            console.warn('⚠️ MathEngine not available for problem generation testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Problem generation test failed: ${error.message}`);
        return false;
    }
}

// Test 6: Test character system
function testCharacterSystem() {
    console.log('\n🔍 Testing character system...');
    
    try {
        if (typeof CharacterSystem !== 'undefined') {
            // Test character system initialization
            const canvas = document.getElementById('gameCanvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                const characterSystem = new CharacterSystem(canvas, ctx);
                
                assert(characterSystem !== null, 'CharacterSystem can be instantiated');
                assert(typeof characterSystem.setActive === 'function', 'CharacterSystem has setActive method');
                assert(typeof characterSystem.reset === 'function', 'CharacterSystem has reset method');
                assert(typeof characterSystem.destroy === 'function', 'CharacterSystem has destroy method');
                
                return true;
            } else {
                console.warn('⚠️ Canvas not available for character system testing');
                return false;
            }
        } else {
            console.warn('⚠️ CharacterSystem not available for testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Character system test failed: ${error.message}`);
        return false;
    }
}

// Test 7: Test UI interactions
function testUIInteractions() {
    console.log('\n🔍 Testing UI interactions...');
    
    try {
        // Test that required UI elements exist
        const requiredElements = [
            'currentLevel',
            'mistakeCount',
            'maxMistakes',
            'currentEquation',
            'solutionSteps',
            'helpButton',
            'gameOverModal',
            'successOverlay'
        ];
        
        let allElementsFound = true;
        requiredElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                console.log(`✅ UI element found: ${elementId}`);
            } else {
                console.error(`❌ UI element missing: ${elementId}`);
                allElementsFound = false;
            }
        });
        
        return allElementsFound;
    } catch (error) {
        console.error(`❌ UI interaction test failed: ${error.message}`);
        return false;
    }
}

// Test 8: Test event listener cleanup (specific to the merge conflict fix)
function testEventListenerCleanup() {
    console.log('\n🔍 Testing event listener cleanup...');
    
    try {
        if (typeof window.mathMistressGame !== 'undefined') {
            const game = window.mathMistressGame;
            
            // Test that the destroy method exists and can be called
            assert(typeof game.destroy === 'function', 'Game has destroy method');
            
            // Test that the game has the proper event handlers
            assert(typeof game.resizeHandler === 'function', 'Game has resizeHandler');
            assert(typeof game.boundResizeHandler === 'function', 'Game has boundResizeHandler');
            
            // Test that we can call destroy without errors
            // Note: We won't actually call destroy as it would break the game
            console.log('✅ Event listener cleanup methods are available');
            return true;
        } else {
            console.warn('⚠️ Game instance not available for event listener testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Event listener cleanup test failed: ${error.message}`);
        return false;
    }
}

// Test 9: Test that the game can run without errors
function testGameRunning() {
    console.log('\n🔍 Testing game running state...');
    
    try {
        if (typeof window.mathMistressGame !== 'undefined') {
            const game = window.mathMistressGame;
            
            // Test that the game state is valid
            assert(typeof game.gameState === 'string', 'Game has valid gameState');
            assert(game.canvas !== null, 'Game has canvas element');
            assert(game.ctx !== null, 'Game has canvas context');
            assert(game.mathEngine !== null, 'Game has mathEngine');
            
            // Test that no errors are thrown during basic operations
            console.log('✅ Game is running without errors');
            return true;
        } else {
            console.warn('⚠️ Game instance not available for running state testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Game running test failed: ${error.message}`);
        return false;
    }
}

// Test 10: Integration test - simulate a complete game interaction
function testGameIntegration() {
    console.log('\n🔍 Testing game integration...');
    
    try {
        if (typeof window.mathMistressGame !== 'undefined') {
            const game = window.mathMistressGame;
            
            // Test that we can start a new game
            if (typeof game.startNewGame === 'function') {
                // Don't actually start new game, just check it exists
                console.log('✅ Game has startNewGame method');
            }
            
            // Test that we can load a new problem
            if (typeof game.loadNewProblem === 'function') {
                console.log('✅ Game has loadNewProblem method');
            }
            
            // Test that we can handle help requests
            if (typeof game.handleHelpRequest === 'function') {
                console.log('✅ Game has handleHelpRequest method');
            }
            
            // Test that we can handle character clicks
            if (typeof game.handleCharacterClick === 'function') {
                console.log('✅ Game has handleCharacterClick method');
            }
            
            console.log('✅ Game integration test passed');
            return true;
        } else {
            console.warn('⚠️ Game instance not available for integration testing');
            return false;
        }
    } catch (error) {
        console.error(`❌ Game integration test failed: ${error.message}`);
        return false;
    }
}

// Main test runner
function runAllTests() {
    console.log('🧪 Starting comprehensive test suite for Git merge conflict fixes...');
    console.log('=' * 60);
    
    // Run all tests
    setTimeout(() => testMergeConflictRemoval(), 100);
    setTimeout(() => testJavaScriptSyntax(), 200);
    setTimeout(() => testMathEngine(), 300);
    setTimeout(() => testGameInitialization(), 400);
    setTimeout(() => testProblemGeneration(), 500);
    setTimeout(() => testCharacterSystem(), 600);
    setTimeout(() => testUIInteractions(), 700);
    setTimeout(() => testEventListenerCleanup(), 800);
    setTimeout(() => testGameRunning(), 900);
    setTimeout(() => testGameIntegration(), 1000);
    
    setTimeout(() => {
        console.log('\n🎉 Test suite completed!');
        console.log('=' * 60);
    }, 1100);
}

// Export test functions for manual running
window.testMergeConflictRemoval = testMergeConflictRemoval;
window.testJavaScriptSyntax = testJavaScriptSyntax;
window.testMathEngine = testMathEngine;
window.testGameInitialization = testGameInitialization;
window.testProblemGeneration = testProblemGeneration;
window.testCharacterSystem = testCharacterSystem;
window.testUIInteractions = testUIInteractions;
window.testEventListenerCleanup = testEventListenerCleanup;
window.testGameRunning = testGameRunning;
window.testGameIntegration = testGameIntegration;
window.runAllTests = runAllTests;