# -*- coding: utf-8 -*-
"""
-
Author:
Date:
"""

import os
import re
from datetime import datetime
import schedule
import time


def exception_handler(func):
    """抛出异常"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("Exception caught: {}".format(e))

    return wrapper


def list_files(start_dir):
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            yield os.path.join(root, file)


# 逐行读取文件
def read_large_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()  # strip()用于去除行尾的换行符


def find_hex_values(text):
    """
    查找并返回给定文本中所有的十六进制值。
    参数:
    text (str): 要搜索的文本。
    返回:
    list: 所有找到的十六进制值的列表。
    """
    pattern = r'0x[0-9a-fA-F]+'
    matches = re.findall(pattern, text)
    return matches


def find_values_by_pattern(text, pattern):
    """
    根据给定的正则表达式模式查找并返回给定文本中所有匹配的值。
    参数:
    text (str): 要搜索的文本。
    pattern (str): 用于匹配的正则表达式。
    返回:
    list: 所有找到的匹配值的列表。
    """
    matches = re.findall(pattern, text)
    return matches


# 筛选连接成功的信息
def record_reconnect_success_data(data: dict, line: str, forwarding_server_ip: list) -> dict:
    pattern_0x = r'0x[0-9a-fA-F]+'
    matche = find_values_by_pattern(line, pattern_0x)[0]
    if matche not in data.keys():
        # forwarding_server_ip_dict:dict ={key:0 for key in forwarding_server_ip}
        # data[matche] = {"P2P": 0,
        #                 "RLY": forwarding_server_ip_dict}
        data[matche] = {"P2P": 0,
                        "RLY": {"服务器转发": 0,
                                "设备转发": 0,
                                "总次数": 0
                                }}
    if "P2P" in line:
        data[matche]["P2P"] += 1
    elif "RLY" in line:
        data[matche]["RLY"]["总次数"] += 1
        flag = True
        for ip in forwarding_server_ip:
            if ip in line:
                data[matche]["RLY"]["服务器转发"] += 1
                flag = False
        if flag:
            data[matche]["RLY"]["设备转发"] += 1
    else:
        print("未检测到连接方式")

    return data


# 筛选连接失败的信息
def record_reconnect_faile_data(data: dict, line: str) -> dict:
    pattern_ret = r'ret=\-?\d+'
    pattern_0x = r'0x[0-9a-fA-F]+'
    matche_0x = find_values_by_pattern(line, pattern_0x)[0]
    matche_ret = find_values_by_pattern(line, pattern_ret)[0]
    if matche_ret not in data.keys():
        data[matche_ret] = {}
    if matche_0x not in data[matche_ret].keys():
        data[matche_ret][matche_0x] = 1
    else:
        data[matche_ret][matche_0x] += 1
    return data


def current_time_as_list():
    """
    获取当前时间，并以列表形式返回。
    返回:
    list: 包含年、月、日、时、分、秒的列表。
    """
    # 前一分钟的时间戳
    timestamp = int(time.time()) - 60
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp)
    # 将datetime对象转换为列表
    time_list = [dt_object.year, dt_object.month, dt_object.day,
                 dt_object.hour, dt_object.minute, dt_object.second]
    return time_list


# 生成文件路径
def format_date_from_list(date_list):
    # 从列表中获取年月日
    year, month, day, hour, minute = date_list[:5]
    # 日期格式 'YYYYMMDD'
    formatted_date = "{:04d}{:02d}{:02d}".format(year, month, day)
    # 时间格式 'HH','mm'
    formatted_hour = "{:02d}".format(hour)
    formatted_minute = "{:02d}".format(minute)
    dir_path = '{}/{}/{}.txt'.format(formatted_date, formatted_hour, formatted_minute)
    return dir_path


if __name__ == '__main__':
    # @exception_handler
    def job():
        # 使用函数获取当前时间,并生成文件相对路径
        current_time = current_time_as_list()
        file_path = format_date_from_list(current_time)
        print(file_path)

        # base目录，合并生成绝对路径
        base_path = r'/root/EasyDebug/PPC_Log/'
        temp_file_path = ''
        # print(temp_file_path)
        flag_enter = False
        if os.name == 'posix' and not flag_enter:
            # print("当前系统是类Unix系统，包括Linux和Mac OS")
            temp_file_path = input("请输入文件的绝对路径(回车则自动运行)：")
            flag_enter = True
            if len(temp_file_path) < 5:
                temp_file_path = base_path + file_path
        elif os.name == 'nt':
            # print("当前系统是Windows")
            temp_file_path = r'F:\easydebug测试文件\test\06.txt'
        else:
            print("当前系统未知")

        # 成功次数和失败次数
        all_count = 0
        success_num = 0
        faile_num = 0
        p2p_count = 0
        rly_count = 0
        p2p_connection_count = 0
        forward_count = 0
        success_data = {}
        faile_data = {}
        forwarding_server_ip = ['124.70.48.140',
                                '116.205.246.62',
                                '124.71.28.144',
                                '110.41.148.162',
                                '139.159.162.81',
                                '139.9.42.68',
                                '129.150.62.146.',
                                '158.178.226.162',
                                '122.8.149.214',
                                '158.101.162.182',
                                '172.234.26.124',
                                '159.138.140.4',
                                '49.0.251.50']

        # 筛选出符合条件的数据
        for line in read_large_file(temp_file_path):
            if 'Connect' in line and '0x27' not in line:
                if 'failed' in line:
                    faile_data = record_reconnect_faile_data(faile_data, line)
                    faile_num += 1
                elif 'P2P' in line or "RLY" in line:
                    if "P2P" in line:
                        p2p_count += 1
                    elif "RLY" in line:
                        rly_count += 1
                    success_data = record_reconnect_success_data(success_data, line, forwarding_server_ip)
                    success_num += 1

        # 筛选-6的0x00、0x01参数 和 0x27
        count_ret = 0
        # print(faile_data)
        for ret, hex_frequency_map in faile_data.items():
            for hex, num in hex_frequency_map.items():
                if ret == 'ret=-6' and (hex == '0x01' or hex == '0x00'):
                    count_ret += faile_data[ret][hex]
                elif hex == '0x27':
                    count_ret += faile_data[ret][hex]

        # 实际连接失败次数
        actual_failure_count = faile_num - count_ret

        # 失败百分比
        failure_percentage = faile_num / (success_num + faile_num)

        # 实际失败百分比（剔除了-6的0x00、0x01参数 和 0x27）
        actual_failure_percentage = actual_failure_count / (success_num + actual_failure_count)

        # 总连接次数
        all_count = actual_failure_count + success_num

        print("当前解析文件：{}".format(temp_file_path))
        print("总连接次数：{},成功次数：{}, 失败次数:{}(失败百分比：{:.0%}) "
              "\n实际成功次数：{}, 实际失败次数:{}(实际失败百分比:{:.0%})"
              "\nP2P连接总数：{},RLY连接总数：{}"
              .format(all_count, success_num, faile_num, failure_percentage, success_num, actual_failure_count
                      , actual_failure_percentage, p2p_count, rly_count))
        print("连接成功")
        print(success_data)
        print("连接失败")
        print(faile_data)
        print("*" * 100)


    # 使用cron风格的时间设置，每30分钟执行一次，* 表示任意值，因此"*/30"表示每30分钟
    job()
    schedule.every(1).minutes.do(job)
    print("Task scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(1)
