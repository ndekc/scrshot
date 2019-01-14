from adb.client import Client as AdbClient
from compare_images import CompareImage
import os

client = AdbClient(host="127.0.0.1", port=5037)
device = client.devices()[0]

# -------
# Номер директорії скріншотів
directory_index = 0

# Початок назви директорії скріншотів
directory_prefix = 'viber'

# Номер першого скріншота.
image_index = 0

# Напрямок свайпу 
# Cвайп звичайно виконується вгору.
# Для виконнання свайпу вниз змінити на 'будь що', чи 'down'
swipe_direction = ''

# частина назви файлів скріншотів
name = 'scr'

# розширення назви файлів скріншотів
ext = '.png'

# директорія, в яку потраплятимуть скріншоти
directory =f'scr\\{directory_prefix}{directory_index}\\'


# Виконує знімок екрану
def make_screenshot(name):

    curr_dir = os.path.dirname(os.path.abspath(name))
    if not os.path.exists(curr_dir):
        os.mkdir(curr_dir)

    result = device.screencap()
    with open(name, "wb") as fp:
        fp.write(result)

# Виконує свайп
def swipe(direction='up'):
    x = '460'
    y1, y2='300', '1120'
    speed_factor = '1000'
    
    if (direction!='up'):
        y1, y2 = y2, y1

    swipe_command = f'input swipe {x} {y1} {x} {y2} {speed_factor}'
    device.shell(swipe_command)

# Формує ім'я файлу скріншоту
def generate_scr_name(image_index):
    return f'{directory}{name}_{image_index}{ext}'

''' 
Виконує знімок екрану та свайп в заданому напрямку.
Порівнює зображення, пропонує видалити схожі.
Для підтвердження видалення ввести 'y' (за замовченням, тому просто можна  натистути 'enter').
Для відміни видалення останнього зобоаження ввести 'n'.
'''
def create_screenshots(start_index=0):
    i=start_index
    
    flag = True
    while flag:
        curr_name = generate_scr_name(i)
        make_screenshot(curr_name)
        print(curr_name)
        
        swipe(direction=swipe_direction)
        if i>0:
            prev_name = generate_scr_name(i-1)
            comparator = CompareImage(prev_name, curr_name)
            difference = comparator.compare_images()
            print(difference)
            if difference < 0.002:
                print(f'{curr_name} ~ {prev_name} -> {difference}')
                flag = False

                c = input('Delete and back? (n/Y)')
                if c.lower()!='n':
                    device.shell('input keyevent 4')
                    os.remove(curr_name)
        i+=1

# Недороблено
def get_last_directory(root_directory='./scr/'):
    pass
def show_menu():
    pass

# Головна функція
def main():
    create_screenshots(start_index=image_index)
    

# Точка входу
if __name__ == '__main__':
    main()
