import sys, pygame
from matrix_like import *
from pygame.transform import scale




data = game_matrix()

def main():
    global data
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('mowang simulator')
    # 图片加载
    cube_img_list = load_image()
    block_img = "image/999.png"
    # 方块加载
    cube_surface_list, cube_rect_list = load_cubes(cube_img_list, block_img,
                                                   data.sand_board)

    # 画背景
    draw_bg(screen)
    # 画方块
    draw_cubes(screen,cube_surface_list,cube_rect_list)
    moving = False
    moving_cube_row,moving_cube_column = 0,0
    moving_cube=None
    # total_grade=0
    # cube_matrix = [[0 for j in range(5)] for i in range(3)]
    steps=MAX_STEPS
    # 画文字
    draw_words(screen, data.cube_matrix, steps)
    temp_surface=None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if steps==0:
                font = pygame.font.SysFont("arial", 80)
                grade_label1 = font.render("    Game Over", True,
                                           RED)
                grade_label1.set_alpha(255)
                grade_rect1 = grade_label1.get_rect(topleft=(0, 220))
                screen.blit(grade_label1, grade_rect1)

                font = pygame.font.SysFont("arial", 40)
                grade_label2 = font.render("         Please close this window ", True,
                                           RED)
                grade_label2.set_alpha(255)
                grade_rect2 = grade_label2.get_rect(topleft=(0, 320))
                screen.blit(grade_label2, grade_rect2)
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
            # 鼠标按下，让状态变成可以移动
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y=event.pos
                if x > LENGTH or y > LENGTH:
                    continue
                row, column = get_rect_at(event.pos)
                if data.sand_board[row,column]<0:
                    continue

                moving = True
                moving_cube=cube_surface_list[row, column]
                moving_cube_row,moving_cube_column = row,column
                # 画背景
                draw_bg(screen)
                # 画方块
                draw_cubes(screen, cube_surface_list, cube_rect_list, [
                    cube_surface_list[row,column]])
                # 画文字
                draw_words(screen, data.cube_matrix, steps)
                temp_surface=screen.copy()

            # 鼠标弹起，让状态变成不可以移动
            if event.type == pygame.MOUSEBUTTONUP and moving:
                x,y=event.pos
                if x>LENGTH or y>LENGTH:
                    if not moving:
                        continue
                    steps -= 1
                    # 计算得分
                    if GRADE_TYPE == "score based":
                        color = data.sand_board[moving_cube_row][moving_cube_column]
                        # total_grade += (pow(3, color // 100))
                    elif GRADE_TYPE == "xiao chu wang based":
                        color=data.sand_board[moving_cube_row][moving_cube_column]
                        base_score = 0
                        if color // 100 == 0:
                            base_score = 10
                        elif color // 100 == 1:
                            base_score = 40
                        elif color // 100 == 2:
                            base_score = 160
                        elif color // 100 == 3:
                            base_score = 640
                            steps += 1
                        elif color // 100 == 4:
                            base_score = 4000
                            steps += 1
                        # total_grade += base_score
                    elif GRADE_TYPE == "jishu":
                        color = data.sand_board[moving_cube_row][
                            moving_cube_column]
                        level = color // 100
                        monster = color % 10
                        data.cube_matrix[monster][level] += 1
                        if level>=3:
                            steps+=1
                    # 从matrix和surface中删除
                    data.sand_board[moving_cube_row][moving_cube_column]=5
                    cube_surface_list[moving_cube_row, moving_cube_column]=None
                    # 画背景
                    draw_bg(screen)
                    # 画方块
                    draw_cubes(screen, cube_surface_list, cube_rect_list, [
                        cube_surface_list[row, column]])
                    # 画文字
                    draw_words(screen, data.cube_matrix, steps)
                    temp_surface = screen.copy()
                else:
                    steps -= 1
                    # 交换surface中的方块
                    row, column = get_rect_at(event.pos)
                    if row==moving_cube_row and column==moving_cube_column:
                        steps += 1
                    if  data.sand_board[row,column]<0:
                        steps += 1
                        row=moving_cube_row
                        column=moving_cube_column
                    cube_surface_list[moving_cube_row, moving_cube_column] \
                        , cube_surface_list[row, column] \
                        = cube_surface_list[row, column], moving_cube
                    # 交换matrix中的方块
                    data.sand_board[row, column], data.sand_board[
                        moving_cube_row, moving_cube_column] \
                        = data.sand_board[moving_cube_row, moving_cube_column], \
                          data.sand_board[row, column]
                    """消除交换后的块"""
                    temp_cube_matrix, pair_lists = data.match_once(
                        ((row, column), (moving_cube_row, moving_cube_column)),
                        1)
                    # # 增加分数
                    # for i,monster in enumerate(temp_cube_matrix,0):
                    #     for j,level in enumerate(monster,0):
                    #         cube_matrix[i][j]+=level
                    # 存储被消除的块
                    pair_cubes = list()
                    for groups in pair_lists:
                        for points in groups:
                            pair_cubes.append(
                                cube_surface_list[points[0]][points[1]])
                    # 闪动动画
                    flash_cubes(screen, cube_surface_list, cube_rect_list,
                                pair_cubes, data.cube_matrix, steps)
                    # 更新沙盘
                    cube_surface_list, cube_rect_list = load_cubes(
                        cube_img_list,block_img, data.sand_board)

                """消除掉落的块"""
                while np.count_nonzero(data.sand_board == 5) != 0:
                    # 记录掉落的块
                    drop_record = data.move_down(data.sand_board)
                    # 旧方块掉落动画
                    drop_cubes(screen, drop_record, cube_rect_list,
                               cube_surface_list, data.cube_matrix, steps)
                    # 新方块掉落动画
                    while True:
                        data.get_new_cubes(data.sand_board, False)
                        # 加载方块
                        cube_surface_list, cube_rect_list = load_cubes(
                            cube_img_list,block_img, data.sand_board)
                        # 记录掉落的块
                        drop_record = data.move_down(data.sand_board)
                        # 掉落动画
                        drop_cubes(screen, drop_record, cube_rect_list,
                                   cube_surface_list, data.cube_matrix, steps)
                        if np.count_nonzero(data.sand_board == 5) == 0:
                            break
                    # 继续消除
                    temp_cube_matrix, pair_lists = data.match_once((), 2)
                    # for i, monster in enumerate(temp_cube_matrix, 0):
                    #     for j, level in enumerate(monster, 0):
                    #         cube_matrix[i][j] += level
                    # 存储被消除的块
                    pair_cubes = list()
                    for groups in pair_lists:
                        for points in groups:
                            pair_cubes.append(
                                cube_surface_list[points[0]][points[1]])
                    # 闪动动画
                    flash_cubes(screen, cube_surface_list, cube_rect_list,
                                pair_cubes, data.cube_matrix, steps)

                    cube_surface_list, cube_rect_list = load_cubes(
                        cube_img_list,block_img, data.sand_board)
                moving = False



            # 鼠标移动对应的事件
            if event.type == pygame.MOUSEMOTION:
                if moving:
                    screen.blit(temp_surface, temp_surface.get_rect())
                    # 画移动中的方块
                    x, y = event.pos
                    image_w, image_h = moving_cube.get_size()
                    ## 保证鼠标在图片的中心
                    image_y = y - image_h / 2
                    image_x = x - image_w / 2
                    screen.blit(moving_cube, (int(image_x), int(image_y)))
                    pygame.display.update()



        pygame.display.update()


