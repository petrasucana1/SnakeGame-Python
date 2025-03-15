# Snake Game with Obstacles

This is a simple yet fun Snake Game built using Python and Pygame, where the player controls a snake that grows longer as it eats food and must avoid colliding with itself or obstacles.  
The game includes basic sound effects, a configuration file to set up game parameters, and a scoring system that tracks the player's performance.

## Features:
### Snake Movement:
The player controls the snake's movement using the arrow keys.

### Food:
The snake eats food that appears randomly on the board, increasing the player's score.

### Obstacles:
The game gradually adds obstacles every 3 points scored, increasing difficulty.

### Boundaries:
The snake wraps around the board when it moves past the edges, reappearing on the opposite side.

### Game Over:
If the snake collides with itself or an obstacle, the game ends and the score is displayed.

### Sound Effects:
Includes custom sound effects for eating food and when the game is over.



## How it Works:
### Configuration:
The game is configured using a JSON file, where the board size, obstacle positions, and other parameters are defined.

### Game Loop:
The main game loop handles user input, updates the snake's position, checks for collisions, and renders the game screen.

### Snake Evolution:
The snake's position updates every frame, growing when it eats food. The game generates new food and places obstacles as the player progresses.

### Collision Detection:
The game verifies if the snake collides with itself or the obstacles and ends the game if a collision occurs.

---

The **Snake Game with Obstacles** is a beginner-friendly project that I created as an introduction to **Pygame**. It has a simple structure and is easy to modify for further enhancements.  
It was fun learning how to implement game mechanics, handle user input, and integrate sounds. While not highly complex, it was a great starting point for my journey into game development with Pygame!

## **VIDEO:**
[Watch the gameplay](https://youtube.com/shorts/46-FgUI1zSY?feature=share)

## **PHOTOS:**
![Photo](https://github.com/user-attachments/assets/bcf33225-3a29-4cc2-9575-6ecd14f5463a)  
![Game Over](https://github.com/user-attachments/assets/a12e7098-85bb-4e7a-ae11-c27c3c12aaf4)
