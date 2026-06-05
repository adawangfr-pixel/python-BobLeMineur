# --------------------------
# Importations de librairies
# --------------------------

import pygame
import sys
import math
import random
pygame.font.init()

# -----------------------
# Constantes du programme
# -----------------------

# ----- Couleurs.
ROCHE   = (100, 100, 100)
TUNNEL  = (255, 255, 255)
TERRE   = (160, 82, 45)
BACKGROUND = (255, 255, 255)  # 细节 2 — 岩石颜色与背景颜色相同，地图难以辨认
WATER   = (173, 216, 230) # 设置水的颜色 change-4.1
BLACK = (0, 0, 0)
RED = 	(128,0,0)
GREEN = (34,139,34)
WHITE = (255, 255, 255)
# ----- Taille de chaque case de la vue de la grille de jeu.
CASE = 40
ITEM_SIZE = 36
STATUS_BAR_HEIGHT = 80 # 预设状态栏的高度 change-2.1
DRAW_PADDING_Y =  40 # 设定整个游戏添加元素前的y轴偏移量 change-2.1
DRAW_PADDING_X =  40 # 设定整个游戏添加元素前的x轴偏移量 change-2.1
MAP_OFFSET_X = DRAW_PADDING_X # 设定游戏地图绘画的起始点x轴偏移量 change-2.1
MAP_OFFSET_Y = DRAW_PADDING_Y + STATUS_BAR_HEIGHT # 设定游戏地图绘画的起始点y轴偏移量 change-2.1

STATE_ICON_SIZE = 20
# ----- Icônes.
ico_mineur  = pygame.transform.scale(pygame.image.load("ico/mineur.png"), (ITEM_SIZE, ITEM_SIZE))
ico_diamant = pygame.transform.scale(pygame.image.load("ico/diamant.png"), (ITEM_SIZE, ITEM_SIZE))
ico_exit = pygame.transform.scale(pygame.image.load("ico/cave-exit.png"), (ITEM_SIZE, ITEM_SIZE)) # 出口贴图 change-1

ico_bomb_status = pygame.transform.scale(pygame.image.load("ico/bomb.png"), (STATE_ICON_SIZE, STATE_ICON_SIZE)) # 炸弹装备贴图 change-2.1
ico_bubble = pygame.transform.scale(pygame.image.load("ico/bubbles.png"), (STATE_ICON_SIZE, STATE_ICON_SIZE)) # 气泡装备贴图 change-2.1

ico_bomb = pygame.transform.scale(pygame.image.load("ico/bomb.png"), (ITEM_SIZE, ITEM_SIZE)) # 炸弹道具贴图 change-2.3
ico_oxygen = pygame.transform.scale(pygame.image.load("ico/oxygen.png"), (ITEM_SIZE, ITEM_SIZE)) # 氧气瓶道具贴图 change-2.3

ico_bomb_ignite = pygame.transform.scale(pygame.image.load("ico/bomb-explode.png"), (ITEM_SIZE, ITEM_SIZE)) # 被点燃的炸弹贴图 change-3.1
ico_bomb_bang = pygame.transform.scale(pygame.image.load("ico/bang-64.png"), (ITEM_SIZE*2, ITEM_SIZE*2)) # 炸弹爆炸时贴图 change-3.2

ico_monster_standby =  pygame.transform.scale(pygame.image.load("ico/monster_standby.png"), (ITEM_SIZE, ITEM_SIZE)) # 怪兽待命贴图 change-5.1
ico_monster_attack =  pygame.transform.scale(pygame.image.load("ico/monster_attack.png"), (ITEM_SIZE, ITEM_SIZE)) # 怪兽攻击贴图 change-5.1
ico_monster_dead =  pygame.transform.scale(pygame.image.load("ico/monster_dead.png"), (ITEM_SIZE, ITEM_SIZE)) # 怪兽死了贴图 change-5.1
# ----- game settings
DAMAGE = {
    'bomb':40,
    'monster':20,
}
WAIT = {
    'bob_action':500,
    'monster_action':500,
    'magic_movement':100,
    'bomb_ignite':2000,
    'bomb_explode':1000
}
MONSTER_STEPS = 10
# ---------------
# Sous-programmes
# ---------------

