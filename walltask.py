#!/usr/bin/python3
import ctypes
import os, sys
from shutil import copyfile
from PIL import Image, ImageFont, ImageDraw
import argparse
import json

# User has to store original wallpaper in folder 'wallpaper' with the filename 'wall.jpg'
org_wall = 'wallpaper/wall.jpg'
# Tasks will be drawn onto this file (will first be created as a copy of org_wall when tasks are added)
new_wall = 'wallpaper/task_wall.jpg'

try:
    rf = open('data.json', 'r')
# Initial usage of the script will create a json file with all the default settings and a list to store tasks
except FileNotFoundError:
    temp_wf = open('data.json', 'w')
    init_data = {'tasks': [], 'xpos': 600, 'colour': 'white', 'fontsize': 30}
    json.dump(init_data, temp_wf, indent=4)
    temp_wf.close()
    rf = open('data.json', 'r')

# Is used throughout this program to access the tasks, settings in json file and update them
data = json.load(rf)

def create_wallpaper():
    ''' Create a new wallpaper by accessing tasks list in data dict loaded from json file. Is called when tasks are added or removed from json file'''

    # Open org_wall. Tasks will be drawn on contents of this image and will be saved to new_wall without affecting org_wall
    wall = Image.open(org_wall)
    draw = ImageDraw.Draw(wall)
    fontsize = int(data['fontsize'])
    font = ImageFont.truetype('arial.ttf', fontsize)
    ypos = 50
    xpos = data['xpos']

    # Loop over each item in tasks list saved in json data file. The tasks are then drawn on wallpaper.
    for task in data['tasks']:
        try:
            draw.text((xpos, ypos), '{}. {}'.format(task['id'], task['t']), data['colour'], font=font)
        except ValueError:
            print('The colour or the font you set did not exist')
        # ypos is updated by the font size to ensure that two tasks don't draw over each other on the wallpaper.
        ypos += fontsize

    with open('data.json', 'w') as wf:
        json.dump(data, wf, indent=4)
    # Save changed image to new_wall, leaving the org_wall unaffected
    wall.save(new_wall)

def update_wallpaper(file):
    '''Sets a new desktop background'''
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, file, 0)

def add(added_tasks):
    ''' Adds tasks to data dict. added_tasks is a list from taking in arguments in the commandline from user.'''

    # Following is to get max no of tasks in data so as to assign id to a task by continuing after the largest id.
    tasks_len = len(data['tasks'])

    for i in range(len(added_tasks)):
        # Number each task by adding tasks_len to i, so the id keeps increasing.
        cur_id = tasks_len + i
        data['tasks'].append({'t': '{}'.format(added_tasks[i]), 'id': cur_id})
    # Return updated data dict which will be saved to data.json in main() and then new wallpaper is created with new data
    return data

def remove(ids):
    # Reverse sorted ids list since am removing from data['tasks] by index. If args were not reversed; ex:[2,5], After removing 2 first would result in
    # abrupt IndexError since index 5 would no longer exist
    try:
        for i in sorted(ids, reverse=True):
            del data['tasks'][i]
        # Re-assign the ids to tasks as there will be gaps after removing.
        for i, task_dict in enumerate(data['tasks']):
            task_dict['id'] = i
    # If user provides an index that has not been assigned to a task.
    except IndexError:
        print("There does not exist a task with atleast one of the indexes you provided")

def clear_tasks():
    ''' Clears all tasks from data.json and subsequently the wallpaper'''
    # Empty the tasks list
    data['tasks'] = []

    # Dump the updated data dict to the same file from where it was retrieved
    with open('data.json', 'w') as wf:
        json.dump(data, wf, indent=4)
        wf.close()
    try:
        # Remove new_wall and change wallpaper to original
        os.remove(new_wall)
        update_wallpaper(os.path.join(os.getcwd(), org_wall))
    # If file 'new_wall' is not found, the user has already cleared tasks by removing new_wall
    except FileNotFoundError:
        print('You have already cleared all your tasks.')

def main():
    parser = argparse.ArgumentParser(description='Add or remove tasks to your wallpaper')
    parser.add_argument('-a', '--add', nargs='*', help='Add tasks to wallpaper')
    parser.add_argument('-c', '--clear', help='Clear all of your tasks', action='store_true')
    parser.add_argument('-r', '--remove', nargs='*', type=int, help='Remove a task by id')
    parser.add_argument('-m', '--margin', nargs=1, type=int, help='Change left margin')
    parser.add_argument('-cl', '--colour', nargs=1, help='Change colour of the tasks')
    parser.add_argument('-fs', '--fontsize', nargs=1, help='Change font of the tasks')
    args = parser.parse_args()

    # Following arguments will always require 3 or more arguments to make a change
    if len(sys.argv) > 2:
        # Stores returned data after it has been changed in a function. Is then dumped to json data.
        updated_data = {}
        if args.add:
            updated_data = add(args.add)
        if args.remove:
            updated_data = remove(args.remove)
        if args.margin:
            data['xpos'] = args.margin
        if args.colour:
            data['colour'] = args.colour
        if args.fontsize:
            data['font'] = args.font

        with open('data.json', 'w') as wf:
            json.dump(updated_data, wf, indent=4)
            wf.close()

        create_wallpaper()
        update_wallpaper(os.path.join(os.getcwd(), new_wall))

    if args.clear:
        clear_tasks()

if __name__ == '__main__':
    main()
