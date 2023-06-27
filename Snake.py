import pygame
from random import randint

WIDTH, HEIGHT = 700, 700
FPS = 30
DIRECTION = "right"
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
ROW = 20
DIMENSIONS = WIDTH // ROW

pygame.init()
font = pygame.font.SysFont(None, 50)

class Snake:
    def __init__(self, x, y, length):
        self.x = x
        self.y = y
        self.length = length
        
        self.snakeParts = [[x, y] for _ in range(self.length)]
        for i, part in enumerate(self.snakeParts):
            part[0] -= i
    
    def draw(self, WIN):
        for x, y in self.snakeParts:
            pygame.draw.rect(WIN, GREEN, (x * DIMENSIONS, y * DIMENSIONS, DIMENSIONS, DIMENSIONS))
    
    def getBigger(self):
        self.snakeParts.append([self.snakeParts[-1][0], self.snakeParts[-1][1]])


class Apple:
    def __init__(self, snake):
        while True:
            self.appleX = randint(0, ROW - 1)
            self.appleY = randint(0, ROW - 1)
            
            for x, y in snake.snakeParts:
                if self.appleX == x and self.appleY == y:
                    break
            else:
                break
    
    def draw(self, WIN):
        pygame.draw.circle(WIN, RED, (self.appleX * DIMENSIONS + DIMENSIONS / 2, self.appleY * DIMENSIONS + DIMENSIONS / 2), DIMENSIONS / 2)


def change_direction(keys):
    global DIRECTION
    
    if keys[pygame.K_d] and DIRECTION != "left":
        DIRECTION = "right"
    elif keys[pygame.K_a] and DIRECTION != "right":
        DIRECTION = "left"
    elif keys[pygame.K_w] and DIRECTION != "down":
        DIRECTION = "up"
    elif keys[pygame.K_s] and DIRECTION != "up":
        DIRECTION = "down"


def move(snake):
    for i in range(snake.length - 1, 0, -1):
        snake.snakeParts[i][0] = snake.snakeParts[i-1][0]
        snake.snakeParts[i][1] = snake.snakeParts[i-1][1]
    
    if DIRECTION == "left":
        snake.snakeParts[0][0] -= 1
    elif DIRECTION == "right":
        snake.snakeParts[0][0] += 1
    elif DIRECTION == "up":
        snake.snakeParts[0][1] -= 1
    elif DIRECTION == "down":
        snake.snakeParts[0][1] += 1


def check_collision(snake, apple):
    x, y = snake.snakeParts[0]
    
    if (x, y) == (apple.appleX, apple.appleY):
        return 1
    
    for cordX, cordY in snake.snakeParts[2:]:
        if (x, y) == (cordX, cordY):
            return 2
    
    if x < 0:
        snake.snakeParts[0][0] = ROW
    elif x >= ROW:
        snake.snakeParts[0][0] = 0
    elif y < 0:
        snake.snakeParts[0][1] = ROW
    elif y >= ROW:
        snake.snakeParts[0][1] = 0


def draw(WIN, snake, apple, snake_parts):
    WIN.fill((0, 0, 0))
    textWidth = font.size(f"Score: {snake.length - snake_parts}")[0]
    WIN.blit(font.render(f"Score: {snake.length - snake_parts}", True, WHITE), (WIDTH / 2 - textWidth / 2, 10))
    snake.draw(WIN)
    apple.draw(WIN)
    
    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SNAKE")
    
    snake_parts = 5
    snake = Snake(10, 10, snake_parts)
    apple = Apple(snake)
    
    gameRunning = True
    while gameRunning:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameRunning = False
        
        keys = pygame.key.get_pressed()
        change_direction(keys)
        move(snake)
        returned = check_collision(snake, apple)
        if returned == 1:
            del apple
            apple = Apple(snake)
            snake.length += 1
            snake.getBigger()
        elif returned == 2:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    gameRunning = False
                    break
                elif event.type == pygame.KEYDOWN:
                    main()
        draw(WIN, snake, apple, snake_parts)
    
    pygame.quit()

if __name__ == "__main__":
    main()