# ----- Fonction de chargement du jeu.

def chargement_jeu (fichier):

    with open(fichier, 'r', encoding='utf-8') as f:
        ht = int(f.readline().strip())  # Lecture du nombre de lignes.
        lg = int(f.readline().strip()) # Lecture du nombre de colonnes.

        # ----- Lecture de chaque ligne du fichier / grille.
        gr = [] # Grille
        bombs_loc = set() # 炸弹道具所在地方集合 Set(Tuple)
        oxygen_loc = set() # 氧气瓶道具所在地方集合 Set(Tuple)
        monster_lst = []
        for i in range(ht):
            line = f.readline().strip().replace('\ufeff','')  # Lecture d'une ligne du fichier.
            items = line.split(";")

            lig = []
            for j in range(lg):
                valeur = items[j] 

                # ----- Les cases.
                # Chaque case de la grille est de nature différente.
                if valeur in ['0','1','2','3']: # 新增一个水的材质，使用数字3表示 change-4.1
                    lig.append(valeur)

                elif valeur == 'B':
                    lig.append('0')

                    # ----- Bob le mineur.
                    # Bob est défini par sa position initiale sur la grille et un icone.
                    bo = [i, j, ico_mineur]

                elif valeur == 'D':
                    lig.append('2')

                    # ----- Le diamant.
                    # Le diamant est défini par sa position sur la grille et un icone.
                    di = [i, j, ico_diamant]

                elif valeur == 'E': # 添加出口位置 change-1
                    exit = [i,j,ico_exit]
                    lig.append('0')
                elif valeur == 'P': # 添加炸弹位置 change-2.3
                    bombs_loc.add((i,j))
                    lig.append('0')
                elif valeur == 'X': # 添加氧气瓶位置 change-2.3
                    oxygen_loc.add((i,j))
                    lig.append('0')
                elif valeur == 'M': # 添加怪兽的位置 change-5.1
                    monster = {
                        'pos':(i,j), # 所在位置
                        'health':100,# 生命
                        'state':0,   # 状态：0-standby,1-chasing,2-attack,3-dead
                        'next_move':(i,j), # 下一步移动位置
                        'next_move_time':0,# 下一动作启动时间
                        'move_routine':[], # 预设位移路线
                        'move_cursor':0,   # 位移路线中当前所使用的下标
                    }
                    monster_lst.append(monster)
                    lig.append('0')
            
            gr.append(lig)

    return gr, bo, di, exit,bombs_loc, oxygen_loc, monster_lst


# ----- Procédure pour visualiser la grille de jeu, le mineur et les objets.
 # Draw staus 状态栏
def visualise_state(fen, state):
    # change-2.2
    num_bomb = state['bomb'] # 炸弹数量
    num_air = state['air']   # 氧气数量
    icon_margin = 3 # 状态栏道具上下间距
    text_size = 14 # 道具说明字体大小
    icon_offset_x = DRAW_PADDING_X + 50 # 状态栏图标x轴偏移量
    bomb_offset_y = DRAW_PADDING_Y + STATE_ICON_SIZE + icon_margin # 炸弹图标状态栏y轴偏移量
    air_offset_y = bomb_offset_y + STATE_ICON_SIZE + icon_margin   # 氧气图标状态栏y轴偏移量

    # change-2.1------
    # 血条参数
    bar_width = 200
    bar_height = 20
    current_health = state['health']
    max_health = 100
    # 绘制血条背景（红色）
    pygame.draw.rect(fen, RED, (icon_offset_x, DRAW_PADDING_Y, bar_width, bar_height))
    
    # 绘制血条前景（绿色，根据当前血量比例）
    health_ratio = current_health / max_health
    current_bar_width = bar_width * health_ratio
    pygame.draw.rect(fen, GREEN, (icon_offset_x, DRAW_PADDING_Y, current_bar_width, bar_height))
    
    # 可选：添加边框
    pygame.draw.rect(fen, WHITE, (icon_offset_x, DRAW_PADDING_Y, bar_width, bar_height), 3)
    
    # 可选：显示血量文字
    font = pygame.font.SysFont("Arial", text_size)
    text_hp = font.render(f"HP: ", True, (200, 255, 255))
    fen.blit(text_hp, (DRAW_PADDING_X, DRAW_PADDING_Y))
    # -------------
    # change-2.2
    # Bomb 道具
    text_o = pygame.font.SysFont("Arial", text_size).render("Bomb: ", True, (200, 255, 255))
    fen.blit(text_o, (DRAW_PADDING_X ,bomb_offset_y))

    for boom_i in range(num_bomb):
        fen.blit(ico_bomb_status, (icon_offset_x + boom_i*STATE_ICON_SIZE , bomb_offset_y))
    # Oxygen 道具
    text_o = pygame.font.SysFont("Arial", text_size).render("Oxygen: ", True, (200, 255, 255))
    fen.blit(text_o, (DRAW_PADDING_X ,air_offset_y))

    for air_i in range(num_air):
        fen.blit(ico_bubble, (icon_offset_x + air_i*STATE_ICON_SIZE , air_offset_y))
