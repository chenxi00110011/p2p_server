import json
import os


def read_and_deserialize_json(file_path: str) -> list:
    """
    从指定文件路径读取JSON数据，反序列化它，并返回结果。

    参数:
        file_path (str): 包含JSON数据的文件的路径。

    返回:
        dict or list: 反序列化后的Python数据结构。

    异常:
        FileNotFoundError: 如果文件不存在。
        json.JSONDecodeError: 如果文件内容不是有效的JSON格式。
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("文件未找到: {}".format(file_path))
    except json.JSONDecodeError as e:
        print("JSON解码错误: {}".format(e))


def serialize_and_append_to_json_array(data: dict, file_path: str):
    """
    将给定的数据字典序列化为JSON格式的字符串，并以数组元素的形式追加到指定的文件中。

    参数:
    data (dict): 要序列化的Python字典。
    file_path (str): 文件路径，用于存储JSON数据。

    返回:
    bool: 如果成功，则返回True；否则返回False。
    """
    # 确保数据目录存在
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        # 文件不存在，创建json列表并添加该数据
        json_array = [data]
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("[\n")
        except IOError as e:
            print("Error creating file: {}".format(e))
            return False
    else:
        # 文件存在，则反序列化该文件
        json_array = read_and_deserialize_json(file_path)
        json_array.append(data)

    try:
        # 序列化数据为JSON字符串
        json_str = json.dumps(json_array, indent=4, ensure_ascii=False)

        # 打开文件并写入数据
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json_str)

        return True
    except Exception as e:
        print("Error serializing data to JSON or appending to file: {}".format(e))
        return False


# 示例使用
if __name__ == "__main__":
    sample_data = {
        "name": "张三",
        "age": 30,
        "is_student": False,
        "grades": [90, 85, 92],
        "address": {
            "street": "123 Main St",
            "city": "北京",
            "country": "中国"
        }
    }

    file_path = "./data.json"

    success = serialize_and_append_to_json_array(sample_data, file_path)
    if success:
        print("Data successfully appended to the file.")
    else:
        print("Failed to append data to the file.")

    data = read_and_deserialize_json("./data.json")
    print(data)
    print(type(data))
