import math

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame


def plot_line_chart_from_df(df: DataFrame, file_path: str):
    # 创建一个新的 Figure 对象并设置其大小
    fig, ax = plt.subplots(figsize=(14, 10))  # 设置宽度为10英寸，高度为6英寸

    # 设置 Seaborn 的样式
    sns.set_style("whitegrid")

    # 使用 Seaborn 的 lineplot 函数绘制折线图
    sns.lineplot(x="time", y="value", hue="type", data=df, ax=ax)

    # 设置 y 轴的范围
    # 找出 'value' 列中的最大值
    max_value = df['value'].max()
    max_value = math.ceil(max_value * 10) / 10
    ax.set_ylim(bottom=0, top=1)


    # 添加标题和标签
    ax.set_title('')
    ax.set_xlabel('time')
    ax.set_ylabel('value(%)')

    # 定义一个函数来格式化y轴的刻度标签为百分比形式
    def to_percent(y, position):
        # 将y值转换为百分比字符串，假设原始数据是0-1的小数形式
        s = str(int(100 * y)) + '%' if y != '' else ''
        return s

    # 创建一个FuncFormatter对象，使用上面定义的to_percent函数
    formatter_y = FuncFormatter(to_percent)

    # 应用格式化到y轴
    ax.yaxis.set_major_formatter(formatter_y)

    # 调整x轴标签的旋转角度
    plt.setp(ax.get_xticklabels(), rotation=45)

    # 设置自动日期定位器和格式器
    locator = mdates.AutoDateLocator()
    formatter_x = mdates.DateFormatter('%H:%M')  # 自定义日期格式

    # 应用定位器和格式器到x轴
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter_x)

    # 控制x轴标签的数量
    ax.xaxis.set_major_locator(plt.MaxNLocator(24))

    # 保存图表，保持DPI一致，并使用之前设置的 figsize
    fig.savefig(file_path, dpi=100, bbox_inches='tight')

    # 关闭
    plt.close(fig)


def plot_line_chart_from_dict(data: dict, file_dir: str):
    # 确保data字典中有time、value、type这三个key
    df = DataFrame(data)
    # 获取类别列的唯一值
    types = df['type'].unique()
    # 遍历每一个类别并创建独立的折线图
    for type in types:
        # 选择当前类别的数据
        df_category = df[df['type'] == type]
        plot_line_chart_from_df(df_category, file_dir + type + '.PNG')