# 透明度正弦变化
def flashing_alpha(speed = 8):
    # 返回透明度Alph值（100-255），按照正弦函数变化，可根据speed调整闪烁的速度 
    current_time = pygame.time.get_ticks()
    return int(100 + 155 * (math.sin(current_time * 0.001* speed) + 1) / 2)

def visualise_jeu (grl, mineur, dia, exit, state,bomb_loc, oxygen_loc, bomb_set_loc, monster_lst, fen): # change-1, change-2.1

    # Efface la fenêtre.
    # fen.fill(BACKGROUND) # change-2.1
    
    fen.blit(background, (0, 0)) # 设置游戏背景图片

    # Lecture de la grille et visualisation des cases.
    # '0' -> TUNNEL
    # '1' -> ROCHE
    # '2' -> TERRE
    # ‘3’ -> WATER

    # Draw staus 状态栏------
    visualise_state(fen, state)
    # ----------
    # Draw map 游戏地图
    
    for lig in range(len(grl)):
        for col in range(len(grl[0])):
            carre = pygame.Rect(MAP_OFFSET_X + col * CASE, MAP_OFFSET_Y+ lig * CASE, CASE, CASE) # change-2.1

            if grl[lig][col] == '1':
                pygame.draw.rect(fen, ROCHE, carre)
            elif grl[lig][col] == '0':
                pygame.draw.rect(fen, TUNNEL, carre)
            elif grl[lig][col] == '2':
                pygame.draw.rect(fen, TERRE, carre)
            elif grl[lig][col] == '3':
                pygame.draw.rect(fen, WATER, carre)
            else:
                pygame.draw.rect(fen, BACKGROUND, carre)  # avoid color switching

    # Affichage du diamant. change-2.1
    fen.blit(dia[2], (MAP_OFFSET_X + dia[1] * CASE, MAP_OFFSET_Y + dia[0] * CASE))

    # Affichage du mineur. change-2.1
    fen.blit(mineur[2], (MAP_OFFSET_X + mineur[1]*CASE, MAP_OFFSET_Y + mineur[0]*CASE))

    # Affichage du exit. change-1 change-2.1
    fen.blit(exit[2], (MAP_OFFSET_X + exit[1]*CASE, MAP_OFFSET_Y + exit[0]*CASE))

    # Set bomb 用户部署的炸弹 # change 3.1
    for bomb in bomb_set_loc:
        if bomb_set_loc[bomb][0] == 0: # set bomb 只部署未引爆
            fen.blit(ico_bomb_ignite, (MAP_OFFSET_X + bomb[1]*CASE, MAP_OFFSET_Y + bomb[0]*CASE))
        elif bomb_set_loc[bomb][0] == 1: # explode 已经点燃 change 3.2
            # 炸弹爆炸前闪烁
            bomb_surf = ico_bomb_ignite.copy()  # 复制一份，避免修改原图

            alpha = flashing_alpha()
            bomb_surf.set_alpha(alpha)  # 设置透明度
            fen.blit(bomb_surf,(MAP_OFFSET_X + bomb[1]*CASE, MAP_OFFSET_Y + bomb[0]*CASE))
        elif bomb_set_loc[bomb][0] == 2: # 已经爆炸
            # 设置图片中心点
            center_pos = (0.5*CASE + MAP_OFFSET_X + bomb[1]*CASE, 0.5*CASE + MAP_OFFSET_Y + bomb[0]*CASE)
            # 根据图片大小换算左上角坐标
            bang_rect = ico_bomb_bang.get_rect(center=center_pos)
            fen.blit(ico_bomb_bang, bang_rect)
            
            
    # change-2.3
    # Draw Bomb 炸弹道具布置
    for bomb in bomb_loc:
        fen.blit(ico_bomb, (MAP_OFFSET_X + bomb[1]*CASE, MAP_OFFSET_Y + bomb[0]*CASE))
    # Draw Oxygen 氧气瓶道具布置
    for oxy in oxygen_loc:
        fen.blit(ico_oxygen, (MAP_OFFSET_X + oxy[1]*CASE, MAP_OFFSET_Y + oxy[0]*CASE))
    # change-5.1
    # 放置怪兽
    for monster in monster_lst:
        if monster['state'] == 2:
            ico = ico_monster_attack
        elif monster['state'] == 3:
            ico = ico_monster_dead
        else:
            ico = ico_monster_standby

        fen.blit(ico, (MAP_OFFSET_X + monster['pos'][1]*CASE, MAP_OFFSET_Y + monster['pos'][0]*CASE))

