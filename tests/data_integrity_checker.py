# -*- coding: utf-8 -*-
"""
-
Author:
Date:
"""
import re
# from my_decorator import timer
from tqdm import tqdm
import bz2
import os
import schedule
import time


def decompress_bz2_file(input_path, output_path):
    """
    解压缩.bz2文件到指定的输出文件。
    :param input_path: .bz2文件的路径 (str)
    :param output_path: 输出文件的路径 (str)
    """
    with bz2.BZ2File(input_path, 'rb') as compressed_file:
        with open(output_path, 'wb') as decompressed_file:
            for data in iter(lambda: compressed_file.read(100 * 1024), b''):
                decompressed_file.write(data)


def extract_six_digit_numbers(filename, mark=None):
    # 定义正则表达式模式，查找任何位置上的连续6位数字
    pattern = re.compile(r'\d{6}' + mark)
    pattern1 = re.compile(r'\d{6}')
    # 打开文件并读取全部内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, content)

    # 打印所有匹配到的6位数字
    res_match = []
    for match in matches:
        match = re.findall(pattern1, match)
        res_match.append(match[0])
    return res_match


def extract_content_between_markers(file_path, start_marker, end_marker=None):
    """
    提取文件中位于指定起始标记和结束标记之间的内容。
    如果结束标记为 None，则返回起始标记后面的所有内容直至文件结尾。

    :param file_path: 文件路径 (str)
    :param start_marker: 起始标记 (str)
    :param end_marker: 结束标记 (str or None)
    :return: 包含所有匹配内容的列表 (list of str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if end_marker is not None:
                # 构建正则表达式，匹配起始和结束标记之间的内容
                pattern = re.escape(start_marker) + '(.*?)' + re.escape(end_marker)
                matches = re.findall(pattern, content, re.DOTALL)
            else:
                # 如果 end_marker 为 None，查找从 start_marker 到文件结尾的内容
                start_index = content.find(start_marker)
                if start_index == -1:
                    matches = []
                else:
                    matches = [content[start_index + len(start_marker):]]
            return matches
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
        return []
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return []


def process_data(content):
    """
    将给定的行数据列表转换为字典，其中每行的第一个字段作为键，
    该字段之后的所有数据（去除了前后空格和逗号）作为值列表。

    :param lines: 一个包含多行数据的列表，每行数据由空格分隔。
    :return: 转换后的字典，键为每行的第一个字段，值为该行其余字段组成的列表。
    """
    # with open(filename, 'r', encoding='utf-8') as file:
    #     content = file.read()

    # 使用splitlines()函数按行分割字符串
    lines_list = content.splitlines()
    # # 打印列表内容，查看结果
    # for line in lines_list:
    #     print(line)
    data_dict = {}
    for line in lines_list:
        # 分割行数据，去除键部分的冒号，并清理每个值元素
        parts = line.split(' ')
        key = parts[0].strip(':')
        values = [part.strip(',') for part in parts[1:] if part]

        # 将处理后的数据存入字典
        data_dict[key] = values
    return data_dict


def filter_online_devices(data_dict: dict):
    online_list = []
    for key, value in data_dict.items():
        if len(value) >= 3:
            online_list.append(key)
            continue
        elif len(value) == 0:
            continue
        # print(key, value)
        online_time = re.sub(r'\(.*?', '', value[0])
        if int(online_time) <= 3600:
            # print(key, value)
            online_list.append(key)
            continue
    return online_list


def find_files_with_extension(root_dir, concent):
    """
    遍历指定目录及其子目录，找出具有特定扩展名的文件。
    :param root_dir: 要遍历的根目录路径 (str)
    :param extension: 要查找的文件扩展名 (str)，例如 '.txt' 或 '.jpg'
    :return: 符合条件的文件的完整路径列表 (list of str)
    """
    matching_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if '.bz2' in filename and concent in filename:
                matching_files.append(os.path.join(dirpath, filename))
    return matching_files


if __name__ == '__main__':
    # 配置
    dids = ['IOTGAA', 'IOTGBB', 'IOTGCC', 'IOTGDD', 'IOTGEE', 'IOTGFF']  # 服务器支持的did列表
    file_dir = '/root/EasyDebug/bin/'  # 增量包所在目录
    dump_name = 'DID_Dump.log'  # 源文件名称
    file_path_dump = file_dir + dump_name  # 源文件路径
    old_flag_file = []


    def job():
        global old_flag_file
        online_dev = 0
        for i in range(len(dids)):
            did = dids[i]
            matching_files = find_files_with_extension(file_dir, did)
            if not matching_files:
                # 如果没有生成这轮最后一个增量包，则直接返回，等待下轮
                continue
            elif set(matching_files).issubset(set(old_flag_file)):
                # 如果已经生成这轮最后一个增量包，但是该轮已经执行了，
                # print(old_flag_file, '\n', matching_files)
                # print("如果已经生成这轮最后一个增量包，但是该轮已经执行了，直接返回")
                continue
            else:
                # 如果已经生成这轮最后一个增量包，但是该轮还没有执行，则添加该文件到old_flag_file，并执行该轮
                old_flag_file += matching_files
            # print(old_flag_file)
            input_path = matching_files[0]  # 增量包bz2路径
            output_path = file_dir + 'temp.txt'
            # 解压增量包
            decompress_bz2_file(input_path, output_path)
            start_marker = did
            if i == len(dids) - 1:
                end_marker = None
            else:
                end_marker = dids[i + 1]
            content_list = extract_content_between_markers(file_path_dump, start_marker, end_marker)
            content_str = ''
            for content in content_list:
                content_str = content_str.join(content)
            # 调用函数并打印结果
            processed_data = process_data(content_str)
            online_list = filter_online_devices(processed_data)
            # print(len(online_list))
            # print(online_list[:10])

            # 读取增量包

            matchs = extract_six_digit_numbers(output_path, mark='_')
            # print(matchs[:10])
            print(f"{input_path}增量包数量{len(matchs)},源文件在线设备数量{len(online_list)}")
            online_dev += len(online_list)
            for i in tqdm(range(len(online_list))):
                if online_list[i] != '0' + matchs[i]:
                    print(online_list[i], matchs[i])
                    print("匹配出错")
        print(f"这轮合计在线设备总数为：{online_dev}")
        print("#"*100)


    job()
    schedule.every(60).minutes.do(job)

    print("Task scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(1)
