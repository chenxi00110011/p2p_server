import time
from datetime import datetime

from data_visualizer import main
from config import *
import pytest


@pytest.mark.flaky(reruns=3, reruns_delay=10)
@pytest.mark.parametrize("host", hosts)
def test_download_and_plot_data(host: str):
    # 生成前一天的日期
    dt = datetime.fromtimestamp(time.time() - 86400)
    date_str = '{:02d}-{:02d}-{:02d}'.format(dt.year, dt.month, dt.day)

    # 拼接成文件名
    down_file = date_str + '.log'

    # 下载并绘制折线图
    main(host, down_file)