# ----- Retourne la position dans la grille (ligne,colonne)
# du pixel sur lequel l'utilisateur a cliqué.

def position (pixel):# 根据鼠标点击位置判断当前所在单元格 change-3.2
    # 先删除偏移量，再计算所在单元格编号
    y = pixel[1] - MAP_OFFSET_Y
    x = pixel[0] - MAP_OFFSET_X
    if x<0 or y<0:
        return None,None
    return y // CASE, x // CASE

def checkBomb(grille, bob, bomb_set_loc, monster_lst): # 检查布置的炸弹状态并更新 change-3.2
    current_time = pygame.time.get_ticks()
    bomb_key_to_remove = [] # 缓存需要删除的炸弹
    for bomb in bomb_set_loc:
        # 如果炸弹已经点燃，而且爆炸时间已到
        if bomb_set_loc[bomb][0] == 1 and bomb_set_loc[bomb][1] < current_time:
            bomb_set_loc[bomb][0] = 2 # 炸弹状态设置为爆炸
            # 设定需要被炸弹清理的方块相对位置
            clear_lst = [(i,j) for i in [1, 0 ,-1] for j in [1, 0 ,-1] ] 
            # 清理炸弹
            for i,j in clear_lst:
                # 如果当前位置不是“水”就清理为“通道”
                if grille[bomb[0]+i][bomb[1]+j] != '3':
                    grille[bomb[0]+i][bomb[1]+j] = '0'
                # 如果Bob站在了爆炸波及范围，则Bob受重伤
                if bomb[0]+i == bob[0] and bomb[1]+j == bob[1]:
                    state['health'] -= DAMAGE['bomb']
                # 如果怪兽在附近则被波及
                for monster in monster_lst:
                    mons_pos = monster['pos']
                    if bomb[0]+i == mons_pos[0] and bomb[1]+j == mons_pos[1]:
                        monster['health'] -= DAMAGE['bomb']
            pause_until = pygame.time.get_ticks() + WAIT['bomb_explode']   # 暂停 1000 毫秒 = 1 秒
            bomb_set_loc[bomb][1] = pause_until # 设置爆炸特效展示时长
        # 如果炸弹已经爆炸，且图片展示时间已到，记录需要删除的炸弹
        elif bomb_set_loc[bomb][0] == 2 and bomb_set_loc[bomb][1] < current_time:
            bomb_key_to_remove.append(bomb)
    # 删除所有已经完成爆炸的炸弹
    for key in bomb_key_to_remove:
        del bomb_set_loc[key]
    return True

