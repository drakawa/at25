from .defined_panel import *
import numpy as np
import itertools as it
from copy import deepcopy
import os

class Board:
    def __init__(
            self, 
            player_ids: list, 
            board: np.ndarray, 
            at_chances: list,
            game_id: int,
            savedir: str,
            ):
        self.player_ids = player_ids
        self.board = board
        self.at_chances = at_chances

        self.len_row, self.len_col = self.board.shape

        self.game_id = game_id
        self.history = list()
        self.savedir = savedir

    def is_init(self):
        return np.sum(self.board == FIRST) == 1
    
    def is_atchance(self):
        return np.sum(self.board == EMPTY) in self.at_chances
    
    def load_state(self, boardcsv):
        state = np.loadtxt(boardcsv, delimiter=",", dtype=int)
        if state.shape != self.board.shape:
            print("invalid shape")
            exit(1)

        try:
            for i, j in it.product(*map(range, self.board.shape)):
                if self.board[i, j] not in (set(self.player_ids) | set([WALL, EMPTY, FIRST, CHANCE])):
                    raise Exception("invalid boardcsv.")
        except Exception as inst:
            print(inst.args)
            exit(1)

        self.board = state

    def display_board(self):
        def _cell_to_str(val):
            if val == WALL:
                return "x"
            elif val == EMPTY:
                return "."
            elif val == FIRST:
                return "*"
            elif val == CHANCE:
                return "!"
            else:
                return str(val)
        """盤面を表示する"""
        print("  " + " ".join(map(str, range(self.len_col))))
        print("\n".join(
            [str(row_idx) + " " + " ".join(
                    [_cell_to_str(cell) for cell in row]
                ) for row_idx, row in enumerate(self.board)
            ]
        ))

    def update_panel(self, i, j, player):
        if player not in self.player_ids:
            print("invalid player:", player)
            exit(1)
        try:
            if self.board[i, j] == WALL:
                raise Exception(f"invalid index ({i}, {j})")
            self.board[i, j] = player
            self.display_board()
            self.history.append(deepcopy(self.board))
            np.savetxt(
                os.path.join(self.savedir, f"at25_{self.game_id:05}_{len(self.history):03}.csv"),
                self.board,
                delimiter=",",
                fmt="%d"
            )
            print(f"save to {self.savedir}/at25_{self.game_id:05}_{len(self.history):03}.csv")

        except Exception as inst:
            print(inst.args)
            exit(1)

    def is_out(self, i, j):
        return i not in range(self.len_row) or j not in range(self.len_col) or self.board[i, j] == WALL

    def to_get_select(self, i, j, player) -> tuple[list[int], list[int]]:
        if player not in self.player_ids:
            print("invalid player:", player)
            return
        to_get_panels = list()
        selectable_panels = list()

        # directions = it.product((-1,0,1), repeat=2)
        directions = [(-1,0),(1,0),(0,-1),(0,1),
                      (-1,-1),(-1,1),(1,-1),(1,1)
        ]
        for dir_i, dir_j in directions:
            if (dir_i, dir_j) == (0, 0):
                continue            
            tmp_cands = list()
            tmp_i, tmp_j = i + dir_i, j + dir_j
            is_first = True
            while not self.is_out(tmp_i, tmp_j):
                if is_first:
                    if self.board[tmp_i, tmp_j] in (set(self.player_ids) - set([player,])):
                        is_first = False
                    else:
                        break
                else:
                    if self.board[tmp_i,tmp_j] == player:
                        for tmp_cand in tmp_cands:
                            if tmp_cand not in to_get_panels:
                                to_get_panels.append(tmp_cand)
                        break
                    elif self.board[tmp_i,tmp_j] in EMPTYS:
                        selectable_panels.append((tmp_i, tmp_j))
                        break

                tmp_cands.append((tmp_i, tmp_j))
                tmp_i += dir_i
                tmp_j += dir_j

        return to_get_panels, selectable_panels

    def to_flip_panels(self, i, j, player):
        return self.to_get_select(i, j, player)[0]

    def set_at_chance(self, i, j):
        try:
            if self.board[i, j] in [EMPTY, WALL, FIRST, CHANCE]:
                raise Exception(f"invalid index ({i}, {j})")
            self.board[i, j] = CHANCE
            self.display_board()
            self.history.append(deepcopy(self.board))
            np.savetxt(
                os.path.join(self.savedir, f"at25_{self.game_id:05}_{len(self.history):03}.csv"),
                self.board,
                delimiter=",",
                fmt="%d"
            )
            print(f"save to {self.savedir}/at25_{self.game_id:05}_{len(self.history):03}.csv")

        except Exception as inst:
            print(inst.args)
            exit(1)

    def selectable_panels(self, player):
        if player not in self.player_ids:
            print("invalid player:", player)
            return
        
        if np.any(self.board == FIRST):
            indices = np.where(self.board == FIRST)
            return list(zip(indices[0], indices[1]))
        
        cands = list()
        indices = np.where(self.board == player)
        for i, j in zip(indices[0], indices[1]):
            _, tmp_cands = self.to_get_select(i, j, player)
            for tmp_cand in tmp_cands:
                if tmp_cand not in cands:
                    cands.append(tmp_cand)
        if len(cands) > 0:
            return cands

        cands = list()
        indices = np.where(np.isin(self.board, EMPTYS) == True)
        for i, j in zip(indices[0], indices[1]):
            _, tmp_cands = self.to_get_select(i, j, player)
            for tmp_cand in tmp_cands:
                if tmp_cand not in cands:
                    cands.append(tmp_cand)
        if len(cands) > 0:
            return cands
        
        cands = list()
        indices = np.where(np.isin(self.board, EMPTYS) == True)
        for i, j in zip(indices[0], indices[1]):
            directions = it.product((-1,0,1), repeat=2)
            for dir_i, dir_j in directions:
                if (dir_i, dir_j) == (0, 0):
                    continue            
                tmp_i, tmp_j = i + dir_i, j + dir_j
                if not self.is_out(tmp_i, tmp_j) and self.board[tmp_i,tmp_j] not in EMPTYS:
                    cands.append((i, j))
                    break


        if len(cands) > 0:
            return cands

        cands = list()
        for i in range(self.len_row):
            for j in range(self.len_col):
                if self.board[i,j] not in EMPTYS + [WALL,]:
                    cands.append((i, j))
        return cands

    def flip_panel(self, i, j, player):
        if player not in self.player_ids:
            return
        if (i, j) not in self.selectable_panels(player):
            print("invalid panel:", (i, j))
            return
        to_get_panels = [(i, j)] + self.to_flip_panels(i, j, player)
        print("to_get_panels:", to_get_panels)
        for tmp_i, tmp_j in to_get_panels:
            self.update_panel(tmp_i, tmp_j, player)

        return to_get_panels

    def players_panels(self):
        res = list()
        for p in self.player_ids:
            indices = np.where(self.board == p)
            for i, j in zip(indices[0], indices[1]):
                res.append((i, j))
        return res

    def board_panels(self):
        return self.board