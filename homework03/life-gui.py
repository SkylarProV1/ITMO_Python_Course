import pygame
from pygame.locals import *
 
from life import GameOfLife
from ui import UI

 
class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
 
        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen_size = (self.width, self.height)
        self.cell_size = cell_size
        self.speed = speed
 
    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))
 
    def draw_grid(self) -> None:
        """
       Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
       """
        for y in range(len(self.life.curr_generation)):
            for x in range(len(self.life.curr_generation[0])):
                if self.life.curr_generation[y][x]:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     (x * self.cell_size + 1,
                                      y * self.cell_size + 1,
                                      self.cell_size - 1,
                                      self.cell_size - 1))

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        # Начальная отрисовка списка клеток
        self.draw_grid()
        self.draw_lines()
 
        runs = True
        while runs and self.life.is_changing and not self.life.is_max_generations_exceed:
            self.screen.fill(pygame.Color('white'))
 
            for event in pygame.event.get():
                if event.type == QUIT:
                    runs = False
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        if self.pause():
                            runs = False
            if runs:
                self.life.step()
                self.draw_grid()
                self.draw_lines()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()
 
    def pause(self):
        flag = True
        while flag:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        flag = False
                if event.type == QUIT:
                    return 1
                if event.type == MOUSEBUTTONDOWN:
                    self.change_status(event.pos)
                if event.type == KEYDOWN:
                    if event.key == K_s:
                        self.life.save(pathlib.Path(input("path-->")))
 
    def change_status(self, pos):
        x, y = pos
        a = self.cell_size
        x //= a
        y //= a
        k = self.life.curr_generation[y][x]
        self.life.curr_generation[y][x] = 1 - k
        self.draw_grid()
        self.draw_lines()
        pygame.display.flip()
 
 
if __name__ == '__main__':
    life = GameOfLife((30, 30), True, max_generations=50)
    gui = GUI(life, 10, 10)
    gui.run()
