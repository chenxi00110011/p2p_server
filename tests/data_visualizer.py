import copy
import os
import time
from datetime import datetime
from pandas import DataFrame
from config import *
import sftp_utils
import easygui
from json_util import read_and_deserialize_json
import viz_craft


def align_dict_values_lengths(input_dict):
    """
    对齐字典中值（列表）的长度。

    参数:
    input_dict (dict): 输入的字典，其中值为列表。

    返回:
    dict: 一个新字典，其中所有列表的长度已经被对齐。
    """
    # 如果字典为空，则直接返回
    if len(input_dict) == 0:
        return input_dict
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
    excel_dict = {}
    result = {'失败百分比': [],
              '总连接次数': [],
              '失败次数': [], }
    count = 0
    for ret_tuple in data:
        # 使用字典推导式为每个值列表添加0
        excel_dict = {key: value + [0] for key, value in excel_dict.items()}

        # 失败百分比、总连接次数、失败次数 初始化
        failure_percentage, all_count, faile_num = 0, 0, 0

        # 遍历外部字典
        for ret_key, inner_dict in ret_tuple[0].items():
            # 遍历内部字典
            for code_key, value in inner_dict.items():
                if ret_key == 'ret=-6' or ret_key == 'ret=-19':
                    continue
                elif code_key == '0x27' or code_key == '0x00':
                    continue
                # 创建新的键格式
                new_key = f"{ret_key}({code_key})"

                # 失败次数累加
                faile_num += value

                # # 转换为百分比
                # if percentage:
                #     value = (value / ret_tuple[1])

                # 如果键不存在，则添加；否则，追加值到现有列表中
                if new_key not in excel_dict.keys():
                    excel_dict[new_key] = [0 for _ in range(count)] + [value]
                else:
                    excel_dict[new_key][-1] = value

        # 总连接次数 = 失败次数 + 成功次数
        all_count = faile_num + data[count][1]

        # 失败百分比 = 失败次数/总连接次数
        if all_count:
            failure_percentage = faile_num / all_count
        else:
            failure_percentage = 0

        # result更新 总连接次数、失败次数、失败百分比
        result['总连接次数'].append(all_count)
        result['失败次数'].append(faile_num)
        result['失败百分比'].append(failure_percentage)

        count += 1

    # 换算为百分比
    if percentage:
        for ret, ret_data in excel_dict.items():
            for index, _ in enumerate(ret_data):
                if result['总连接次数'][index]:
                    excel_dict[ret][index] = _ / result['总连接次数'][index]
                else:
                    excel_dict[ret][index] = 0
    result.update(excel_dict)
    return result


def main(selected_choice_server, selected_choice_file):
    # 删除tmpe文件
    # 检查文件是否存在
    file_path = local_path + local_file_name
    if os.path.exists(file_path):
        # 删除文件
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    else:
        print(f"The file {file_path} does not exist.")

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
    fail_data = [(d.get('连接失败数据', '默认值'), d.get('实际成功次数', '默认值')) for d in data]
    # time_list = [_ for _ in range(len(fail_data))]

    # 用于存储到excel中的数据
    convert_data_to_ecxel = convert_to_format(fail_data, percentage=False)
    # print(convert_data_to_ecxel)
    # for k, v in convert_data_to_ecxel.items():
    #     print(k, v)

    # 用于生成折线图的数据
    convert_data = convert_to_format(fail_data, percentage=True)

    # 添加时间
    convert_data_to_ecxel['时间'] = time_list

    # 对齐数据
    convert_data_to_ecxel = align_dict_values_lengths(convert_data_to_ecxel)

    # 折线图的数据 移除总连接次数和失败次数
    del convert_data['总连接次数']
    del convert_data['失败次数']

    # 将数据调整为折线图可以识别的数据
    convert_data = pad_dictionary_lists(time_list, convert_data)

    # 去掉文件名的后缀，然后生成目录
    date_str = selected_choice_file.replace('.log', '')
    save_dataframe_to_excel(convert_data_to_ecxel,
                            '../data/{}/{}/{}.xlsx'.format(date_str, selected_choice_server, date_str))

    # 生成折线图
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