# bresenham算法，计算两个点连成的直线里会经过的方格
def bresenham_line(pos1, pos2):
    x0, y0 = pos1
    x1, y1 = pos2 
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

# 判断两个点之间是否有岩石/土壤遮挡视线
def line_of_sight(grille, pos1, pos2):
    # pos1, pos2: (lig, col)
    line = bresenham_line(pos1, pos2)  # (col, lig)
    blocked_types = {'1', '2'}
    for p in line[1:-1]:  # exclude start and end
        if grille[p[0]][p[1]] in blocked_types:
            return False,None
    return True,line
# 判断是否位置可访问
def accessible(grille,pos):
    return grille[pos[0]][pos[1]] not in {'1', '2'}
# 两个点之间的路程
def distance(pos1,pos2):
    dx = abs(pos1[0]-pos2[0])
    dy = abs(pos1[1]-pos2[1])
    return dx+dy
# teste si une position 边界检测
def dans_grille(lig, col, grille):
    return 0 <= lig < len(grille) and 0 <= col < len(grille[0])
# 怪兽探测bob与钻石
def monster_detect(grille, monster_lst, bob,diamant):
    bob_pos = bob[0],bob[1]
    diamant_pos = diamant[0],diamant[1]
    for monster in monster_lst:
        monster_pos = monster['pos']
        # 如果状态为已死亡则跳过
        if monster['state'] == 3:
            continue
        # 超出视野可以不管
        bob_dist = distance(bob_pos,monster_pos)
        # 距离大于3，重制状态
        if  bob_dist > 3:
            if monster['state'] == 1 or monster['state'] == 2:
                # 已经见不到bob需要重新初始化路线
                monster['move_routine'] = []
                monster['move_cursor'] = 0
            monster['state'] = 0
            continue
        # 距离小于等于1进入追击状态
        if bob_dist <= 1:
            monster['state'] = 2 
            monster['next_move'] = monster_pos
            continue

        bob_seen, bob_line = line_of_sight(grille, monster_pos, bob_pos) if bob_dist <= 3 else (False,None)
        # 遇到bob且钻石没挡路
        if bob_seen and diamant_pos not in bob_line:
            next_move = bob_line[1]
            if distance(next_move, monster_pos) == 2: # 斜对角
                dx_next_move = (next_move[0], monster_pos[1])
                dy_next_move = (monster_pos[0],next_move[1])
                if accessible(grille, dx_next_move):
                    next_move = dx_next_move
                elif accessible(grille, dy_next_move):
                    next_move = dy_next_move
                else:
                    next_move = monster_pos
                
            monster['next_move'] = next_move # bob_line[0]为怪兽自己所在位置
            monster['state'] = 1
            
# 怪兽阻挡检测 change-5.1
def monster_blockage(monster_lst, lig,col):
    for monster in monster_lst:
        mon_pos = monster['pos']
        if mon_pos[0]== lig and mon_pos[1] == col:
            return True
    return False
