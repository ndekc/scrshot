# import tkinter as tk
import sys
import os

import configparser
import json

from adb.client import Client as AdbClient
from compare_images import CompareImage


config = configparser.ConfigParser()
with open('config.json', 'r') as f:
    config = json.load(f)


client = AdbClient(host=config['adb']['host'], port=config['adb']['port'])
device = client.devices()[0]

directory = f'scr\\{config["directory_name"]["prefix"]}{config["directory_name"]["index"]}\\'


# Виконує знімок екрану
def make_screenshot(name):

    curr_dir = os.path.dirname(os.path.abspath(name))
    if not os.path.exists(curr_dir):
        os.mkdir(curr_dir)

    result = device.screencap()
    with open(name, "wb") as fp:
        fp.write(result)

    

# Виконує свайп
def swipe():
    x1 = config["swipe"]["point_start"]["x"]
    x2 = config["swipe"]["point_end"]["x"]

    y1 = config["swipe"]["point_start"]["y"]
    y2 = config["swipe"]["point_end"]["y"]

    speed_factor = config["swipe"]["speed_factor"]
    
    if (config["swipe"]["swap_x"]!='True'):
        x1, x2 = x2, x1

    if (config["swipe"]["swap_y"]!='True'):
        y1, y2 = y2, y1

    speed_factor = config["swipe"]["speed_factor"]

    swipe_command = f'input swipe {x1} {y1} {x2} {y2} {speed_factor}'
    device.shell(swipe_command)

# Формує ім'я файлу скріншоту
def generate_scr_name(image_index):
    return f"{directory}{config['file_name']['prefix']}_{image_index}{config['file_name']['extention']}"

''' 
Виконує знімок екрану та свайп в заданому напрямку.
Порівнює зображення, пропонує видалити схожі.
Для підтвердження видалення ввести 'y' (за замовченням, тому просто можна  натистути 'enter').
Для відміни видалення останнього зобоаження ввести 'n'.
'''
def create_screenshots(start_index):
    i=start_index

    flag = True
    while flag:
        curr_name = generate_scr_name(i)
        make_screenshot(curr_name)
        print(curr_name)
        
        swipe()
        if i>0:
            prev_name = generate_scr_name(i-1)
            comparator = CompareImage(prev_name, curr_name)
            difference = comparator.compare_images()
            print(difference)
            if difference < 0.002:
                print(f'{curr_name} ~ {prev_name} -> {difference}')
                if show_finish_promt():
                    if config["push_back_after_finish"] == 'True':
                        device.shell('input keyevent 4')
                    os.remove(curr_name)
                    flag = False

                elif not show_continue_promt():
                    flag = False
        i+=1
    

def show_finish_promt():
    c = input('Delete last screenshot, and finish? (n/Y)')
    return c.lower()!='n'

def show_continue_promt():
    c = input('Continue? (n/Y)')
    return c.lower()!='n'
    

# Головна функція
def main():
    create_screenshots(config['file_name']['index'])

# Точка входу
if __name__ == '__main__':
    main()
