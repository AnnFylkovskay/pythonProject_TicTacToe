import pygame as pg, sys
from pygame.locals import *
import time, random, copy, csv

# Введение глобальных переменных
XO = None  # -1 это игрок X, 1 это игрок O
move = None # числа от 0 до 8

    # TicTacToe поле 3x3
TTT= [0,0,0,0,0,0,0,0,0]
    # Игровое поле разделено на 9 ячеек с определением каждой слева направо в верхнем, среднем и нижнем ряду:
    # 0,1,2 - верхний ряд
    # 3,4,5 - средний ряд
    # 6,7,8 - нижний ряд
    # всего = поле 3x3  = 9 чисел (от 0 до 8 с учетом того, что список [TTT] начинается с 0 позиции)

game_save=[]
    # все этапы в одной игре - для сохранения в файл (в будущем это будет использоваться в машинном обучении)
    # формула та же TTT, но с 9 позицией на текущем этапе плюс 2 дополнительных места (пример: [-1,1,-1,0,1,0,0,0,0,-6,7]
    # [9]=[следующий ход X- или O-игрока. "-" - это X-ход, "+" - O-ход], (в примере: game_save[9]=-6 означает, что именно X-игрок переходит на 6-ю ячейку)
    # [10]=[количество этапов в одной игре], (в примере: game_save[10]=7)

# ценные данные для функции машинного обучения
stage=[] # список со всеми номерами этапов в базе данных, для которых установлено текущее поле (TTT[])
move_stage=[] # список с "следующим ходом" в базе данных, который соответствует текущему полю (TTT[]) и этапу
moves=[]  # список с наилучшими вариантами ходов


winner = None
draw = False
width = 400
height = 400
white = (255, 255, 255)
RED = (255,182,193)
BLACK = (0, 0, 0)
line_color = (10, 10, 10)

# Параметры начального окна
pg.init()
fps = 30
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((width, height + 100), 0, 32)
pg.display.set_caption("Крестики-Нолики")

# Загрузка изображений
opening = pg.image.load('images/tic tac opening.png')
x_img = pg.image.load('images/x.png')
o_img = pg.image.load('images/o.png')

# Изменение размера изображений
x_img = pg.transform.scale(x_img, (80, 80))
o_img = pg.transform.scale(o_img, (80, 80))
opening = pg.transform.scale(opening, (width, height + 100))

def game_opening():
    screen.fill(white)
    screen.blit(opening, (0, 0))
    pg.display.update()
    time.sleep(1.5)
    screen.fill(white)

    # Рисование вертикальных линий
    pg.draw.line(screen, line_color, (width / 3, 0), (width / 3, height), 7)
    pg.draw.line(screen, line_color, (width / 3 * 2, 0), (width / 3 * 2, height), 7)
    # Рисование горизонтальных линий
    pg.draw.line(screen, line_color, (0, height / 3), (width, height / 3), 7)
    pg.draw.line(screen, line_color, (0, height / 3 * 2), (width, height / 3 * 2), 7)

    draw_status()
def draw_status(): # статус игры. Если победитель определен - вся игра переходит в файл с формулой, на экране обновляется надпись ниже
    global XO, draw, game_save, filename

    if winner is None and XO == -1:
        message = "Ходит X"
    if winner == -1:
        message = "X победил!"

    if winner is None and XO == 1:
        message = "Ходит 0"
    if winner == 1:
        message = "0 победил!"
    if draw:
        message = 'Ничья!'

    font = pg.font.Font(None, 30)
    text = font.render(message, 1, (255, 255, 255))

    # вывод полученного сообщения на доску
    screen.fill((0, 0, 0), (0, 400, 500, 100))
    text_rect = text.get_rect(center=(width / 2, 500 - 50))
    screen.blit(text, text_rect)
    pg.display.update()
    time.sleep(0.4)
