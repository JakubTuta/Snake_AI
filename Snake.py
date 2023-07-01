import pygame                   # pip install pygame / pip install pygame --pre
import neat                     # pip install neat-python
import os
from random import randint
import pickle

LOAD_BEST_POPULATION = True
SAVE_BEST_POPULATION = True

WIDTH, HEIGHT = 700, 700
FPS = 60
DIRECTION = "right"
ROWS = 40
DIMENSIONS = WIDTH / ROWS
SNAKE_PARTS = 5
GEN = 0
MAX_DIAGONAL = 2 * ROWS
BEST_SCORE = 0
BEST_FITNESS = 0

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE")
clock = pygame.time.Clock()

pygame.init()
font = pygame.font.SysFont(None, 40)

COLORS = {
    "GREEN": (0, 255, 0),
    "RED": (255, 0, 0),
    "WHITE": (255, 255, 255)
}

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = SNAKE_PARTS
        
        self.snakeParts = [[x - i - 1, y] for i in range(self.length)]
    
    def draw(self, WIN):
        for x, y in self.snakeParts:
            pygame.draw.rect(WIN, COLORS["GREEN"], (x * DIMENSIONS, y * DIMENSIONS, DIMENSIONS, DIMENSIONS))
    
    def getBigger(self):
        self.snakeParts.append([self.snakeParts[-1][0], self.snakeParts[-1][1]])
        self.length += 1
    
    def calculateDistanceHeadToWalls(self, apple):
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        distances = [0 for i in range(len(directions))]
        
        for i, (x, y) in enumerate(directions):
            headX = self.snakeParts[0][0]
            headY = self.snakeParts[0][1]
            loopCount = 1
            distance = 1
            while True:
                returned = check_collision((headX + (x * loopCount), headY + (y * loopCount)), self, apple)
                if returned == 3:
                    break
                else:
                    distance += 1
                loopCount += 1
            distances[i] = 1 / distance
        
        return distances
    
    def calculateDistanceHeadToApple(self, apple):
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        distances = [0 for i in range(len(directions))]
        
        for i, (x, y) in enumerate(directions):
            headX = self.snakeParts[0][0]
            headY = self.snakeParts[0][1]
            loopCount = 1
            while True:
                returned = check_collision((headX + (x * loopCount), headY + (y * loopCount)), self, apple)
                if returned == 1:
                    distances[i] = 1
                    break
                elif returned == 3:
                    break
                loopCount += 1
        
        return distances
    
    def calculateDistanceHeadToSnakeparts(self, apple):
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        distances = [0 for i in range(len(directions))]
        
        for i, (x, y) in enumerate(directions):
            headX = self.snakeParts[0][0]
            headY = self.snakeParts[0][1]
            loopCount = 1
            distance = 1
            bodyFound = False
            while True:
                returned = check_collision((headX + (x * loopCount), headY + (y * loopCount)), self, apple)
                if returned == 2:
                    bodyFound = True
                    break
                elif returned == 3:
                    break
                else:
                    distance += 1
                loopCount += 1
            
            if bodyFound:
                distances[i] = 1 / distance
            else:
                distances[i] = 0
        
        return distances
    
    def calculateDistanceToApple(self, apple):
        return abs(apple.appleX - self.snakeParts[0][0] + apple.appleY - self.snakeParts[0][1])


class Apple:
    def __init__(self, snake):
        while True:
            self.appleX = randint(0, ROWS - 1)
            self.appleY = randint(0, ROWS - 1)
            
            for x, y in snake.snakeParts:
                if self.appleX == x and self.appleY == y:
                    break
            else:
                break
    
    def draw(self, WIN):
        pygame.draw.circle(WIN, COLORS["RED"], (self.appleX * DIMENSIONS + DIMENSIONS / 2, self.appleY * DIMENSIONS + DIMENSIONS / 2), DIMENSIONS / 2)


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


