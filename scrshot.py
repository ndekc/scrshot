# import tkinter as tk
import sys
import os
import cv2
import re

import configparser
import json

from adb.client import Client as AdbClient

class CompareImage:

    def __init__(self, image_1_path, image_2_path):
        self.minimum_commutative_image_diff = 1
        self.image_1_path = image_1_path
        self.image_2_path = image_2_path

    def compare_images(self):
        image_1 = cv2.imread(self.image_1_path, 0)
        image_2 = cv2.imread(self.image_2_path, 0)
        commutative_image_diff = self.get_image_difference(image_1, image_2)

        if commutative_image_diff < self.minimum_commutative_image_diff:
            # print("Matched")
            return commutative_image_diff
        return 10000 #random failure value

    @staticmethod
    def get_image_difference(image_1, image_2):
        first_image_hist = cv2.calcHist([image_1], [0], None, [256], [0, 256])
        second_image_hist = cv2.calcHist([image_2], [0], None, [256], [0, 256])

        img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_BHATTACHARYYA)
        img_template_probability_match = cv2.matchTemplate(first_image_hist, second_image_hist, cv2.TM_CCOEFF_NORMED)[0][0]
        img_template_diff = 1 - img_template_probability_match

        # taking only 10% of histogram diff, since it's less accurate than template method
        commutative_image_diff = (img_hist_diff / 10) + img_template_diff
        return commutative_image_diff

config = None

config = configparser.ConfigParser()
with open('config.json', 'r') as f:
    config = json.load(f)


client = AdbClient(host=config['adb']['host'], port=config['adb']['port'])
device = client.devices()[0]

def get_last_directory_index():
    regexp = re.compile(config['directory_settings']['prefix']+r'\d+')

    for objects in os.walk(config["directory_settings"]["base_directory"]):
        dirs = objects[1]
        directories = list(filter(regexp.match, dirs))
        index = 0
        if (len(directories)) > 0:
            index = max(list(map(int, [re.sub(r'\D+', '', d) for d in directories])))

        return index

directory = f'{config["directory_settings"]["base_directory"]}'\
    + f'\\{config["directory_settings"]["prefix"]}'\
    + str(get_last_directory_index()+1) + '\\'

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
    return f"{directory}{config['file_name']['prefix']}"\
    + f"_{image_index}{config['file_name']['extention']}"

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
    c = input('Delete last screenshot and finish? (n/Y)')
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
