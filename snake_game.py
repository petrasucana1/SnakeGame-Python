import pygame
import sys
import json
import random
import os
import math

pygame.mixer.init()

CELL_SIZE = 20
FPS = 8
STATUS_BAR_HEIGHT = 40
BORDER_THICKNESS = 8

class SnakeGame:
    def __init__(self, config_file):
        """Initializează jocul Snake: încarcă configurațiile, imaginile și sunetele necesare, și setează fereastra de joc."""
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

        self.food_images = [
            pygame.transform.scale(pygame.image.load("images/apple.png"), (int(CELL_SIZE * 2), int(CELL_SIZE * 2))),
            pygame.transform.scale(pygame.image.load("images/pear.png"), (int(CELL_SIZE * 2), int(CELL_SIZE * 2.2))),
            pygame.transform.scale(pygame.image.load("images/peach.png"), (int(CELL_SIZE * 2), int(CELL_SIZE * 2.2)))
        ]

        self.status_images = [
            pygame.transform.scale(pygame.image.load("images/apple.png"), (28, 28)),
            pygame.transform.scale(pygame.image.load("images/pear.png"), (24, 29)),
            pygame.transform.scale(pygame.image.load("images/peach.png"), (24, 30))
        ]

        self.obstacles_images = [
            pygame.transform.scale(pygame.image.load("images/rock.png"), (int(CELL_SIZE * 2), int(CELL_SIZE * 2))),
            pygame.transform.scale(pygame.image.load("images/grass.png"), (int(CELL_SIZE * 2), int(CELL_SIZE * 2.2)))
        ]

        try:
            self.eat_sound = pygame.mixer.Sound('sounds/bite.mp3')
        except pygame.error:
            print("Error: 'bite.mp3' sound file not found.")
            sys.exit(1)

        try:
            self.game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
        except pygame.error:
            print("Error: 'game_over.wav' sound file not found.")
            sys.exit(1)

        self.screen = pygame.display.set_mode((self.width * CELL_SIZE + 2 * BORDER_THICKNESS, self.height * CELL_SIZE + STATUS_BAR_HEIGHT + BORDER_THICKNESS))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        self.high_score = 0
        self.new_game()


    def new_game(self):
        """Resetează jocul: reinițializează variabilele și creează un nou joc."""
        self.snake = [{"x": 0, "y": 0}]
        self.direction = "RIGHT"
        self.score = 0
        self.total_fruits = 0
        self.fruit_counter = {"apple": 0, "pear": 0, "peach": 0}
        self.active_obstacles = []
        for obstacle in self.obstacles[:3]:
            self.active_obstacles.append({"x": obstacle["x"], "y": obstacle["y"], "image": random.choice(self.obstacles_images)})
        self.food = self.generate_food()


    def generate_food(self):
        """Generează o poziție aleatoare pentru mâncare, asigurându-se că nu se suprapune cu obstacolele sau cu șarpele."""
        food_position = {"x": random.randint(0, self.width - 1), "y": random.randint(0, self.height - 1)}
        while any(food_position["x"] == o["x"] and food_position["y"] == o["y"] for o in self.active_obstacles) or food_position in self.snake:
            food_position = {"x": random.randint(0, self.width - 1), "y": random.randint(0, self.height - 1)}

        self.food_type = random.choice(["apple", "pear", "peach"])
        index = {"apple": 0, "pear": 1, "peach": 2}[self.food_type]
        self.food_image = self.food_images[index]
        return food_position


    def table_drawing(self):
        """Desenează tabla de joc: creează un model de tablă cu celule colorate."""
        color1 = (170, 215, 81)
        color2 = (162, 209, 73)
        for x in range(self.width):
            for y in range(self.height):
                cell_color = color1 if (x + y) % 2 == 0 else color2
                cell = pygame.Rect(x * CELL_SIZE + BORDER_THICKNESS, y * CELL_SIZE + STATUS_BAR_HEIGHT + BORDER_THICKNESS, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, cell_color, cell)


    def snake_drawing(self):
        """Desenează șarpele: fiecare segment al șarpelui este desenat cu o animație de undă."""
        color_snake = (0, 160, 0)
        wave_speed = 5
        wave_amplitude = 3

        time_now = pygame.time.get_ticks() / 1000
        snake_length = len(self.snake)

        for index, snake_part in enumerate(self.snake):
            scale = 1 - (index / snake_length) * 0.4
            segment_size = int(CELL_SIZE * scale)

            wave = math.sin(time_now * wave_speed + index * 0.5) * wave_amplitude

            cell_x = snake_part["x"] * CELL_SIZE + BORDER_THICKNESS + (CELL_SIZE - segment_size) // 2
            cell_y = snake_part["y"] * CELL_SIZE + STATUS_BAR_HEIGHT + BORDER_THICKNESS + (CELL_SIZE - segment_size) // 2 + wave

            cell = pygame.Rect(cell_x, cell_y, segment_size, segment_size)
            pygame.draw.rect(self.screen, color_snake, cell, border_radius=segment_size // 4)


    def food_drawing(self):
        """Desenează mâncarea: imaginea mâncării este plasată pe tablă."""
        apple_rect = self.food_image.get_rect()
        apple_rect.center = (self.food["x"] * CELL_SIZE + CELL_SIZE // 2 + BORDER_THICKNESS, self.food["y"] * CELL_SIZE + CELL_SIZE // 2 + STATUS_BAR_HEIGHT + BORDER_THICKNESS)
        self.screen.blit(self.food_image, apple_rect)


    def obstacles_drawing(self):
        """Desenează obstacolele: fiecare obstacol este desenat pe tablă."""
        for obstacle in self.active_obstacles:
            image = obstacle["image"]
            rect = image.get_rect()
            rect.center = (obstacle["x"] * CELL_SIZE + CELL_SIZE // 2 + BORDER_THICKNESS, obstacle["y"] * CELL_SIZE + CELL_SIZE // 2 + STATUS_BAR_HEIGHT + BORDER_THICKNESS)
            self.screen.blit(image, rect)


    def draw_status_bar(self):
        """Desenează bara de stare: afișează scorul, numărul de fructe și tipul acestora."""
        pygame.draw.rect(self.screen, (40, 100, 40), (0, 0, self.width * CELL_SIZE + 2 * BORDER_THICKNESS, STATUS_BAR_HEIGHT))
        font = pygame.font.Font(None, 24)
        start_x = 10
        fruits = ["apple", "pear", "peach"]
        for i, fruit in enumerate(fruits):
            self.screen.blit(self.status_images[i], (start_x, 8))
            count_text = font.render(f"x {self.fruit_counter[fruit]}", True, (255, 255, 255))
            self.screen.blit(count_text, (start_x + 30, 12))
            start_x += 90
        total_text = font.render(f"Total Score: {self.total_fruits}", True, (255, 255, 255))
        self.screen.blit(total_text, (self.width * CELL_SIZE - 150, 12))


    def snake_evolution(self):
        """Evoluează șarpele: mută capul șarpelui în direcția curentă și verifică coliziunile."""
        head = self.snake[0].copy()

        if self.direction == "UP":
            head["y"] -= 1
        elif self.direction == "DOWN":
            head["y"] += 1
        elif self.direction == "LEFT":
            head["x"] -= 1
        elif self.direction == "RIGHT":
            head["x"] += 1

        head["x"] %= self.width
        head["y"] %= self.height

        self.snake.insert(0, head)

        if head["x"] == self.food["x"] and head["y"] == self.food["y"]:
            self.score += 1
            self.total_fruits += 1
            self.fruit_counter[self.food_type] += 1
            self.food = self.generate_food()
            self.eat_sound.play()
            if self.score % 3 == 0 and len(self.active_obstacles) < len(self.obstacles):
                next_obstacle = self.obstacles[len(self.active_obstacles)]
                self.active_obstacles.append({"x": next_obstacle["x"], "y": next_obstacle["y"], "image": random.choice(self.obstacles_images)})
        else:
            self.snake.pop()


    def collision_verification(self):
        """Verifică coliziunile: dacă capul șarpelui se ciocnește de obstacole sau de el însuși."""
        head = self.snake[0]
        if any(head["x"] == o["x"] and head["y"] == o["y"] for o in self.active_obstacles) or head in self.snake[1:]:
            return True
        return False


    def end_game(self):
        """Finalizează jocul: afișează mesajul de finalizare și redă sunetul corespunzător."""
        font = pygame.font.Font(None, 36)
        self.game_over_sound.play()
        text = font.render(f"Game Over! Your Score: {self.score}", True, (150, 0, 0))
        self.screen.blit(text, (self.width * CELL_SIZE // 2 - text.get_width() // 2, self.height * CELL_SIZE // 2))
        text = font.render(f"High Score: {self.high_score}", True, (0, 150, 0))
        self.screen.blit(text, (self.width * CELL_SIZE // 2 - text.get_width() // 2, self.height * CELL_SIZE // 2 + 40))
        pygame.display.flip()
        pygame.time.wait(2000)


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
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
            self.draw_status_bar()
            self.table_drawing()
            self.snake_drawing()
            self.food_drawing()
            self.obstacles_drawing()

            border_color = (40, 100, 40)
            pygame.draw.rect(self.screen, border_color, (0, STATUS_BAR_HEIGHT, self.width * CELL_SIZE + 2 * BORDER_THICKNESS, self.height * CELL_SIZE + BORDER_THICKNESS), BORDER_THICKNESS)

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
