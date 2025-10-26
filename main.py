from game_base import Game, Bot, RandomBot, GreedyBot, GameRunner, User
from senya0000amazingbot import S4ZBot
'''
крч, каждый бот должен иметь метод make_move
пока не сделал хрень, которая будет говорить боту "Нет, так ходить нельзя, переходи"

каждый бот будет получать game_state
Часть кода:
{
    'board': self.board.copy(),
    'owners': self.owners.copy(),
    'current_player': self.current_player,
    'players_count': self.players_count,
    'players_name': self.players_name,
    'h': self.h,
    'n': self.n,
    'm': self.m,
    'game_over': self.game_over,
    'winner': self.winner,
    'valid_moves': self.get_valid_moves()
}
board - текущая доска, это массив NxM(в частности это квадратная) np.ndarray
owners - такого же размера массив, в которм отмечены, к каким игрокам принадлежит каждая ячейка

Ботов создавать по подобию базовых, на основе Bot
когда его создаёшь, надо дать ему индекс

'''

if __name__ == "__main__":
    # боты(базовые) или игроки
    # Обычного игрока я не создал
    # Визуальную хернюдля взаимодейсвтия пока не доделал
    bots = [
        #RandomBot(1),
        #GreedyBot(2),
        S4ZBot(1, depth=7, variant=0),
        S4ZBot(2, depth=5, variant=0),
        
    ]

    # Запускаем игру
    runner = GameRunner(
        n=5, m=5,
        players=bots,
        players_name=['S4zBot1', 'S4zBot2']
    )
    winner = runner.run_game(verbose=True)
    print(winner)

    # Статистика по множеству игр

    # wins = [0] * len(bots)
    # for _ in range(100):
    #     runner = GameRunner(n=5, m=5, h=4, players=bots)
    #     winner = runner.run_game(verbose=False)
    #     wins[winner - 1] += 1

    # print("Результаты 100 игр:")
    # for i, win_count in enumerate(wins):
    #     bot_type = type(bots[i]).__name__
    #     print(f"Игрок {i+1} ({bot_type}): {win_count} побед")