def check_win(): # Отметка победителя и проведение соответсвующей линии
    global TTT, winner, draw

    # Проверка наличия выигрышных строк
    for row in range(0, 7, 3):  # перейти к пункту 3 в списке ТТТ
        if ((TTT[row] == TTT[row + 1] == TTT[row + 2]) and (TTT[row] != 0)):
            # этот ряд выиграл
            winner = TTT[row]
            pg.draw.line(screen, (250, 0, 0), (0, (row/3 + 1) * height / 3 - height / 6), \
                         (width, (row/3 + 1) * height / 3 - height / 6), 6)
            break

    # Проверка наличия выигрышных столбцов
    for col in range(0, 3, 1):  # перейти к пункту 1 в списке TTT
        if (TTT[col] == TTT[col + 3] == TTT[col + 6]) and (TTT[col] != 0):
            # этот столбец выиграл
            winner = TTT[col]
            # эта строка выиграла
            pg.draw.line(screen, (250, 0, 0), ((col + 1) * width / 3 - width / 6, 0), \
                         ((col + 1) * width / 3 - width / 6, height), 6)
            break

    # Проверка наличия диагональных победителей
    if (TTT[0] == TTT[4] == TTT[8]) and (TTT[0] != 0):
        # Игра выиграна по диагонали слева направо
        winner = TTT[0]
        pg.draw.line(screen, (250, 70, 70), (50, 50), (350, 350), 6)

    if (TTT[2] == TTT[4] == TTT[6]) and (TTT[2] != 0):
        # Игра выиграна по диагонали справа налево
        winner = TTT[2]
        pg.draw.line(screen, (250, 70, 70), (350, 50), (50, 350), 6)

    if TTT.count(0) == 0 and winner is None:  # все ячейки заполнены
        draw = True

    draw_status()

def DrawXO(): # фиксация X или O в зависимости от выбора ячейки при игре, а также смена игрока после окончания хода (XO => - XO)
    global TTT, XO, move
    TTT[move] = XO
    if move == 0:
        posx = 30
        posy = 30
    if move == 1:
        posx = width / 3 + 30
        posy = 30
    if move == 2:
        posx = width / 3 * 2 + 30
        posy = 30

    if move == 3:
        posx = 30
        posy = height / 3 + 30
    if move == 4:
        posx = width / 3 + 30
        posy = height / 3 + 30
    if move == 5:
        posx = width / 3 * 2 + 30
        posy = height / 3 + 30

    if move == 6:
        posx = 30
        posy = height / 3 * 2 + 30
    if move == 7:
        posx = width / 3 + 30
        posy = height / 3 * 2 + 30
    if move == 8:
        posx = width / 3 * 2 + 30
        posy = height / 3 * 2 + 30

    if XO == -1:
        screen.blit(x_img, (posx, posy))
    else:
        screen.blit(o_img, (posx, posy))
    XO = -1*XO
    pg.display.update()
    check_win()

def user_click():  # щелчок игрока
    global move
    move = None
    # Получение координат щелчка мыши
    x, y = pg.mouse.get_pos()
    # Получение x,y от щелчка мыши (ячейка 1-9)
    if (y < height / 3) and (x < width / 3):
        move = 0
    elif (y < height / 3) and (x < width / 3 * 2):
        move = 1
    elif (y < height / 3) and (x < width):
        move = 2

    elif (y < height / 3 * 2) and (x < width / 3):
        move = 3
    elif (y < height / 3 * 2) and (x < width / 3 * 2):
        move = 4
    elif (y < height / 3 * 2) and (x < width):
        move = 5

    elif (y < height) and (x < width / 3):
        move = 6
    elif (y < height) and (x < width / 3 * 2):
        move = 7
    elif (y < height) and (x < width):
        move = 8

def reset_game(): # Перезагрузка и начало новой игры
    global TTT, TTT2, winner, XO, draw
    time.sleep(1.5)
    XO = -1
    draw = False
    winner = None
    TTT= [0,0,0,0,0,0,0,0,0]
    game_opening()
    draw_status()


def for_file():  # сохраните все этапы одной игры в список game_save=[] с формулой
    global TTT, game_save, move
    if TTT2.count(0) <= 8:
        TTT2.append((move + 1) * XO)  # добавьте будущий ход на 9-ю позицию в старом поле TTT, и XO обозначит его знаком (+/-)
        # Итак, nums[9]=-5 - ход X, nums[9]=2 - ход O
        # Чтобы упростить проверку внутри файла базы данных, мы отображаем номер перемещения в базе данных
        # с 1-го (1...9), а не с 0-го, как в списке (0...8)
        TTT3 = copy.deepcopy(TTT2)  # чтобы избежать изменений внутри временного хранилища game_save при TTT2.pop()
        game_save.append(TTT3)  # добавить защищенный от любых изменений TTT3
        TTT2.pop()  # удалить номер последнего (перемещения) из списка рабочих полей

