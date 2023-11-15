
BD = None # вывод двоичного



def two():

 n = int(input('Введите число'))
 twon = " "

 while n > 0:
    remainder = n % 2
    twon = str(remainder) + twon
    n = n // 2
    print ('Двоичное число' + ' ' + str(twon))

 decimal = int(twon, 2)
 print ('Десятичное число' + ' ' + str(decimal))

def ten():
   m = int(input('Введите число'))
   tenm = " "
   decimal = int(m, 2)
   print ('Десятичное число' + ' ' + str(decimal))

   while m > 0:
    remainder = m % 2
    tenm = str(remainder) + twon
    m = m // 2
    print('Двоичное число' + ' ' + str(tenm))

def draw_status():

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