# 怪物路线生成器 change-5.3
def monster_routine(monster_lst, grille):
    for monster in monster_lst:
        mon_step = len(monster['move_routine'])
        if mon_step >= MONSTER_STEPS or monster['state']!=0: # 如果不是standby
            continue
        cur_mon_pos = monster['pos']
        for i in range(MONSTER_STEPS//2):
            option = [] # 生成可选的移动位置，必须是通道或者水路
            for i,j in [(1,0),(-1,0),(0,1),(0,-1)]:
                cur_pos = (cur_mon_pos[0]+i, cur_mon_pos[1]+j)
                if grille[cur_pos[0]][cur_pos[1]] == '0' or grille[cur_pos[0]][cur_pos[1]] == '3':
                    option.append((i,j))
            # 随机选择一个位置
            next_move = option[random.randint(0,len(option)-1)]
            # 假设移动到新的位置，再次循环判断可选走向
            cur_mon_pos =  (cur_mon_pos[0]+next_move[0], cur_mon_pos[1]+next_move[1])
            monster['move_routine'].append(next_move)
        # 根据前面移动的轨迹，进行反向巡逻
        reversed = monster['move_routine'][::-1]
        reversed = [[i*-1,j*-1] for i,j in reversed]
        monster['move_routine'] += reversed
        
# 怪物移动 change-5.4
def move_monster(monster_lst,bob):
    del_list = []
    for monster in monster_lst:
        current_time = pygame.time.get_ticks()
        # 如果未到行动时间，则跳过
        if monster['next_move_time'] > current_time:
            continue
        # 如果是待命状态，则设置下一个移动地点，并更新游标
        if monster['state'] == 0:
            next_shift = monster['move_routine'][monster['move_cursor']]
            monster['next_move'] = (monster['pos'][0] + next_shift[0], monster['pos'][1] + next_shift[1])
            monster['move_cursor'] = (monster['move_cursor'] +1) % MONSTER_STEPS
        elif monster['state'] == 2:
            if distance(monster['pos'],(bob[0],bob[1])) == 1:
                state['health'] -= DAMAGE['monster']
        elif monster['state'] == 3:
            del_list.append(monster)
        # 移动怪兽并设置新的行动时间
        monster['pos'] = monster['next_move']
        monster['next_move_time'] += WAIT['monster_action']
        if monster['health'] <=0:
            monster['state'] = 3
    for mon in del_list:
        monster_lst.remove(mon)
# -------------------
# Programme principal
# -------------------

# ----- Chargement du jeu et du mineur.
grille, bob, diamant, exit, bomb_loc, oxygen_loc, monster_lst = chargement_jeu('grille.txt')  # change-1 change-2.2
'''
exit: 出口所在地 [i,j,surface]
bomb_loc: 炸弹道具所在地 Set(Tuple(i,j))
oxygen_loc: 氧气瓶道具所在地 Set(Tuple(i,j))
'''

# ----- La vue.
# La vue est une représentation de la grille de jeu dans
# une fenêtre graphique.

vue_hauteur = len(grille) * CASE + DRAW_PADDING_Y*2 + STATUS_BAR_HEIGHT
vue_largeur = len(grille[0]) * CASE + DRAW_PADDING_X*2



vue = pygame.display.set_mode((vue_largeur, vue_hauteur))
pygame.display.set_caption("Bob le mineur !")
# 添加背景图片加载 change-2.1
background = pygame.image.load("ico/background.png").convert_alpha()
# 如果图片大小和窗口不一致，可以缩放 change-2.1
background = pygame.transform.scale(background, (vue_largeur, vue_hauteur))

#----- La boucle du jeu.
joue = True
heure = pygame.time.Clock()
# 玩家状态初始化：change-2.1
state = {'health':100,'bomb':3,'air':6}
bomb_set_loc = {} # 用户部署的炸弹 change-3.1 (x,y): [state, time], state: 0 - set, 1-ignite, 2-exploded


while joue:
    monster_detect(grille, monster_lst, bob, diamant)
    monster_routine(monster_lst, grille)
    move_monster(monster_lst,bob)
    for evt in pygame.event.get():
        # 退出事件处理
        if evt.type == pygame.QUIT:
            joue = False

        if evt.type == pygame.KEYDOWN:

            mv_lig = 0
            mv_col = 0

            # flèches directionnelles
            if evt.key == pygame.K_LEFT:
                mv_col = -1
            if evt.key == pygame.K_RIGHT:
                mv_col = 1
            if evt.key == pygame.K_UP:
                mv_lig = -1
            if evt.key == pygame.K_DOWN:
                mv_lig = 1
            

            # Si aucune flèche n'a été appuyée --细节 1 — 在 KEYDOWN 中未处理无方向键的情况（但无影响） change-3.1
            # if mv_lig == 0 and mv_col == 0:
            #     continue

            nouvelle_lig = bob[0] + mv_lig
            nouvelle_col = bob[1] + mv_col
            case_cible = grille[nouvelle_lig][nouvelle_col]
            
            # 移动拦截条件，任一成立则continue
            if any([
                not dans_grille(nouvelle_lig, nouvelle_col, grille), # Bordure 边界检测
                case_cible == '1',                                   # Collision roche 岩石碰撞检测
                monster_blockage(monster_lst, nouvelle_lig,nouvelle_col) # 怪兽阻挡检测
            ]):
                continue
            # 3) Creuser la terre 添加挖掘 terre（进入 terre 时把它变成 tunnel）
            if case_cible == '2':
                grille[nouvelle_lig][nouvelle_col] = '0'

            # 判断当前是否在水中，并消耗氧气行走change4.1
            if case_cible == '3':
                if state['air'] > 0:
                    state['air'] -= 1
                else:
                    # 氧气不足就死了
                    print("You are drowned!")
                    joue = False
                    continue


            # 4) Pousser diamant 先移动钻石，再移动 Bob
            # diamant = [lig, col, image]
            if nouvelle_lig == diamant[0] and nouvelle_col == diamant[1]:
                # Position de la case où le diamant doit aller
                dia_nouvelle_lig = diamant[0] + mv_lig
                dia_nouvelle_col = diamant[1] + mv_col
                # a) Le diamant ne peut aller que dans un tunnel  change-4.1 change-5.1
                if any([
                    grille[dia_nouvelle_lig][dia_nouvelle_col] =='1', # 钻石不可越过岩石
                    grille[dia_nouvelle_lig][dia_nouvelle_col] =='2', # 钻石不可越过土
                    monster_blockage(monster_lst, dia_nouvelle_lig, dia_nouvelle_col) # 钻石不可越过怪物
                ]):
                    continue

                # b) Déplacement accepté → pousser le diamant
                diamant[0] = dia_nouvelle_lig
                diamant[1] = dia_nouvelle_col

            # 5) Mouvement Bob 先移动钻石，再移动 Bob
            bob[0] = nouvelle_lig
            bob[1] = nouvelle_col

            # Aquire bomb and oxygen，获取到道具后从集合中剔除 change-2.4
            bob_loc = (nouvelle_lig,nouvelle_col)
            if bob_loc in bomb_loc:
                bomb_loc.discard(bob_loc)
                state['bomb'] += 1
            if bob_loc in oxygen_loc:
                oxygen_loc.discard(bob_loc)
                state['air'] += 3
            
            # 按下B键后部署炸弹
            if evt.key == pygame.K_b and state['bomb'] > 0: # change-3.1
                bomb_set_loc[(bob_loc[0],bob_loc[1])] = [0,0]
                state['bomb'] -= 1
            
        
        
        # Evènement souris : bouton enfoncé.
        if evt.type == pygame.MOUSEBUTTONDOWN:

            # Clic gauche.
            if evt.button == 1:
                pos_pixel = pygame.mouse.get_pos()  # Récupère la position de la souris.
                case = position(pos_pixel)          # Transforme la position en case.
                # print("Case", case) # change-3.2
                # 判断当前被点击的单元格里是否有炸弹，有则点燃它
                if case in bomb_set_loc:
                    bomb_set_loc[case][0] = 1 # ignight bomb
                    pause_until = pygame.time.get_ticks() + WAIT['bomb_ignite']   # 暂停 2000 毫秒 = 2 秒
                    bomb_set_loc[case][1] = pause_until # 设置炸弹引爆时间
                    
    current_time = pygame.time.get_ticks()
    # 检查布置的炸弹状态并更新 change-3.2
    joue = checkBomb(grille, bob, bomb_set_loc ,monster_lst)
    
    # ----- Visualisation du jeu.
    visualise_jeu(grille, bob, diamant, exit, state, bomb_loc, oxygen_loc, bomb_set_loc,monster_lst,vue) # change-1 change-2.1 change-3.1
    

    # ----- Condition de victoire ----- 添加简单胜利条件
    if diamant[0] == exit[0] and diamant[1] == exit[1]: ## !!!!change-1
        print("Bravo ! Vous avez gagné !")
        joue = False
    if state['health'] <=0:
        print("Bob is dead!")
        joue = False
    pygame.display.flip()


    # ----- Nombre maximal d'exécution de la boucle par seconde (FPS).
    heure.tick(25)

# ----- Au revoir !
pygame.quit()
sys.exit()