def game_save_length():  # количество этапов в одной выигранной игре (game_save[...,9-следующий ход, 10-количество ходов до победы]
    # Осознанный подсчет начинается со 2-го хода.
    # Следовательно, победа O всегда заканчивается нечетно (5, 7), а X - четно (4, 6, 8). Ничья имеет 9 в позиции nums[10].
    # Последнего (9-го) этапа каждой игры нет в game_save[], потому что он нам не нужен для сравнения.
    global game_save, XO
    for item in game_save:
        if draw is True:  # мы должны разделить X выигрышных и ничейных ситуаций. Давайте сыграем вничью - всего 9 ходов.
            item.append(9)  # или len(game_save)+1 = 9 (постоянно)
        else:
            item.append(len(game_save))  # на каждом этапе будет добавляться [10] позиция (4 ... 8)

def into_file():  # сохранение всех игр со всеми этапами в файле с формулой (но без дубликатов!)
    global game_save
    game_save_length()  # создаем финальную версию game_save[]
    # Мы должны разделять, используя один и тот же файл, только шаг за шагом

    filename = "data.csv"
    with open(filename, "r") as file:  # только для открытия и чтения
        reader = csv.reader(file)
        for row_file in reader:  # читаю все строчки по отдельности
            nums = list(map(int, row_file))  # одна строка записывается в переменную nums
            for item in game_save:  # выполните итерацию по всем вложенным спискам
                if item == nums:
                    game_save.remove(item)  # нам нужны только уникальные списки = строки в файле базы данных
    file.close()  # подготовка к переходу к следующему шагу

    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        for item in game_save:
            writer.writerow(item)  # сохранять в БД только уникальные списки (строки)
    file.close()
    game_save.clear()  # очистка списка после сохранения в файле

def from_file():  # получение "наилучшего следующего хода" из базы данных (2-й шаг в АЛГОРИТМЕ машинного обучения)
    global TTT, move, XO
    filename = "data.csv"  # основной файл базы данных
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row_file in reader:
            nums = list(map(int, row_file))  # одна строка - это один список с описанием этапа одной игры
            if nums[:9] == TTT and nums[10] != 9:  # если текущее поле (TTT[]) равно такому же в базе данных (nums[:9])
                stage.append(nums[10])  # список со всеми номерами этапов в базе данных, для которых установлено текущее поле (TTT[])
                move_stage.append(abs(nums[9]))  # список с "следующим ходом" в базе данных, который установлен (TTT[]), и этап
                # Позиция ценностей в обоих списках одинакова. Например, stage[2] соответствует move_stage[2]

        if len(stage) == 0:  # если списки X и O пусты (потому что "ничья"), списки заполняются из nums[10]==9
            for row_file in reader:
                nums = list(map(int, row_file))
                if nums[:9] == TTT and nums[10] == 9:
                    stage.append(nums[10])
                    move_stage.append(abs(nums[9]))

        for q in range(0, len(stage), 1):
            if stage[q] == min(stage):  # найдите минимальное значение stage [q], потому что оно дает наилучший "следующий ход".
                moves.append(move_stage[q])  # лучший "следующий ход" заполняет moves[] с помощью move_stage[q] (это подходит)

        if len(moves) == 0:  # если пусто (не нашел лучшего хода)
            move = None  # путь для случайной ячейки в поле
        elif len(moves) == 1:
            move = moves[0] - 1
        else:  # если есть несколько лучших "следующих ходов", то машина выбирает один из них случайным образом
            while True:
                move = moves[random.randint(0, len(moves) - 1)] - 1
                if TTT[move] == 0:
                    break
        stage.clear()
        move_stage.clear()
        moves.clear()
