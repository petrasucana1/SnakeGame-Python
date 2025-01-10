import pygame
import sys
import json
import random
import os

pygame.mixer.init() 

CELL_SIZE = 20 
FPS = 8 

class SnakeGame:
    def __init__(self, config_file):
        """
        Initializes the Snake game with the specified configuration file.

        Args:
            config_file (str): Path to the JSON configuration file.

        Attributes:
            width (int): Width of the game board in cells.
            height (int): Height of the game board in cells.
            obstacles (list): List of obstacle positions from the configuration file.
            screen (pygame.Surface): Game screen surface.
            clock (pygame.time.Clock): Clock to control the game's FPS.
            snake (list): List of dictionaries representing the snake's body segments.
            direction (str): Current direction of the snake's movement.
            food (dict): Current position of the food on the board.
            score (int): Current score of the player.
            high_score (int): The highest score achieved during the session.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file is not a valid JSON.
        """

        try:
            with open(config_file, 'r') as file:
                configuration = json.load(file)
        except FileNotFoundError:
            print("Error: Configuration file not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Configuration file is not a valid JSON.")
            sys.exit(1)

        self.width = configuration["width"]
        self.height = configuration["height"]
        self.obstacles = configuration["obstacles"]

        pygame.init()

        try:
            self.eat_sound = pygame.mixer.Sound('bite.mp3')  
        except pygame.error:
            print("Error: 'bite.mp3' sound file not found.")
            sys.exit(1)

        try:
            self.game_over_sound = pygame.mixer.Sound('game_over.wav') 
        except pygame.error:
            print("Error: 'game_over.wav' sound file not found.")
            sys.exit(1)

        self.screen = pygame.display.set_mode((self.width * CELL_SIZE, self.height * CELL_SIZE))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock() 

        self.new_game()
        self.high_score = 0
    
    def new_game(self):
        """
        Resets the game state for a new game session.

        Initializes the snake's position, direction, food, and obstacles.
        """
        self.snake = [{"x":0, "y":0}]
        self.direction = "RIGHT"
        self.food = self.generate_food()
        self.score = 0
        self.active_obstacles = self.obstacles[:3]

    def generate_food(self):
        """
        Generates a random position for the food that does not overlap with the snake or obstacles.

        Returns:
            dict: Position of the food as a dictionary with 'x' and 'y' keys.
        """
        food_position = {"x":random.randint(0,self.width-1), "y":random.randint(0, self.height-1)}

        while food_position in self.snake and food_position in self.active_obstacles:
             food_position = {"x":random.randint(0,self.width-1), "y":random.randint(0, self.height-1)}

        return food_position
    
    def table_drawing(self):
        """
        Draws the game board grid on the screen.
        """
        for x in range(self.width):
            for y in range(self.height):
                cell = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (200, 200, 200), cell)  
                pygame.draw.rect(self.screen, (255, 255, 255), cell, 1) 

    def snake_drawing(self):
        """
        Draws the snake on the screen.
        """
        for snake_part in self.snake:
            cell = pygame.Rect(snake_part["x"] * CELL_SIZE, snake_part["y"] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, (0, 150, 0), cell)
            pygame.draw.rect(self.screen, (0, 50, 0), cell, 1) 
    
    def food_drawing(self):
        """
        Draws the food on the screen.
        """
        cell = pygame.Rect(self.food["x"] * CELL_SIZE, self.food["y"] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (200, 200, 0), cell)  
        pygame.draw.rect(self.screen, (255, 230, 0), cell, 2) 


    def obstacles_drawing(self):
        """
        Draws the obstacles on the screen.
        """
        for obstacle in self.active_obstacles:
            cell = pygame.Rect(obstacle["x"] * CELL_SIZE, obstacle["y"] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, (150, 0, 0), cell)
            pygame.draw.rect(self.screen, (255, 50, 50), cell, 2)

    def snake_evolution(self):
        """
        Updates the snake's position and checks for interactions with food or obstacles.

        - Moves the snake in the current direction.
        - Handles teleportation when crossing the board boundaries.
        - Checks if the snake eats the food and grows in size.
        - Adds new obstacles every 3 points scored.
        """
        head = self.snake[0].copy()

        if self.direction == "UP":
            head["y"] = head["y"] - 1
        elif self.direction == "DOWN":
            head["y"] = head["y"] + 1
        elif self.direction == "LEFT":
            head["x"] = head["x"] - 1
        elif self.direction == "RIGHT": 
            head["x"] = head["x"] + 1

        if head["x"] < 0:  
            head["x"] = self.width - 1  
        elif head["x"] >= self.width:  
            head["x"] = 0 

        if head["y"] < 0: 
            head["y"] = self.height - 1  
        elif head["y"] >= self.height:  
            head["y"] = 0 
        
        self.snake.insert(0, head)

        if head == self.food:
            self.score = self.score + 1
            self.food = self.generate_food()
            self.eat_sound.play()

            if self.score % 3 == 0 and len(self.active_obstacles) < len(self.obstacles):
                self.active_obstacles.append(self.obstacles[len(self.active_obstacles)])
        else:
            self.snake.pop()    

    def collision_verification(self):
        """
        Checks if the snake collides with itself or obstacles.

        Returns:
            bool: True if a collision occurs, otherwise False.
        """
        head = self.snake[0]

        if head in self.snake[1:] or head in self.active_obstacles:
            return True
        return False
    
    def end_game(self):
        """
        Displays the "Game Over" screen and resets the game.

        - Shows the player's score and the high score.
        - Plays the "Game Over" sound.
        - Waits for 2 seconds before resetting the game.
        """
        font = pygame.font.Font(None, 36)

        self.game_over_sound.play()

        text = font.render(f"Game Over! Your Score: {self.score}", True, (150, 0, 0))
        self.screen.blit(text, (self.width * CELL_SIZE // 2 - text.get_width() // 2, self.height * CELL_SIZE // 2 ))

        text = font.render(f"High Score: {self.high_score}", True, (0, 150, 0))
        self.screen.blit(text, (self.width * CELL_SIZE // 2 - text.get_width() // 2, self.height * CELL_SIZE // 2 + 40))
        
        pygame.display.flip() #actualizare ecran cu textul
        pygame.time.wait(2000) #asteapta 2 secunde

    def run(self):
        """
        Main loop of the game.

        - Handles events (key presses, quitting).
        - Updates game state.
        - Renders the game on the screen.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.direction = "RIGHT"

            self.snake_evolution()

            if self.collision_verification():
                self.high_score = max(self.high_score, self.score)
                self.end_game()
                self.new_game()

            self.screen.fill((0, 0, 0))
            self.table_drawing()
            self.snake_drawing()
            self.food_drawing()
            self.obstacles_drawing()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No configuration file provided.")
        sys.exit(1)

    config_file = sys.argv[1]

    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)

    game = SnakeGame(config_file)
    game.run()



