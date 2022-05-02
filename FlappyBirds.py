import pygame
import random
from time import sleep
import neat
import os


ai_playing = True
generation = 0



from pathlib import Path
#Taking the base directory from project
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


#View Settings 
VIEW_HEIGHT = 800
VIEW_WIDTH = 500

#IMGS Settings
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(BASE_DIR / "imgs/pipe.png"))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(BASE_DIR / "imgs/bg.png"))
FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(BASE_DIR/ "imgs/base.png"))
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(BASE_DIR/"imgs/bird1.png")),
    pygame.transform.scale2x(pygame.image.load(BASE_DIR/"imgs/bird2.png")),
    pygame.transform.scale2x(pygame.image.load(BASE_DIR/"imgs/bird3.png")),
]

#Text Settings
pygame.font.init()
FONT_SIZE = pygame.font.SysFont('Arial', 50)


#Creating Objects Class

class Bird:
    IMGS = BIRD_IMGS
    #rotation animations
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        assert isinstance(x, (int, float)), 'X, precisa ser INT ou FLOAT'
        assert isinstance(y, (int, float)), 'Y, precisa ser INT ou FLOAT'
        self.x = x
        self.y = y
        self.ang = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        #calculate displacement
        self.time +=1
        displacement = 1.5 * (self.time**2) + self.speed * self.time
        #constrain displacement
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2
        
        self.y += displacement
        #bird Ang
        if displacement < 0 or self.y < (self.height +50):
            if self.ang < self.MAX_ROTATION:
                self.ang = self.MAX_ROTATION
        else:
            if self.ang > -90:
                self.ang -= self.ROTATION_SPEED

    def draw(self, screen):
        #define which bird img will be used
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #if the bird is falling dont move wings
        if self.ang <= 80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #draw the image
        rotated_img = pygame.transform.rotate(self.img, self.ang)
        pos_img_center = self.img.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_img.get_rect(center=pos_img_center)
        screen.blit(rotated_img, rectangle.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.bottom_pos = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.BOTTOM_PIPE = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bottom_pos = self.height + self.DISTANCE

    def move(self):
        self.x-=self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_pos))
        screen.blit(self.BOTTOM_PIPE, (self.x, self.bottom_pos))

    def collide(self, bird):
        #getting masks
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

        #getting pipe top and pip bottom bird distance
        difficult = 0.05
        top_distance = (self.x - bird.x, self.top_pos - round(bird.y) +20)
        bottom_distance = (self.x - bird.x, self.bottom_pos - round(bird.y) -20)

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(bottom_mask ,bottom_distance)

        if top_point or base_point:
            return True
        else:
            return False

class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMG.get_width()
    IMG = FLOOR_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1+self.WIDTH < 0:
            self.x1 = self.WIDTH + self.x2 
        if self.x2+self.WIDTH < 0:
            self.x2 = self.WIDTH + self.x1 
 

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BACKGROUND_IMG, (0,0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)
    text = FONT_SIZE.render(f"Points: {points}", 1, (255,255,255))
    screen.blit(text, (VIEW_WIDTH - 10 - text.get_width(),10))

    if ai_playing:
            text = FONT_SIZE.render(f"Generation: {generation}", 1, (255,255,255))
            screen.blit(text, (10,10))
    floor.draw(screen)
    pygame.display.update()


def main(genomes, config):
    global generation
    generation += 1

    if ai_playing:
        grids = []
        genome_list = []
        birds = []
        for _, genome in genomes:
            grid = neat.nn.FeedForwardNetwork.create(genome, config)
            grids.append(grid)
            genome.fitness = 0
            genome_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT)) 
    points = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(30)
 

        #user interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
        else:
            running = False
            break
        #moving objects
        for i, bird in enumerate(birds):
            bird.move()
            #increscing bir fitness
            genome_list[i].fitness += 0.1
            output = grids[i].activate(
                (
                bird.y, 
                abs(bird.y - pipes[pipe_index].height), 
                abs(bird.y - pipes[pipe_index].bottom_pos),
                )
            )
            # if output > 0.5 = Jump
            if output[0]>0.5:
                bird.jump()
        floor.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        genome_list[i].fitness -= 1
                        genome_list.pop(i)
                        grids.pop(i)
            #TODO: se o pássaro não estiver batendo no cano quando já está dentro dele, pipe.x -> pip.x + pipe.TOP_PIPE.get_width()
            if not pipe.passed and bird.x > pipe.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
            for genome in genome_list:
                genome.fitness +=5
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i,bird in enumerate(birds):
            if (bird.y + bird.img.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    genome_list.pop(i)
                    grids.pop(i)
        draw_screen(screen=screen,birds=birds, pipes=pipes, floor=floor, points=points)


def run(path_config):
    config = neat.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        PATH_CONFIG
        )
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == "__main__":
    PATH = os.path.dirname(__file__)
    PATH_CONFIG = os.path.join(PATH, "config.txt")
    run(PATH_CONFIG)