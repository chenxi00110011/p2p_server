# 0x20AF	1	7949452000000100	111076030000101	1HeJcg56	1HeJcg56

import random
import string
import pandas as pd


def generate_dataframe(bordid: str, num: int) -> dict:
    # 使用列表推导式生成随机字符串列表
    random_strings = [''.join(random.choices(string.ascii_letters + string.digits, k=8)) for _ in range(num)]
    var = {'版型ID': [bordid for _ in range(num)],
           '序号': [str(_ + 1) for _ in range(num)],
           '设备序列号': [str(_ + 7944190000010200) for _ in range(num)],
           'CMEI': [str(_ + 111057690010200) for _ in range(num)],
           '平台接入密码（预留功能，暂可不支持）': random_strings,
           '密钥': random_strings
           }
    return var


if __name__ == '__main__':
    data = generate_dataframe(bordid='0x20AF', num=20000)
    # 将字典转换为DataFrame
    df = pd.DataFrame(data)
    # 写入Excel文件
    file_name = '../data/employees.xlsx'
    df.to_excel(file_name, index=False)


