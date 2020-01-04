import pygame
import random

from pygame.locals import *
from typing import List, Tuple


Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]

class GameOfLife:

    def __init__(self, width: int=640, height: int=480, cell_size: int=20, speed: int=10) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
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
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen,pygame.Color('green'),
                                     (x * self.cell_size+1,
                                      y * self.cell_size+1,
                                      self.cell_size-1,
                                      self.cell_size-1))

    def run(self) -> None:
        """ Запустить игру """       
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))

        #Создание списка клеток
        self.grid = self.create_grid(randomize=True)
        runs = True
        while runs:
            for event in pygame.event.get():
                if event.type == QUIT:
                    runs = False
            self.screen.fill(pygame.Color('white'))
            self.draw_lines()
            self.draw_grid()

            self.grid = self.get_next_generation()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


    def create_grid(self, randomize: bool=False) -> Grid:
        """
        Создание списка клеток.
        
        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.
        Parameters
        ----------
        randomize : bool
        Если значение истина, то создается матрица, где каждая клетка может
        быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.
        Returns
        ----------
        out : Grid
            Матрица клеток размером `cell_height` х `cell_width`.
        """

        if randomize==True:
            self.grid=[[random.randint(0,1) for x in range(self.cell_width)] for y in range(self.cell_height)]
            return self.grid
        if randomize==False:
            self.grid=[[0 for x in range(self.cell_width)] for y in range(self.cell_height)]
            return self.grid


    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.
        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.
        Parameters
        ----------
        cell : Cell
        Клетка, для которой необходимо получить список соседей. Клетка
        представлена кортежем, содержащим ее координаты на игровом поле.
        Returns
        ----------
        out : Cells
        Список соседних клеток.
        """
        cells=[]
        temp=cell
        for x in range(-1,2):
            for y in range(-1,2):
                if x==0 and y == 0:
                    continue

                Fx=temp[1]+x
                Fy=temp[0]+y

                if 0<=Fx<self.cell_width and 0<=Fy<self.cell_height :
                    cells.append(self.grid[Fy][Fx])
        return cells

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.
        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        answer=[[0 for x in range(self.cell_width)] for y in range(self.cell_height)]
        for y in range(self.cell_height):
            for x in range(self.cell_width):
                self.k=y,x
                if self.grid[y][x]==0:
                    if self.get_neighbours(self.k).count(1) == 3:
                        answer[y][x]=1
                if self.grid[y][x]==1:
                    if self.get_neighbours(self.k).count(1)==2 or self.get_neighbours(self.k).count(1)==3:
                        answer[y][x]=1
        return answer


if __name__ == '__main__':
    game = GameOfLife(320,240,20,10)
    game.grid = game.create_grid(randomize=True) 
    game.run()
