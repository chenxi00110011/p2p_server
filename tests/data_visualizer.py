import copy
import os
import time
from datetime import datetime
from pandas import DataFrame
from config import *
from src import sftp_utils
import easygui
from json_util import read_and_deserialize_json
from src import viz_craft


def align_dict_values_lengths(input_dict):
    """
    对齐字典中值（列表）的长度。

    参数:
    input_dict (dict): 输入的字典，其中值为列表。

    返回:
    dict: 一个新字典，其中所有列表的长度已经被对齐。
    """
    # 查找最长的列表长度
    max_length = max(len(lst) for lst in input_dict.values())

    # 创建一个新字典来存储对齐后的列表
    aligned_dict = {}

    # 遍历输入字典中的每个键值对
    for key, value in input_dict.items():
        # 如果列表长度小于最长列表的长度，则填充 None
        if len(value) < max_length:
            # 使用 None 填充较短的列表
            value.extend([0] * (max_length - len(value)))

        # 将对齐后的列表添加到新字典中
        aligned_dict[key] = value

    return aligned_dict


def save_dataframe_to_excel(data, file_path):
    """
    Save a Pandas DataFrame to an Excel file.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be saved.
    - file_path (str): The full path including filename and extension where the Excel file will be saved.

    Returns:
    - None
    """
    # Check if the directory exists, if not create it
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    df = DataFrame(data)
    # 将时间列放到最前面
    if '时间' in df.columns:
        timestamp_col = df.pop('时间')
        df.insert(0, '时间', timestamp_col)
    # Save the DataFrame to Excel
    df.to_excel(file_path, index=False)


def pad_dictionary_lists(time_list: list, dictionary: dict):
    # 将数据调整为折线图可以识别的数据
    # data数据需要time、value、type这三个key
    df = {
        'time': [],
        'value': [],
        'type': []
    }
    # 遍历字典，将每个列表的长度补齐到最大长度
    for key in dictionary.keys():
        df['time'] += time_list
        df['value'] += dictionary[key]
        while len(df['value']) < len(df['time']):
            df['value'].append(0)
        while len(df['type']) < len(df['time']):
            df['type'].append(key)

    return df


def timestamp_to_array(timestamp):
    """
    将单个时间戳转换为包含年、月、日、时、分、秒的数组。

    参数:
        timestamp (int/float): 时间戳值。

    返回:
        list: 时间数组 [年, 月, 日, 时, 分, 秒]。
    """
    dt = datetime.fromtimestamp(timestamp)

    return '{:02d}:{:02d}:{:02d}'.format(dt.day, dt.hour, dt.minute)


def select_single_option(message, title, choices):
    """
    Displays a multichoice box to the user and ensures only one choice is made.

    :param message: The message to be displayed on the dialog box.
    :param title: The title of the dialog box.
    :param choices: A list of strings representing the choices available.
    :return: The selected choice if one is made, otherwise None.
    """
    selected_choices = easygui.multchoicebox(message, title, choices)

    if selected_choices and len(selected_choices) == 1:
        return selected_choices[0]
    else:
        print("请选择其中1个，不要多选")
        return None


def convert_to_format(data: list, percentage=True):
    # 对齐数据
    # 创建一个空字典用于存储结果
    result = {'失败百分比': [_[2] for _ in data],
              '总连接次数': [_[3] for _ in data],
              '失败次数': [_[4] for _ in data], }
    count = 0
    for ret_tuple in data:
        # 遍历外部字典
        for ret_key, inner_dict in ret_tuple[0].items():
            # 遍历内部字典
            for code_key, value in inner_dict.items():
                if ret_key == 'ret=-6' and (code_key == '0x01' or code_key == '0x00'):
                    break
                elif code_key == '0x27':
                    break
                # 创建新的键格式
                new_key = f"{ret_key}({code_key})"

                # 转换为百分比
                if percentage:
                    value = (value / ret_tuple[1])

                # 如果键不存在，则添加；否则，追加值到现有列表中
                if new_key not in result.keys():
                    result[new_key] = [0 for _ in range(count)] + [value]
                else:
                    result[new_key].append(value)
            # # 添加失败百分比
            # if "失败百分比" not in result.keys():
            #     result["失败百分比"] = [ret_tuple[2]]
            # else:
            #     result["失败百分比"].append(ret_tuple[2])

        count += 1
    return result


def main(selected_choice_server, selected_choice_file):
    # 下载JSON文件
    sftp_utils.download_file_from_sftp(
        host=selected_choice_server,
        port=port,
        username=username,
        password=password,
        remote_directory=remote_directory,
        remote_filename=selected_choice_file,
        local_path=local_path,
        local_file_name=local_file_name
    )

    # 反序列化数据
    data = read_and_deserialize_json(local_path + local_file_name)

    # 解析出时间戳列表
    time_list = [d['时间戳'] for d in data]
    # time_list = [timestamp_to_array(_) for _ in time_list]
    time_list = [datetime.fromtimestamp(_) for _ in time_list]

    # 解析出失败数据
    fail_data = [(d.get('连接失败数据', '默认值'), d.get('总连接次数', '默认值'), d.get('实际失败百分比', '默认值'),
                  d.get('总连接次数', '默认值'), d.get('失败次数', '默认值')) for d in data]
    # time_list = [_ for _ in range(len(fail_data))]

    # 用于存储到excel中
    convert_data_to_ecxel = convert_to_format(fail_data, percentage=False)

    # convert_data数据
    convert_data = convert_to_format(fail_data)

    # 添加时间
    convert_data_to_ecxel['时间'] = time_list

    # 对齐数据
    convert_data_to_ecxel = align_dict_values_lengths(convert_data_to_ecxel)

    # 移除总连接次数和失败次数
    del convert_data['总连接次数']
    del convert_data['失败次数']

    convert_data = pad_dictionary_lists(time_list, convert_data)
    # dt = datetime.fromtimestamp(time.time())
    # date_str = '{:02d}-{:02d}-{:02d}'.format(dt.year, dt.month, dt.day)
    date_str = selected_choice_file.replace('.log', '')

    save_dataframe_to_excel(convert_data_to_ecxel,
                            '../data/{}/{}/{}.xlsx'.format(date_str, selected_choice_server, date_str))
    viz_craft.plot_line_chart_from_dict(convert_data, '../data/{}/{}/'.format(date_str, selected_choice_server))


if __name__ == '__main__':
    # 使用函数
    choices = hosts
    title = "服务器连接"
    msg = "请选择列表中的一个服务器"

    selected_choice_server = select_single_option(msg, title, choices)

    if selected_choice_server:
        print("You selected:", selected_choice_server)
    else:
        raise Exception("未选择服务器")

    # 获取服务器/root/tests/目录下的文件列表
    files = sftp_utils.list_remote_directory_as_dict(
        host=selected_choice_server,
        port=port,
        username=username,
        password=password,
        remote_directory='/root/tests/'
    )

    # 选择服务器/root/tests/目录下的log文件
    choices = [k for k in files.keys() if 'log' in k]
    title = "文件选择"
    msg = "请选择列表中的一个文件"

    selected_choice_file = select_single_option(msg, title, choices)
    print("You selected:", selected_choice_file)
    main(selected_choice_server, selected_choice_file)