def get_rect_at(position):
    x, y = position
    x -= BORDER_WIDTH / 2
    y -= BORDER_WIDTH / 2
    row = y // DELTA
    column = x // DELTA
    return int(row), int(column)
def draw_grid(screen, color):
    start = []
    end = []
    for x in range(0, LEVEL + 1):
        start.append((int(x * DELTA + BORDER_WIDTH / 2), 0))
        end.append(
            (int(x * DELTA + BORDER_WIDTH / 2), int(LENGTH + BORDER_WIDTH/2)))
    for y in range(0, LEVEL + 1):
        start.append((0, int(y * DELTA + BORDER_WIDTH / 2)))
        end.append(
            (int(LENGTH + BORDER_WIDTH/2), int(y * DELTA + BORDER_WIDTH / 2)))

    for i in range(len(start)):
        pygame.draw.line(screen, color, start[i], end[i], BORDER_WIDTH)

def load_image():
    cube_img_list = [[] for type in range(3)]
    for level in range(5):
        for type in range(3):
            cube_img_list[type].append(
                'image/%s.png' % (str(type) + str(level)))
    return cube_img_list
def load_cubes(cube_img_list,block_img,data):
    cube_surface_list = np.array(
        [[None for j in range(LEVEL)] for i in range(LEVEL)])
    cube_rect_list = np.array(
        [[None for j in range(LEVEL)] for i in range(LEVEL)])
    for row in range(LEVEL):
        for column in range(LEVEL):
            cube_value = data[row,column]
            if cube_value==5:
                continue
            # 石块
            if data[row][column]<0:
                cube_surface = scale(
                    pygame.image.load(block_img),
                    (int(CUBE_LENGTH), int(CUBE_LENGTH)))
                    # (int(CUBE_LENGTH * 2 / 3), int(CUBE_LENGTH * 2 / 3)))
            # 方块
            else:
                cube_type = cube_value % 100
                cube_level = cube_value // 100
                cube_surface = scale(
                    pygame.image.load(cube_img_list[cube_type][cube_level]),
                    (int(CUBE_LENGTH), int(CUBE_LENGTH)))
                # (int(CUBE_LENGTH * 2 / 3), int(CUBE_LENGTH * 2 / 3)))
            cube_rect = cube_surface.get_rect(
                topleft=(int(BORDER_WIDTH + column * DELTA),
                         int(BORDER_WIDTH + row * DELTA)))
                # topleft=(int(BORDER_WIDTH+CUBE_LENGTH/6 + column * DELTA),
                #          int(BORDER_WIDTH+CUBE_LENGTH/6 + row * DELTA)))
            cube_surface_list[row, column] = cube_surface
            cube_rect_list[row, column] = cube_rect
    return cube_surface_list,cube_rect_list

