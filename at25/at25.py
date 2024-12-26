import itertools as it
import numpy as np
from copy import deepcopy
import random

from load_conf import load_conf_yaml
from board.defined_panel import EMPTY, WALL, FIRST, CHANCE, EMPTYS
from board.panels_board import Board

class Attack25:
    def __init__(self,
                 conffile: str,
                 savedir: str,
                 ):

        config = load_conf_yaml(conffile)
        self.savedir = savedir

        self.n_players = config["n_players"]
        if self.n_players < 2:
            print("invalid players:", self.n_players)
            exit(1)

        self.player_ids = list(range(1, 1 + self.n_players))

        player_names = [list(d.keys())[0] for d in config["player_colors"]]
        player_colors = [list(d.values())[0] for d in config["player_colors"]]

        self.player_names = dict(zip(self.player_ids, player_names))
        self.player_colors = dict(zip(self.player_ids, player_colors))

        self.game_id = random.getrandbits(16)
        print("this games id:", self.game_id)

        self.at_chances = config["at_chances"]

        self.board = Board(self.player_ids, config["init_board"], 
                           self.at_chances,
                           self.game_id, self.savedir)

        if not self.board.is_init():
            print("invalid_shape")
            exit(1)

    def main(self):
        while True:
            self.board.display_board()
            if self.board.is_atchance():
                print("アタックチャンス!")
            try:
                player = int(input("正解したプレイヤー: "))
                if player not in self.player_ids:
                    print("存在しないプレイヤー:", player)
                    continue
            except (ValueError):
                print("正しい形式で入力してください（例: 2）")
                continue
            # 入力
            while True:
                try:
                    selectables = self.board.selectable_panels(player)
                    print_selectables = [(int(i), int(j)) for i, j in selectables]
                    print("選択可能なパネル:", list(sorted(print_selectables)))
                    i, j = map(int, input("行,列を入力（0-4, 例: 2 3）: ").split())
                    if (i, j) not in selectables:
                        print("そのパネルは取れません")
                        continue
                except (ValueError, IndexError):
                    print("正しい形式で入力してください（例: 2 3）")
                    continue

                # パネルを操作
                if not self.board.is_atchance():
                    self.board.flip_panel(i, j, player)
                    break
                else:
                    self.board.flip_panel(i, j, player)
                    while True:
                        try:
                            selectables = self.board.players_panels(player)
                            print_selectables = [(int(i), int(j)) for i, j in selectables]
                            print("狙い目にできるパネル:", list(sorted(print_selectables)))
                            i, j = map(int, input("行,列を入力（0-4, 例: 2 3）: ").split())
                            if (i, j) not in selectables:
                                print("そのパネルは狙い目にできません")
                                continue
                        except (ValueError, IndexError):
                            print("正しい形式で入力してください（例: 2 3）")
                            continue


if __name__ == "__main__":
    conf = "config_default.yaml"
    savedir = "csvs"

    game = Attack25(conf, savedir)

    game.main()
    # csvfile = "init_3x3.csv"
    # n_players = 2
    # main(n_players, csvfile)

    # main(4)

#     load_panels = """
#   0 1 2 3 4
# 0 . . 2 . .
# 1 . . 3 . .
# 2 1 1 1 1 1
# 3 . . 3 . .
# 4 . 4 4 4 .
# """
#     main(load_panels)
