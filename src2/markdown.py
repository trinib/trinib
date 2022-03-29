from collections import defaultdict
from urllib.parse import urlencode
import os
import re
import ast

import yaml

with open('data2/settings.yaml', 'r') as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)


def create_link(text, link):
    return " [" + str(text) + "](" + link + ") |"


def create_issue_link(source):
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['move'], safe="{}"))

    
    return create_link(source, issue_link.format(source=source))
    


def generate_top_moves():
    with open("data2/top_moves.txt", 'r') as file:
        contents = file.read()
        dictionary = ast.literal_eval(contents)

    markdown = "\n"
    markdown += "| Total moves |  User  |\n"
    markdown += "| :---------: | :----- |\n"

    counter = 0
    for key,val in sorted(dictionary.items(), key=lambda x: x[1], reverse=True):
        if counter >= settings['misc']['max_top_moves']:
            break

        counter += 1
        markdown += "| " + str(val) + " | " + create_link(key, "https://github.com/" + key[1:]) + " |\n"

    return markdown + "\n"


def generate_last_moves():
    markdown = "\n"
    markdown += "| Move | Author |\n"
    markdown += "| :--: | :----- |\n"

    counter = 0

    with open("data2/last_moves.txt", 'r') as file:
        for line in file.readlines():
            parts = line.rstrip().split(':')

            if not ":" in line:
                continue

            if counter >= settings['misc']['max_last_moves']:
                break

            counter += 1

            markdown += "| `" + parts[0] + "` | " + create_link(parts[1], "https://github.com/" + parts[1].lstrip()[1:]) + " |\n"

    return markdown + "\n"


def generate_moves_list(board):
    # return ''
    # Create dictionary and fill it
    # Write everything in Markdown format
    markdown = ""
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['new_game']))

    if board.is_game_over():
        return "**GAME IS OVER!** " + create_link("Click here", issue_link) + " to start a new game :D\n"
    else:
        return ''


def board_to_list(board):
    board_list = []

    for line in board.split('\n'):
        sublist = []
        for item in line.split(' '):
            sublist.append(item)

        board_list.append(sublist)

    return board_list


def get_image_link(piece):
    switcher = ['img/blank.png', 'img/red.png','img/yellow.png']

    return switcher[piece]


def board_to_markdown(board):
    grid = board.grid
    markdown = ""

    # Write header in Markdown format
    markdown += "|   | 1 | 2 | 3 | 4 | 5 | 6 | 7 |   |\n"
    markdown += "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    # Write board
    for row in reversed(grid):
        markdown += "|---|"
        for elem in row:
            markdown += "<img src=\"{}\" width=50px> | ".format(get_image_link(elem))

        markdown += "|---|\n"

    # Write footer in Markdown format
    moves = board.valid_moves()
    markdown += "|   |"
    for i in range(7):
        if (i+1) in moves:
            markdown += create_issue_link(i+1)
        else:
            markdown += f" {i+1} |"
    markdown += "   |\n"

    return markdown

if __name__ == '__main__':
    nums = range(9)
    for move in nums:
        print(create_issue_link(move))
