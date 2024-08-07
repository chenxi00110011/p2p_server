import configparser
import re


def ini_to_dict(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)

    # 将ConfigParser对象转换为字典
    config_dict = {section: dict(config.items(section)) for section in config.sections()}

    return config_dict


if __name__ == '__main__':
    # 使用示例
    file_path = r'C:\Users\Administrator\P2pServerTest\p2p_server\data\temp.ini'  # 这里替换为你的INI文件路径
    ini_dict = ini_to_dict(file_path)
    print(ini_dict)