bg_with_grid=None
def draw_bg(screen):
    global bg_with_grid
    if bg_with_grid==None:
        # 背景涂白
        screen.fill(WHITE)
        # 画网格线
        draw_grid(screen, BLACK)
        bg_with_grid=screen.copy()
    else:
        screen.blit(bg_with_grid, bg_with_grid.get_rect())


def draw_cubes(screen,cube_surface_list,cube_rect_list,removed_cube_list=None):
    global data
    for row, column in np.ndindex(cube_surface_list.shape):
        if cube_surface_list[row, column]==None:
            continue
        if removed_cube_list is not None and cube_surface_list[row, column] in removed_cube_list:
            continue
        screen.blit(cube_surface_list[row, column], cube_rect_list[row, column])
        if data.sand_board[row, column]<0:
            value=int((-data.sand_board[row, column])//10+1)
            # 显示剩余次数
            font = pygame.font.SysFont("arial", 20)
            break_label = font.render("x" + str(int(value)), True,WHITE)
            break_label.set_alpha(255)
            break_rect = break_label.get_rect(topleft=(int(column*DELTA+CUBE_LENGTH/3), int(row*DELTA+CUBE_LENGTH/2)))
            screen.blit(break_label, break_rect)

def draw_words(screen,cube_matrix,steps):
    font = pygame.font.SysFont("arial", 20)
    # grade_type = font.render("    w  g  b  p  o", True, BLACK)
    # grade_type.set_alpha(255)
    # grade_type_rect = grade_type.get_rect(topleft=(0, 500))
    grade_label1 = font.render(" ∆: "+str(cube_matrix[0]), True, BLACK)
    grade_label1.set_alpha(255)
    grade_rect1 = grade_label1.get_rect(topleft=(0, 520))
    grade_label2 = font.render(" ○: "+str(cube_matrix[1]), True, BLACK)
    grade_label2.set_alpha(255)
    grade_rect2 = grade_label2.get_rect(topleft=(0, 540))
    grade_label3 = font.render(" □: "+str(cube_matrix[2]), True, BLACK)
    grade_label3.set_alpha(255)
    grade_rect3 = grade_label3.get_rect(topleft=(0, 560))
    step_label = font.render("Steps left: "+str(steps), True, BLACK)
    step_label.set_alpha(255)
    step_rect = step_label.get_rect(topleft=(0, 580))
    # screen.blit(grade_type, grade_type_rect)
    screen.blit(grade_label1, grade_rect1)
    screen.blit(grade_label2, grade_rect2)
    screen.blit(grade_label3, grade_rect3)
    screen.blit(step_label, step_rect)

def flash_cubes(screen,cube_surface_list,cube_rect_list,pair_cubes,cube_matrix, steps):

    exclude_cubes=[i for i in cube_surface_list.flatten() if i not in pair_cubes]
    draw_bg(screen)
    draw_cubes(screen, cube_surface_list, cube_rect_list, pair_cubes)
    draw_words(screen, cube_matrix, steps)
    # 存储没有选定cube的图像
    temp_surface = screen.copy()
    for i in range(FLASH_TIMES):
        pygame.time.delay(int(700 / FLASH_SPEED))
        # 显示
        draw_cubes(screen, cube_surface_list, cube_rect_list,exclude_cubes)
        pygame.display.update()
        pygame.time.delay(int(700 / FLASH_SPEED))
        # 不显示
        draw_cubes(screen, cube_surface_list, cube_rect_list,exclude_cubes)
        screen.blit(temp_surface, temp_surface.get_rect())
        pygame.display.update()

def drop_cubes(screen,drop_record,cube_rect_list,cube_surface_list,total_grade, steps):
    # 存储没有选定cube的图像
    draw_bg(screen)
    draw_words(screen, total_grade, steps)
    temp_surface = screen.copy()

    # 开始掉落
    for time in range(10):
        if time!=0:
            pygame.time.delay(int(200 / DROP_SPEED))
        for point in drop_record:
            if cube_rect_list[point[0]][point[1]][1]==None:
                continue
            cube_rect_list[point[0]][point[1]][1] += int(
                DELTA * drop_record[point] / 10)
        screen.blit(temp_surface, temp_surface.get_rect())
        draw_cubes(screen, cube_surface_list, cube_rect_list)
        pygame.display.update()




if __name__ == '__main__':
    main()
