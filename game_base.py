import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random

class Game:
    def __init__(
                self,
                n: int,
                m: int,
                #h: int,
                players_count: int,
                players_name: list
            ):
        """
        Инициализация игры

        Аргументы
            n
                количество строк
            m
                количество столбцов
            h
                модуль (числа от 0 до h-1)
            players_count
                количество игроков
        """

        self.n = n
        self.m = m
        #self.h = h
        self.players_count = players_count
        self.players_name = players_name

        # Игровое поле
        self.board = np.zeros((n, m), dtype=int)

        # Владение клетками
        # 0 - свободно
        # 1..players_count - владение i-го игррока
        self.owners = np.zeros((n, m), dtype=int)

        # Текущий игрок
        self.current_player = 1

        # Статус игры
        self.game_over = False
        self.winner = None

        # Отслеживание первых ходов
        self.first_moves_done = [False] * (players_count + 1)
        # индекс 0 не используется(костыль ёбаный)

        # История ходов
        self.move_history = []

    def _get_player_name(self) -> str:
        """
        Возвращает имя игрока
        """
        return self.players_name[(self.current_player-1)%self.players_count]

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Cписок допустимых ходов для текущего игрока"""
        valid_moves = []

        for i in range(self.n):
            for j in range(self.m):
                if self.__is_valid_move(i, j):
                    valid_moves.append((i, j))

        return valid_moves

    def __is_valid_move(self, i: int, j: int) -> bool:
        """
        Проверка на возможность хода
        i, j - индексы.

        ** Для прямоугольной
        0 <= i < n
        0 <= j < m

        ** Для квадратной **
        0 <= i,j < n
        """
        if not ( (0 <= i < self.n) and (0 <= j < self.m) ):
            return False

        # Первый ход игрока в любую свободную клетку
        # Проверка на первый хол
        if not self.first_moves_done[self.current_player]:
            # Проверка на пустую клетку
            return self.owners[i, j] == 0

        # Ходы только в свои клетки
        return self.owners[i, j] == self.current_player

    def make_move(self, i: int, j: int) -> bool:
        """
        Сделать ход, чё сложного?

        Выводит True если ход был выполнен, False если ход недопустим
        """

        # Если игра закончена, то нахуй ходить?
        # Так ходить нельзя, ты дурак?
        if ( self.game_over ) or ( not self.__is_valid_move(i, j) ):
            print(f'{self._get_player_name()} тупой')
            return False

        # Отмечаем, что игрок сделал первый ход
        if not self.first_moves_done[self.current_player]:
            self.first_moves_done[self.current_player] = True

        # +1 к клетке
        self.board[i, j] += 1

        # Если это был первый ход, устанавливаем владение
        if self.owners[i, j] == 0:
            self.owners[i, j] = self.current_player
            

        # Обрабатываем цепную реакцию
        self._process_chain_reaction(i, j)


        if len(self.move_history) > 1:
            # Проверяем условие победы
            self._check_win_condition()

        # Добавляем ход в историю
        self.move_history.append((self.current_player, i, j))

        # Переходим к следующему игроку
        if not self.game_over:
            self._next_player()

        return True
    

    def _count_available_spaces(self, i: int, j: int) -> int:
        return int(i > 0) + int(j > 0) + int(i < (self.n-1)) + int(j < (self.m - 1))




    def _process_chain_reaction(self, start_i: int, start_j: int):
        """
        Обработать цепную реакцию взрывов
        """
        # Я собирался сделать очередь, типо чтоб 2на2 было, но лень
        # Также это нужно, если у нас "цепная реакция"
        queue = [(start_i, start_j)]
        processed = set()

        while queue:
            i, j = queue.pop(0)

            # Если уже прошли эту клетку, то пропуск
            if (i, j) in processed:
                continue

            # Обрабатываем взрыв, если значение дошло до h
            if self.board[i, j] >= self._count_available_spaces(i, j):
                # Запоминаем, что прошли
                processed.add((i, j))

                # Обнуляем клетку
                self.board[i, j] -= self._count_available_spaces(i, j)
                if self.board[i, j] == 0:
                    self.owners[i, j] = 0 

                # Получаем соседей
                neighbors = self._get_neighbors(i, j)

                # +1 ко всем соседям и изменяем владельца
                for ny, nx in neighbors:
                    self.board[ny, nx] += 1
                    self.owners[ny, nx] = self.current_player

                    # Если сосед теперь имеет значение h, добавляем в очередь
                    if self.board[ny, nx] >= self._count_available_spaces(ny, nx):
                        queue.append((ny, nx))

    def _get_neighbors(self, i: int, j: int) -> List[Tuple[int, int]]:
        """
        Возвращает соседей клетки
        (вверх, вниз, влево, вправо) - бля прямоугольного поля
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.n and 0 <= nj < self.m:
                neighbors.append((ni, nj))

        return neighbors

    def _check_win_condition(self):
        """
        Проверить условие победы
        """

        # Собираем множество игроков, у которых еще есть клетки
        active_players = set()
        for i in range(self.n):
            for j in range(self.m):
                if self.owners[i, j] != 0:
                    active_players.add(self.owners[i, j])

        # Если остался только один игрок - он победил
        if len(active_players) == 1 and self.current_player in active_players:
            self.game_over = True
            self.winner = self.current_player
        # Если у текущего игрока не осталось клеток - игра окончена
        elif self.current_player not in active_players:
            self.game_over = True
            # Победитель - игрок с наибольшим количеством клеток
            player_cells = [0] * (self.players_count + 1)
            for i in range(self.n):
                for j in range(self.m):
                    if self.owners[i, j] != 0:
                        player_cells[self.owners[i, j]] += 1
            self.winner = np.argmax(player_cells)

    def _next_player(self):
        """
        Перейти к следующему игроку
        """

        # Значение current_player изменяется от 1 до players_count
        # Тогда, чтоб прибовлялся 1 и брался модуль, формула должна быть такой:
        self.current_player = self.current_player % self.players_count + 1

        # Пропускаем игроков, у которых нет клеток (кроме случая, когда это их первый ход)
        skip_count = 0
        while skip_count < self.players_count:
            has_cells = np.sum(self.owners == self.current_player)

            if has_cells:
                break

            if ( has_cells ) or ( not self.first_moves_done[self.current_player] ):
                break

            self.current_player = self.current_player % self.players_count + 1
            skip_count += 1

    def get_game_state(self) -> dict:
        """Получить текущее состояние игры (для ботов)"""
        return {
            'board': self.board.copy(),
            'owners': self.owners.copy(),
            'current_player': self.current_player,
            'players_count': self.players_count,
            'players_name': self.players_name,
            #'h': self.h,
            'n': self.n,
            'm': self.m,
            'game_over': self.game_over,
            'winner': self.winner,
            'valid_moves': self.get_valid_moves()
        }

    def print_board(self, pretty=True):
        
        if pretty:
            for i in range(self.n):
                for j in range(self.m):
                    print(f"\033[3{self.owners[i][j]}m{self.board[i][j]}", end=' ')
                print("\n", end='')
            if self.game_over:
                print(f"Игра окончена! Победитель: {self.players_name[self.winner-1]}")

            return True


        """
        Напечатать текущее состояние доски
        (Переписать с цветом, как у Вумного Арса)
        """
        print(f"\nТекущий игрок: {self.current_player}")
        print("Доска (значения):")
        print(self.board)
        print("Владение:")
        print(self.owners)
        if self.game_over:
            print(f"Игра окончена! Победитель: {self.players_name[self.winner-1]}")


