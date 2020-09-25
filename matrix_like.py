import sys, pygame

from config import *

import numpy as np

from random import choice

class game_matrix:
    __slots__ = "grade_type","edit_cubes","round","color_matrix","new_color","sand_board","cube_count","cube_matrix"
    def __init__(self):
        self.cube_matrix = [[0 for j in range(5)] for i in range(3)]
        self.edit_cubes=()
        self.cube_count = 0
        self.sand_board = np.array([[5 for i in range(LEVEL)] for j in range(LEVEL)])
        self.color_matrix = np.array([[-1 for i in range(LEVEL)] for j in range(LEVEL)])
        while True:
            while True:
                self.get_new_cubes(self.sand_board,True)
                # 如果第一排没有5了就结束
                self.move_down(self.sand_board)
                if np.count_nonzero(self.sand_board == 5) == 0:
                    break
            self.match_once((),2)
            self.remove_high_level()
            if np.count_nonzero(self.sand_board==5)==0:
                break
        self.cube_matrix = [[0 for j in range(5)] for i in range(3)]
        # self.sand_board=self.get_sand_board_init()

    def remove_high_level(self):
        self.sand_board=np.where(self.sand_board>10,5,self.sand_board)

    def get_random_cube(self):
        return choice([0, 1, 2])

    def get_next_cube(self):
        queue = FILL_QUEUE# 5/24
        self.cube_count += 1
        return queue[(self.cube_count - 1) % 12]

    def get_new_cubes(self,data,random):
        # 补充第一排
        if random:
            for column in range(LEVEL):
                if data[0][column] == 5:
                    data[0][column] = self.get_random_cube()
                elif data[0][column] < 0:
                    for i in range(1, LEVEL):
                        if data[i][column] == 5:
                            data[i][column] = self.get_random_cube()
                            break
                        elif 0 <= data[i][column] <= 2:
                            break
        else:
            # 统计每列的空格数
            blank_list = np.array(
                [np.count_nonzero(data[:, i] == 5) for i in range(LEVEL)])
            # 统计每列的砖块数
            block_list = np.array([0 for i in range(LEVEL)])
            for column in range(LEVEL):
                for cube in data[:, column]:
                    if cube < 0:
                        block_list[column] += 1
                    else:
                        break
            # 按block数量从小到大出新块
            for blocks in range(max(block_list),min(block_list)-1,-1):
                for column in range(LEVEL):
                    if block_list[column] == blocks and blank_list[column]>0:
                        if data[0][column] == 5:
                            data[0][column] = self.get_random_cube()
                        elif data[0][column] < 0:
                            for i in range(1, LEVEL):
                                if data[i][column] == 5:
                                    data[i][column] = self.get_random_cube()
                                    break
                                elif 0 <= data[i][column] <= 2:
                                    break

    def get_sand_board_init(self):
        temp=SAND_BOARD_INIT
        temp[temp < 0] = temp[temp < 0] * 10 + 5
        temp[temp>0]=temp[temp>0]-1
        return temp

    # 下落
    def move_down(self,data):
        changed = False
        # 下落格数记录
        drop_record=dict()

        # 对于每一列 0~LEVEL-1
        for column in range(LEVEL):
            # 对于每一行  level-1~1
            for i in range(LEVEL - 1):
                row_i = LEVEL - i - 1
                # 如果下面的块不是空的，就pass
                if data[row_i][column] != 5:
                    continue
                # 如果是空的，就找最下面的那个空当
                for j in range(i, LEVEL):
                    row_j = LEVEL - j - 1
                    if data[row_j][column] != 5 and data[row_j][column]>=0:
                        data[row_i][column], data[row_j][column] = data[row_j][column],data[row_i][column]
                        drop_record[(row_j,column)]=row_i-row_j
                        # print((row_j,column),"->",(row_i,column))
                        break
        # 是否进行了下落操作
        return drop_record

    def match_once(self,edit_cubes,pair_mode):
        self.new_color = 0
        self.color_matrix = np.array(
            [[-1 for i in range(LEVEL)] for j in range(LEVEL)])
        # 获得分组
        pair_lists = self.get_pair_lists(self.sand_board, edit_cubes, pair_mode)

        # 统计当前round的得分
        curr_grade = 0
        if GRADE_TYPE == "score based":
            for group in pair_lists:
                curr_grade += ((len(group) - 2) * (pow(3, group[0][2] // 100)))
        elif GRADE_TYPE == "xiao chu wang based":
            for group in pair_lists:
                base_score=0
                if group[0][2] // 100==0:
                    base_score=10
                elif group[0][2] // 100==1:
                    base_score = 40
                elif group[0][2] // 100==2:
                    base_score = 160
                elif group[0][2] // 100==3:
                    base_score = 640
                elif group[0][2] // 100==4:
                    base_score = 4000
                curr_grade += ((len(group) - 2) *base_score)
        elif GRADE_TYPE == "jishu":
            for group in pair_lists:
                level=group[0][2]//100
                monster=group[0][2]%10
                self.cube_matrix[monster][level]+=(len(group) - 2)
        return self.cube_matrix,pair_lists

    def has_pair(self,row, column, data, dir):
        if data[row, column] == 5 or data[row, column]<0:
            return False
        if dir == "u":
            if data[row, column] == data[row - 1, column] == data[
                row - 2, column]:
                return True
        elif dir == "ul":
            if data[row, column] == data[row - 1, column - 1] == data[
                row - 2, column - 2]:
                return True
        elif dir == "ur":
            if data[row, column] == data[row - 1, column + 1] == data[
                row - 2, column + 2]:
                return True
        elif dir == "l":
            if data[row, column] == data[row, column - 1] == data[
                row, column - 2]:
                return True
        else:
            print("error direction")
        return False

    # 找出center并更新color_matrix
    def get_color(self,row, column, dir):
        curr_color = -1
        center = (-1, -1)
        group = set()
        group.add((row, column))
        if dir == "u":
            # 近端
            curr_color = self.color_matrix[row - 1, column] if curr_color == -1 else curr_color
            # 远端
            curr_color = self.color_matrix[row - 2, column] if curr_color == -1 else curr_color
            center = (row - 1, column)
            group.add((row - 1, column))
            group.add((row - 2, column))
        elif dir == "ul":
            curr_color = self.color_matrix[row - 1, column - 1] if curr_color == -1 else curr_color
            curr_color = self.color_matrix[row - 2, column - 2] if curr_color == -1 else curr_color
            center = (row - 1, column - 1)
            group.add((row - 1, column - 1))
            group.add((row - 2, column - 2))
        elif dir == "ur":
            curr_color = self.color_matrix[row - 1, column + 1] if curr_color == -1 else curr_color
            curr_color = self.color_matrix[row - 2, column + 2] if curr_color == -1 else curr_color
            center = (row - 1, column + 1)
            group.add((row - 1, column + 1))
            group.add((row - 2, column + 2))
        elif dir == "l":
            curr_color = self.color_matrix[row, column - 1] if curr_color == -1 else curr_color
            curr_color = self.color_matrix[row, column - 2] if curr_color == -1 else curr_color
            center = (row, column - 1)
            group.add((row, column - 1))
            group.add((row, column - 2))
        else:
            print("error direction")
        # 自身
        # 如果自己没有颜色
        if self.color_matrix[row, column] == -1:
            # 如果延伸两格也没有颜色
            if curr_color == -1:
                # 则设置为新颜色
                curr_color = self.new_color
                self.new_color += 1
            # 如果有颜色
            else:
                # 则不会生成新center
                center = (-1, -1)
        # 如果自己有颜色
        else:
            # 如果延伸两格没颜色
            if curr_color == -1:
                curr_color = self.color_matrix[row, column]
            # 如果延伸两格有颜色
            else:
                pass
            # 则不会生成新center
            center = (-1, -1)
        # fill color
        for point in group:
            self.color_matrix[point[0], point[1]] = curr_color
        return center


    def get_center(self, row, column, data, dir):
        # 如果不在边界上的话
        if (row >= 2 and dir == "u") \
                or (row >= 2 and column >= 2 and dir == "ul") \
                or (row >= 2 and column < len(data) - 2 and dir == "ur") \
                or (column >= 2 and dir == "l"):
            # 如果这个方向上有三连的话
            if self.has_pair(row, column, data, dir):
                # 返回高级块的位置，并给此组的所有方块涂色
                return self.get_color(row, column, dir)
        # 否则返回一个默认值
        return (-1, -1)

    def get_centers(self, row, column, data):
        # 长度应该永远是1，后期可以检查一下
        centers = set()

        directions = ["u", "ul", "ur", "l"]
        # 检查此块的每个方向
        for direction in directions:
            center = self.get_center(row, column, data, direction)
            # 如果有新的center就return
            if center != (-1, -1):
                centers.add(center)
        if len(centers)>1:
            print("一个方块出现多个center!!!!错误！！！！")
        return centers
    def get_pair_lists(self, data, pair, pair_mode):
        centers = set()
        # 对于每一个方格，添加新高级块的位置，并更新颜色矩阵
        for row in range(LEVEL):
            for column in range(LEVEL):
                centers = centers.union(self.get_centers(row, column, data))
        # 遍历颜色矩阵，获得pair_lists
        color_types = list(np.unique(self.color_matrix))
        color_types.remove(-1)
        pair_lists = list()
        # 将方块按照颜色分组
        for color in color_types:
            temp_list = list()
            for row in range(LEVEL):
                for column in range(LEVEL):
                    if self.color_matrix[row][column]==color:
                        # 将消除前的方块加入list
                        temp_list.append((row,column,data[row][column]))
            pair_lists.append(temp_list)
        # 更新data matrix
        for row in range(LEVEL):
            for column in range(LEVEL):
                # 有颜色的话
                if self.color_matrix[row][column] != -1:
                    if 0<=data[row, column]<400:
                        # 如果是center的话就升一级（加一百）
                        if pair_mode == 1 and (row, column) in pair:
                            # switch时center就是switch的两个块
                            data[row, column] += 100
                        elif pair_mode == 2 and (row, column) in centers:
                            # 自由下落时center才会自动生成
                            data[row, column] += 100
                        else:
                            data[row, column] = 5
                    # 否则删除（设置成5）
                    else:
                        data[row, column] = 5
                # 消除石块
                if data[row][column]<0:
                    # 上
                    if row>0 and contain_cube(pair_lists,(row-1,column)):
                        if data[row][column]<0:
                            data[row][column]+=10
                    # 下
                    elif row<LEVEL-1 and contain_cube(pair_lists,(row+1,column)):
                        if data[row][column]<0:
                            data[row][column]+=10
                    # 左
                    elif column>0 and contain_cube(pair_lists,(row,column-1)):
                        if data[row][column]<0:
                            data[row][column]+=10
                    # 右
                    elif column<LEVEL-1 and contain_cube(pair_lists,(row,column+1)):
                        if data[row][column]<0:
                            data[row][column]+=10
        return pair_lists
def contain_cube(pair_lists,position):
    for group in pair_lists:
        for point in group:
            if point[0]==position[0] and point[1]==position[1]:
                return True
    return False


def main():
    a=game_matrix()


if __name__ == '__main__':
    main()