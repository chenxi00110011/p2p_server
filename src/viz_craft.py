import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
from matplotlib.ticker import FuncFormatter
import time


def plot_line_chart_from_dict(data: dict):
    # 确保data字典中有time、value、type这三个key
    df = DataFrame(data)

    # 创建一个新的 Figure 对象并设置其大小
    fig, ax = plt.subplots(figsize=(14, 10))  # 设置宽度为10英寸，高度为6英寸

    # 设置 Seaborn 的样式
    sns.set_style("whitegrid")

    # 使用 Seaborn 的 lineplot 函数绘制折线图
    sns.lineplot(x="time", y="value", hue="type", data=df, ax=ax)

    # 设置 y 轴的范围
    ax.set_ylim(bottom=0, top=0.5)

    # 添加标题和标签
    ax.set_title('')
    ax.set_xlabel('time')
    ax.set_ylabel('value(%)')

    # 调整x轴标签的旋转角度
    plt.setp(ax.get_xticklabels(), rotation=45)

    # 设置自动日期定位器和格式器
    locator = AutoDateLocator()
    formatter = AutoDateFormatter(locator)

    # 应用定位器和格式器到x轴
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # 控制x轴标签的数量
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))

    # 定义一个函数来格式化y轴的刻度标签为百分比形式
    def to_percent(y, position):
        # 将y值转换为百分比字符串，假设原始数据是0-1的小数形式
        s = str(int(100 * y)) + '%' if y != '' else ''
        return s

    # 创建一个FuncFormatter对象，使用上面定义的to_percent函数
    formatter = FuncFormatter(to_percent)

    # 应用格式化到y轴
    ax.yaxis.set_major_formatter(formatter)

    # 保存图表，保持DPI一致，并使用之前设置的 figsize
    fig.savefig('../data/my_figure.png', dpi=100, bbox_inches='tight')

    # 显示图表
    plt.show()

    # 关闭
    time.sleep(10)
    plt.close(fig)