class Bot(ABC):
    """
    Абстрактный класс для ботов
    """

    def __init__(self, player_id: int):
        self.player_id = player_id

    @abstractmethod
    def make_move(self, game_state: dict) -> Tuple[int, int]:
        """
        Выбрать ход на основе текущего состояния игры

        Returns:
            (i, j) - координаты хода
        """
        # return (1, 1)
        # return (2, 2)
        pass

    def _get_neighbors(self, i: int, j: int, n: int, m: int) -> List[Tuple[int, int]]:
        """
        Получить соседей клетки
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m:
                neighbors.append((ni, nj))

        return neighbors


class RandomBot(Bot):
    """
    Бот, который делает случайные ходы
    """

    def make_move(self, game_state: dict) -> Tuple[int, int]:
        valid_moves = game_state['valid_moves']
        return random.choice(valid_moves) if valid_moves else (0, 0)


class User(Bot):
    def make_move(self, game_state:dict) -> Tuple[int, int]:
        return list(map(int, input().split()))[:2]



class GreedyBot(Bot):
    """
    Жадный бот, который пытается максимизировать суммарное значение
    """

    def make_move(self, game_state: dict) -> Tuple[int, int]:
        valid_moves = game_state['valid_moves']
        if not valid_moves:
            return (1, 2)

        best_move = valid_moves[0]
        best_score = -1

        # Симуляция ходов
        for move in valid_moves:
            score = self._evaluate_move(game_state, move)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _evaluate_move(self, game_state: dict, move: Tuple[int, int]) -> float:
        """
        Оценка хода
        """
        i, j = move
        board = game_state['board']
        owners = game_state['owners']
        #h = game_state['h']

        # Оценка
        score = 0

        # Ебашим, если клетка близка ко взрыву
        if board[i, j] == (int(i > 0) + int(j > 0) + int(i < (game_state['n']-1)) + int(j < (game_state['m'] - 1))) - 1:
            score += 20

        # Ебашим, если ещё и захватим чужие клетки
        neighbors = self._get_neighbors(i, j, game_state['n'], game_state['m'])
        for ni, nj in neighbors:
            if ( owners[ni, nj] != 0 ) and ( owners[ni, nj] != self.player_id ):
                score += 5

        # Ебашим, если клитки рядома с вражескими
        enemy_adjacent = False
        for ni, nj in neighbors:
            if ( owners[ni, nj] != 0 ) and ( owners[ni, nj] != self.player_id ):
                score += 2

        return score


class GameRunner:
    """
    Запускатель игры
    """

    def __init__(
                self,
                n: int,
                m: int,
                #h: int,
                players: List[Bot],
                players_name: list[str|None]=[]
            ):

        if players_name == []:
            self.players_name = [f'Игрок {i+1}' for i in range(len(players))]
        else:
            players_name = np.array(players_name)
            # print(players_name.shape, (len(players), ), players_name.shape == (len(players), ))
            if players_name.shape == (len(players), ):
                for i in np.where(players_name == None):
                    players_name[i] = f'Игрок {i+1}'
                self.players_name = list(players_name)
            else:
                raise Exception('Если не можешь задать имена правильно, то и не задавай')

        self.game = Game(n, m, len(players), self.players_name)
        self.players = players

    def run_game(self, verbose: bool = True) -> int:
        """
        Запустить игру и вернуть номер победителя
        """
        if verbose:
            print("Начало игры!")
            self.game.print_board()

        while not self.game.game_over:
            current_player = self.players[self.game.current_player - 1]
            game_state = self.game.get_game_state()

            move = current_player.make_move(game_state)

            if verbose:
                print(f"\n{self.game._get_player_name()} ( {type(current_player).__name__} ) ходит: ({move[0]+1}, {move[1]+1})")

            success = self.game.make_move(move[0], move[1])

            if not success:
                print(f"Недопустимый ход: {move}")
                break

            if verbose:
                self.game.print_board()

        if verbose:
            print(f"\nИгра окончена! Победитель: {self.players_name[self.game.winner-1]}")

        return self.game.winner
