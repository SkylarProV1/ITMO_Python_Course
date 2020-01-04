import curses

from time import sleep
from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border('|', '|', '-', '-', '+', '+', '+', '+')

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for r in range(self.life.rows):
            for c in range(self.life.cols):
                if self.life.curr_generation[r][c] == 1:
                    screen.addstr(r + 1, c + 1, "*")
                else:
                    screen.addstr(r + 1, c + 1, " ")

    def run(self) -> None:
        """ Запустить игру """
        screen = curses.initscr()
        self.draw_borders(screen)
        curses.curs_set(1)
        self.draw_grid(screen)
        screen.refresh()
        while (self.life.is_changing and
               not self.life.is_max_generations_exceeded):
            self.life.step()
            self.draw_grid(screen)
            screen.refresh()
            sleep(0.5)
        curses.endwin()

if __name__ == '__main__':
    life = GameOfLife((9, 50),True, max_generations=200)
    ui = Console(life)
    ui.run()