def check_moves(): # Поиск наилучшего хода компьютера
    global TTT, move
    mov_map = [0, 0, 0, 0, 0, 0, 0, 0, 0] #  поле ходов перед ходом каждого компьютера в текущей ситуации
    move = None
    # Проверка наличия выигрышных строк
    # Вычислить сумму модулей текущего значения и выигрышной ячейки проверяемого игрока, а затем умножить их на знак проверяемого игрока
    # В большинстве случаев: ноль + 1 или -1 (текущий игрок), но если в ячейке одновременно два или три победителя, модуль значения должен быть равен 2 или 3 (-2 или -3)
    for row in range(0, 7, 3):  # перейти к пункту 1 в списке TTT
        r=TTT[row] + TTT[row + 1] + TTT[row + 2]
        if abs(r) == 2:
            if TTT[row] == 0:
                mov = row
                mov_map[mov] = (abs(mov_map[mov])+abs(int((r) / 2)))*int((r) / 2) # модуль суммы выигрыша обоих игроков и кратный на знаке текущего игрока
            elif TTT[row + 1] == 0:
                mov = row + 1
                mov_map[mov] = (abs(mov_map[mov])+abs(int((r) / 2)))*int((r) / 2)
            elif TTT[row + 2] == 0:
                mov = row + 2
                mov_map[mov] = (abs(mov_map[mov])+abs(int((r) / 2)))*int((r) / 2)

    # Проверка наличия выигрышных столбцов
    for col in range(0, 3, 1):  # перейти к пункту 1 в списке TTT
        c=TTT[col] + TTT[col + 3] + TTT[col + 6]
        if abs(c) == 2:
            if TTT[col] == 0:
                mov = col
                mov_map[mov] = (abs(mov_map[mov])+abs(int((c) / 2)))*int((c) / 2)
            elif TTT[col + 3] == 0:
                mov = col + 3
                mov_map[mov] = (abs(mov_map[mov])+abs(int((c) / 2)))*int((c) / 2)
            elif TTT[col + 6] == 0:
                mov = col + 6
                mov_map[mov] = (abs(mov_map[mov]) + abs(int((c) / 2))) * int((c) / 2)

    # Проверка наличия диагональных победителей слева направо
    d_Lr=TTT[0] + TTT[4] + TTT[8]
    if abs(d_Lr) == 2:
        if TTT[0] == 0:
            mov = 0
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Lr) / 2)))*int((d_Lr) / 2)
        elif TTT[4] == 0:
            mov = 4
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Lr) / 2)))*int((d_Lr) / 2)
        elif TTT[8] == 0:
            mov = 8
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Lr) / 2)))*int((d_Lr) / 2)

        # Проверка наличия диагональных победителей справа налево
    d_Rl=TTT[2] + TTT[4] + TTT[6]
    if abs(d_Rl) == 2:
        if TTT[2] == 0:
            mov = 2
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Rl) / 2)))*int((d_Rl) / 2)
        elif TTT[4] == 0:
            mov = 4
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Rl) / 2)))*int((d_Rl) / 2)
        elif TTT[6] == 0:
            mov = 6
            mov_map[mov] = (abs(mov_map[mov])+abs(int((d_Rl) / 2)))*int((d_Rl) / 2)

# Если один победитель в одной ячейке
    if mov_map.count(XO) > 0 and mov_map.count(-1*XO) == 0: #текущий игрок должен выбрать свою собственную клетку, если у противника нет выигрышной клетки
        move = mov_map.index(XO)
    if mov_map.count(-1*XO) > 0 and mov_map.count(XO) == 0: #текущий игрок должен выбрать клетку противника, если в ней нет его собственной выигрышной ячейки
        move = mov_map.index(-1*XO)
    if mov_map.count(XO) > 0 and mov_map.count(-1*XO) > 0: #текущий игрок должен выбрать свою собственную клетку, если у противника также есть выигрышная клетка
        move = mov_map.index(XO)

# Если два победителя или удвоенный один находятся в одной ячейке - предпочтение всегда отдается текущему игроку
    if mov_map.count(2) > 0:
        move = mov_map.index(2)
    if mov_map.count(-2) > 0:
        move = mov_map.index(-2)
def X_player(): # Х - игрок
    global TTT, TTT2, XO, move, winner, draw

    while (True):  # Запуск игрового цикла
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()

            if XO == -1: #  ход игрока X
                if event.type == MOUSEBUTTONDOWN:
                    user_click()  # нажать кнопку мыши для перемещения Х
                    if move == None:
                        continue
                    else:
                        if (TTT[move] == 0):
                            TTT2 = copy.deepcopy(TTT)  # сохранение последнего поля списка ТТТ
                            DrawXO()
            if XO == 1 and draw is False and winner is None: # Движение игрока 0
                TTT2 = copy.deepcopy(TTT)  # сохранение последнего поля списка ТТТ
                check_moves()  # Проверка наличия XX, X_X, OO, O_O
                from_file()  # загрузка из базы данных ("data.csv")
                if move is None:
                    while True:
                        if TTT[4] == 0:  # Защита от дурака (когда соперник образует типичный треугольник "X")
                            move = 4
                            break
                        else:  # Ход на удачу, дающий шанс играть честно, без алгоритма
                            move = random.randint(0, 8)
                            if TTT[move] == 0:
                                break
                DrawXO()

        if (winner or draw):
            reset_game()
        pg.display.update()
        CLOCK.tick(fps)
