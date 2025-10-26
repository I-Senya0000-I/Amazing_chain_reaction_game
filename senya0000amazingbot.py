from game_base import Bot
import numpy as np
import sys
"""
def get_game_state(self) -> dict:
        "Получить текущее состояние игры (для ботов)"
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
"""
def clearLine():
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')

class S4ZBot(Bot):


    def __init__(self, my_color, depth=3, variant=0):
        self.variant = variant
        self.depth = depth
        self.color = my_color
        print(self.color)
        
        

    def make_move(self, game_state: dict):
        self.n = game_state['n']
        self.m = game_state['m']
        self.player_cnt = game_state['players_count']
        #print(game_state)
        for i in range(self.n):
            for j in range(self.m):
                if np.sum(game_state['owners'] == self.color) == 0:
                    # First Move
                    return list(map(int, input().split()))
                else:
                    res = self.deep_analyzis(game_state['board'].copy(), game_state['owners'].copy(), self.color, self.depth, self.variant)
                    #print(res)
                    return res[0], res[1]
    


    def _count_available_spaces(self, i: int, j: int) -> int:
        return int(i > 0) + int(j > 0) + int(i < (self.n-1)) + int(j < (self.m - 1))
    

    def _get_neighbors(self, i: int, j: int):
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


    def _check_game_end(self, board, owners):
        active_players = set()
        for i in range(self.n):
            for j in range(self.m):
                if owners[i, j] != 0:
                    active_players.add(owners[i, j])
        return len(active_players) == 1


    def _process_chain_reaction(self, board, owners, start_i: int, start_j: int):
        """
        Обработать цепную реакцию взрывов
        """
        # Я собирался сделать очередь, типо чтоб 2на2 было, но лень
        # Также это нужно, если у нас "цепная реакция"
        queue = [(start_i, start_j)]
        processed = set()

        while queue and not self._check_game_end(board, owners):
            i, j = queue.pop(0)

            # Если уже прошли эту клетку, то пропуск
            #if (i, j) in processed:
            #    continue
            prev_owner = owners[i, j]
            # Обрабатываем взрыв, если значение дошло до h
            if board[i, j] >= self._count_available_spaces(i, j):
                # Запоминаем, что прошли
                #processed.add((i, j))

                # Обнуляем клетку
                board[i, j] -= self._count_available_spaces(i, j)
                if board[i, j] == 0:
                    owners[i, j] = 0 
                # Владение остается у текущего игрока

                # Получаем соседей
                neighbors = self._get_neighbors(i, j)

                # +1 ко всем соседям и изменяем владельца
                for ny, nx in neighbors:
                    board[ny, nx] += 1
                    owners[ny, nx] = prev_owner

                    # Если сосед теперь имеет значение h, добавляем в очередь
                    if board[ny, nx] >= self._count_available_spaces(ny, nx):
                        queue.append((ny, nx))
            

        return board, owners

    def print_board(self, board, owners, pretty=True):
        
        if pretty:
            for i in range(self.n):
                for j in range(self.m):
                    print(f"\033[3{owners[i][j]}m{board[i][j]}", end=' ')
                print("\n", end='')
           
            return True

    def deep_analyzis(self, board, owners, my_color, depth, variant=0):

        if variant == 0:
            my_cells = 0
            opponent_cells = 0
            my_summary = 0
            opponent_summary = 0

            for i in range(self.n):
                for j in range(self.m):
                    if owners[i, j] == my_color:
                        my_cells += 1
                        my_summary += board[i, j]
                    else:
                        opponent_cells += 1
                        opponent_summary += board[i, j]

            if (my_cells == 0):
                rate = -1000
                #self.print_board(board, owners)
                return [-1, -1, -rate]
            elif opponent_cells == 0:
                rate = 1000
                #self.print_board(board, owners)
                return [-1, -1, -rate]
            else:
                rate = float((my_cells-2*opponent_cells) + my_summary/opponent_summary)
            if depth == 0:
                return [-1, -1, -rate]


        possible_moves = [] 
        for i in range(self.n):
            for j in range(self.m):
                if owners[i, j] == my_color:
                    possible_moves.append((i, j))
        
        moves_results = []
        for i, j in possible_moves:
            newboard = board.copy()
            newowners = owners.copy()
            newboard[i, j] += 1
            newboard, newowners = self._process_chain_reaction(newboard.copy(), newowners.copy(), i, j)
            res = self.deep_analyzis(newboard.copy(), newowners.copy(), (my_color) % self.player_cnt + 1, depth-1, variant)
            moves_results.append([i, j, res[2]])
        

        moves_results.sort(key=lambda x: x[2], reverse=False)

        if not moves_results: return [-1, -1, 1000]


        moves_results[-1][2] = -moves_results[-1][2]
        #print(moves_results[-1], depth,  my_color)
        #clearLine()
        return moves_results[-1]