def check_collision(head, snake, apple):
    x, y = head
    
    if (x, y) == (apple.appleX, apple.appleY):
        return 1
    
    for cordX, cordY in snake.snakeParts[1:]:
        if (x, y) == (cordX, cordY):
            return 2
    
    if x < 0 or x >= ROWS or y < 0 or y >= ROWS:
        return 3
    
    return 0


def draw(WIN, snake, apple, snakeID):
    WIN.fill((0, 0, 0))
    
    apple.draw(WIN)
    snake.draw(WIN)
    
    textHeight = font.size(f"Score: {snake.length - SNAKE_PARTS}")[1]
    WIN.blit(font.render(f"Score: {snake.length - SNAKE_PARTS}", True, COLORS["WHITE"]), (10, 10))
    WIN.blit(font.render(f"Best score: {BEST_SCORE}", True, COLORS["WHITE"]), (10, textHeight + 20))
    WIN.blit(font.render(f"Generation: {GEN}", True, COLORS["WHITE"]), (10, (2 * textHeight) + 30))
    WIN.blit(font.render(f"Snake: {snakeID}", True, COLORS["WHITE"]), (10, (3 * textHeight) + 40))
    WIN.blit(font.render(f"Best fitness: {round(BEST_FITNESS, 2)}", True, COLORS["WHITE"]), (10, (4 * textHeight) + 50))


def changeDirection(newDirection):
    global DIRECTION
    
    if newDirection == "up" and DIRECTION != "down":
        DIRECTION = "up"
    elif newDirection == "down" and DIRECTION != "up":
        DIRECTION = "down"
    elif newDirection == "right" and DIRECTION != "left":
        DIRECTION = "right"
    elif newDirection == "left" and DIRECTION != "right":
        DIRECTION = "left"


def handleNEAT(net, snake, apple):
    inputs = snake.calculateDistanceHeadToWalls(apple) + snake.calculateDistanceHeadToApple(apple) + snake.calculateDistanceHeadToSnakeparts(apple)
    
    output = net.activate((inputs))
    outputList = [
        ("up", output[0]),
        ("down", output[1]),
        ("right", output[2]),
        ("left", output[3])
    ]
    outputList.sort(key=lambda x: x[1], reverse=True)
    
    return outputList[0][0]


def savePopulation(filename, population):
    with open(filename, 'wb') as file:
        pickle.dump(population, file, pickle.HIGHEST_PROTOCOL)


def loadPopulation(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    
    population = neat.Population(config)
    
    if LOAD_BEST_POPULATION:
        population = loadPopulation("population.dat")
    
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    population.run(main, 50)
    
    if SAVE_BEST_POPULATION:
        savePopulation("population.dat", population)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


def main(genomes, config):
    global DIRECTION, GEN, BEST_SCORE, BEST_FITNESS
    GEN += 1
    
    nets = []
    ge = []
    snakes = []
    
    for _, g in genomes:
        g.fitness = 0
        nets.append(neat.nn.FeedForwardNetwork.create(g, config))
        ge.append(g)
        snakes.append(Snake((ROWS // 2) + 2, ROWS // 2))
    
    for i, snake in enumerate(snakes):
        DIRECTION = "right"
        apple = Apple(snake)
        gameRunning = True
        frames = 0
        
        while gameRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
            newDirection = handleNEAT(nets[i], snake, apple)
            changeDirection(newDirection)
            move(snake)
            
            ge[i].fitness += .001
            
            draw(WIN, snake, apple, i + 1)
            pygame.display.update()
            
            if ge[i].fitness > BEST_FITNESS:
                BEST_FITNESS = ge[i].fitness
            
            if snake.length - SNAKE_PARTS > BEST_SCORE:
                BEST_SCORE = snake.length - SNAKE_PARTS
            
            returned = check_collision(snake.snakeParts[0], snake, apple)
            if returned == 1:
                del apple
                apple = Apple(snake)
                snake.getBigger()
                ge[i].fitness += 5
                frames = 0
            elif returned == 2 or returned == 3 or frames > 4 * FPS:
                gameRunning = False
            
            frames += 1
            clock.tick(FPS)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEAT_config.txt")
    run(config_path)