def O_player(): # O - игрок
    global TTT, TTT2, XO, move, winner, draw

    while (True):  # Запуск игрового цикла
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()

            if XO == -1:
                TTT2 = copy.deepcopy(TTT)  # сохранить последнее поле TTT
                check_moves()  # Проверка наличия XX, X_X, OO, O_O
                from_file()  # загрузка из базы данных ("data.csv")
                if move is None:
                    while True:
                        move = random.randint(0, 8)
                        if TTT[move] == 0:
                            break
                DrawXO()
            if XO == 1 and draw is False and winner is None:
                if event.type == MOUSEBUTTONDOWN:
                    user_click()  # Нажать кнопку мыши для одного перемещения X и O-ответ
                    if move == None:
                        continue
                    else:
                        if (TTT[move] == 0):
                            TTT2 = copy.deepcopy(TTT) # сохраните последнее поле TTT
                            DrawXO()
        if (winner or draw):
            reset_game()
        pg.display.update()
        CLOCK.tick(fps)
def menu_XO(): # Изображение для выбора X или O
    screen.fill(white)
    # Рисование вертикальных линий
    pg.draw.line(screen, RED, (width / 3, height/3), (width / 3, height/3*2), 4)
    pg.draw.line(screen, RED, (width / 3 * 2, height/3), (width / 3 * 2, height/3*2), 4)
    pg.draw.line(screen, RED, (1, height / 3), (1, height / 3 * 2), 4)
    pg.draw.line(screen, RED, (width-3, height / 3), (width-3, height / 3 * 2), 4)
    # Рисование горизонтальных линий
    pg.draw.line(screen, RED, (0, height / 3), (width/3+2, height / 3), 4)
    pg.draw.line(screen, RED, (0, height / 3 * 2), (width/3+2, height / 3 * 2), 4)
    pg.draw.line(screen, RED, (width / 3*2, height / 3), (width, height / 3), 4)
    pg.draw.line(screen, RED, (width / 3*2, height / 3 * 2), (width, height / 3 * 2), 4)
    screen.blit(x_img, (30, 160))
    screen.blit(o_img, (290, 160))
    font = pg.font.Font(None, 80)
    text = font.render("X или O ?", 1, (255, 255, 255))
    # Вывод сообщения на форму
    screen.fill((RED), (0, 400, 500, 100))
    text_rect = text.get_rect(center=(width / 2, 500 - 50))
    screen.blit(text, text_rect)
    pg.display.update()
def menu_click(): # выбор игрока X или O
    global XO
    XO = None
    # Получение координат щелчка мыши
    x, y = pg.mouse.get_pos()
    # Получение x,y от щелчка мыши (ячейка X или O)
    if (y < height / 3 * 2) and (y > height / 3 * 1) and (x < width / 3) and (x > 0):
        XO = -1
    elif (y < height / 3 * 2) and (y > height / 3 * 1) and (x < width) and (x > width / 3 * 2):
        XO = 1

while XO is None:  # Запуск меню
    for event in pg.event.get():
        menu_XO()
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            menu_click()  # нажатие на кнопку мыши для выбора очереди Х или 0
            if XO == None:
                continue
            else:
                if XO != None:
                    if XO == -1:
                        message = "X - игрок"
                    if XO == 1:
                        message = "O - игрок"

                    font = pg.font.Font(None, 60)
                    text = font.render(message, 1, (255, 255, 255))

                    # Вывод сообщения на форму
                    screen.fill((BLACK), (0, 400, 500, 100))
                    text_rect = text.get_rect(center=(width / 2, 500 - 50))
                    screen.blit(text, text_rect)
                    pg.display.update()
                    time.sleep(1.5)
                    break

game_opening()

if XO==-1:
    X_player() # X - игрок
elif XO==1:
    XO=-1 # Изменение знака. Сначала Х.
    O_player() # O - игрок