import itertools as it
import numpy as np
from copy import deepcopy
import random

from load_conf.load_yaml import load_conf_yaml
from board.defined_panel import EMPTY, WALL, FIRST, CHANCE, EMPTYS, DEALER
from board.panels_board import Board

import os

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

    def get_game_id(self):
        return self.game_id
    def get_player_names(self):
        return self.player_names
    def get_player_colors(self):
        return self.player_colors
    def get_player_ids(self):
        return self.player_ids
    def get_n_players(self):
        return self.n_players
    def get_n_row(self):
        return self.board.len_row
    def get_n_col(self):
        return self.board.len_col
    def coord_to_panel_idx(self, i, j):
        return i * self.board.len_col + j
    def panel_idx_to_coord(self, idx):
        i = idx // self.board.len_col
        j = idx % self.board.len_col
        return i, j
    def get_selectable_panels(self, player):
        selectable_coords = self.board.selectable_panels(player)
        return [self.coord_to_panel_idx(i, j) for i, j in selectable_coords]
    def is_atchance(self):
        return self.board.is_atchance()
    def to_get_panels(self, idx, player):
        i, j = self.panel_idx_to_coord(idx)
        to_get_panel_coords = self.board.flip_panel(i, j, player)
        return [self.coord_to_panel_idx(m, n) for m, n in to_get_panel_coords]
    def load_state(self, csvfile):
        self.board.load_state(csvfile)
    def get_board_panels(self):
        return list(self.board.board_panels().flatten())
    def get_player_panels(self, player):
        tmp_board = self.get_board_panels()
        tmp_board = np.array(tmp_board)
        indices = np.where(tmp_board == player)
        return list(indices[0])
        pass
        # [self.coord_to_panel_idx(i, j) for i, j in range(5)]
    def set_at_chance(self, idx):
        i, j = self.panel_idx_to_coord(idx)
        self.board.set_at_chance(i, j)

    def myinput(self, message: str):
        res = input(message)
        inputs_path = os.path.join(self.savedir, f"inputs_{self.game_id}.txt")
        with open(inputs_path, "a") as f:
            f.write(res + "\n")
        return res
    
    def main(self):
        after_at_chance = False
        while True:
            self.board.display_board()
            if self.board.is_atchance():
                print("アタックチャンス!")
            try:
                player = int(self.myinput("正解したプレイヤー: "))
                if player == DEALER:
                    print("ゲーム終了")
                    exit(1)
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
                    print_selectables = [(i, j) for i, j in selectables]
                    print("選択可能なパネル:", list(sorted(print_selectables)))
                    i, j = map(int, self.myinput("行,列を入力（0-4, 例: 2 3）: ").split())
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
                            selectables = self.board.players_panels()
                            print_selectables = [(int(i), int(j)) for i, j in selectables]
                            print("狙い目にできるパネル:", list(sorted(print_selectables)))
                            i, j = map(int, self.myinput("行,列を入力（0-4, 例: 2 3）: ").split())
                            if (i, j) not in selectables:
                                print("そのパネルは狙い目にできません")
                                continue
                        except (ValueError, IndexError):
                            print("正しい形式で入力してください（例: 2 3）")
                            continue
                        self.board.set_at_chance(i, j)
                        after_at_chance = True
                        break
                if after_at_chance:
                    after_at_chance = False
                    break


if __name__ == "__main__":
    conf = "config_default.yaml"
    savedir = "csvs"

    game = Attack25(conf, savedir)
    game.board.load_state("csvs/at25_37618_29.csv")
    game.main()
