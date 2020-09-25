import numpy as np
GRADE_TYPE="jishu"
# 动画参数
DROP_SPEED=10
FLASH_SPEED=10
FLASH_TIMES=3

# 沙盘参数
WIDTH=600
HEIGHT=650
BORDER_WIDTH=5

# 游戏参数

# FILL_QUEUE="110220212100"
FILL_QUEUE="221001020211"
MAX_STEPS=100
LEVEL=6
# SAND_BOARD_INIT=np.array(  [[  1,-12,2,-13,  1],
#                             [-14,  2,3,  2,-12],
#                             [  3,  1,1,  3,  3],
#                             [  3,  3,2,  1,  2],
#                             [-13,  2,2,  1, -8]])
SAND_BOARD_INIT=np.array(  [[  1,  1,2,  2,  3],
                            [  1,  3,3,  1,  3],
                            [-17,  3,1,  1, -2],
                            [-13,-12,3,-14,-10],
                            [-10,  3,1,  1, -4]])

# 棋盘长/宽
LENGTH=500
DELTA=round(LENGTH/LEVEL)
CUBE_LENGTH=int(LENGTH/LEVEL-BORDER_WIDTH)



# 颜色参数
WHITE=(255, 255, 255)
RED=(255, 0, 0)
BLACK=(0,0,0)