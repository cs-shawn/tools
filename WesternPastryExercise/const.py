import sys
import os


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


config_path = 'config'
right_path = resource_path(os.path.join('data', 'r.png'))
wrong_path = resource_path(os.path.join('data', 'e.png'))

btn_str_list = ("随机练习", "顺序练习", "模拟考试", "错题练习")
answer_choose_dict = {0: "A", 1: "B", 2: "C", 3: "D"}
answer_judge_dict = {0: "正确", 1: "错误"}
