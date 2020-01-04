import pathlib
import random

from typing import List, Optional, Tuple

Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]

class GameOfLife:
    def __init__(
        self,
        size: Tuple[int, int],
        randomize: bool=True,
        max_generations: Optional[float]=float('inf')
        ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.n_generation = 1

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
            grid=[[random.randint(0,1) for x in range(self.cols)] for y in range(self.rows)]
            return grid
        if randomize==False:
            grid=[[0 for x in range(self.cols)] for y in range(self.rows)]
            return grid

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

                if 0<=Fx<self.cols and 0<=Fy<self.rows :
                    cells.append(self.curr_generation[Fy][Fx])
        return cells

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
        Новое поколение клеток.
        """
        new_grid=self.create_grid()
        for y in range(self.rows):
            for x in range(self.cols):
                neigbours_n=self.get_neighbours((y,x)).count(1)
                if self.curr_generation[y][x]==0:
                    if neigbours_n == 3:
                        new_grid[y][x] = 1
                else:
                    if neigbours_n in [2,3]:
                        new_grid[y][x] = 1
        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        if not self.is_max_generations_exceed:
            self.prev_generation = self.curr_generation
            self.curr_generation = self.get_next_generation()
            self.n_generation+=1


    @property
    def is_max_generations_exceed(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.n_generation>=self.max_generations

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation!=self.curr_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> 'GameOfLife':
        """
        Прочитать состояние клеток из указанного файла.
        """
        #Нахождение размера поля
        cols,rows=0,1
        with open(filename,'r') as temp:
            cols=len(temp.readline())-1
            for i in temp:
                rows+=1
        #Чтение клеток из указанного файла
        grid=[[0 for x in range(cols)] for y in range(rows)]
        test=open(filename,"r")
        y,x=0,0
        while True:
            line=test.read(1)
            if line != '\n' and line!='':
                grid[y][x%(cols)]=line
                if x%(cols)==(cols-1) and rows!=1:
                    y+=1
                x+=1
            if not line:
                break
        grid=[[int(column) for column in rows] for rows in grid]

        game=GameOfLife((rows,cols))
        game.curr_generation=grid
        return game

    def save(self,filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние
        клеток в указанный файл.
        """
        helps=list()
        for i in range(self.rows):
            for j in range(self.cols):
                helps.append(self.curr_generation[i][j])
        count=0
        helps=''.join(map(str,helps))
        with open(filename,'w') as file:
            for value in helps:
                if count%self.cols!=0 or count==0:
                    file.write(value)
                if count%self.cols==0 and count!=0:
                    file.write('\n')
                    file.write(value)
                count+=1

                
if __name__=='__main__':
    game=GameOfLife.from_file('grid.txt')
