"""
自动化运维：
1.每天凌晨检测一次
2.检测服务器的连通性
3.检测主程序（P2P和Relay）的运行状态
4.支持检测partner以及附属进程进程运行状态
5.检测日志生成情况是否正常
6.检测配置是否配置正确
7.通过分析日志关键词确认是否按照配置在运行
8.检测cpu，内存，磁盘占用情况
9.输出检测文档
"""
import time
from datetime import datetime
import os.path
import re
import pytest
from src import sftp_utils, filetools
from config import *

server_info = p2p_servers + relay_servers


@pytest.mark.parametrize('server', p2p_servers)
def test_validate_config_file(server: dict):
    # 检测配置是否配置正确

    # 本地服务器配置存放目录
    local_directory = r'C:\Users\Administrator\P2pServerTest\p2p_server\data'
    # 本地配置文件名称
    local_file_name = 'temp.ini'

    # 从服务器下载配置文件
    sftp_utils.download_file_from_sftp(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        remote_directory='/root/EasyDebug/config/',
        remote_filename='EasyDebugConfig.ini',
        local_path=local_directory,
        local_file_name=local_file_name
    )
    # 将配置文件转变为字典类型
    config_dict = filetools.ini_to_dict(os.path.join(local_directory, local_file_name))

    # 检查配置文件是否正确
    assert config_dict.get('Partner').get('port') == '5666'
    assert config_dict.get('Gateway').get('domain') == 'p2pgw-sgp.p6sai.com:8099'
    assert '3600' in config_dict.get('Interval').get('serverinfointerval')
    assert '3600' in config_dict.get('Interval').get('devdoublesigninterval')
    assert '3600' in config_dict.get('Interval').get('devlocinterval')
    assert '3600' in config_dict.get('Interval').get('devlifecycletincrementinterval')
    assert config_dict.get('BlackListPath').get('path') == '/root/EasyDebug/config/BlackList.ini'


@pytest.mark.parametrize('server', server_info)
def test_check_main_program_status(server: dict):
    # 检测主程序（P2P和Relay）的运行状态

    # 从服务器获取进程信息
    ps_aux_result = sftp_utils.execute_remote_command(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        command='ps -aux'
    )

    # 检查进程信息：GeoIPServer.py、client、Partner
    # print(ps_aux_result)
    assert 'Partner' in ps_aux_result[0]
    assert 'GeoIPServer.py' in ps_aux_result[0]

    # 检查client进程是否有3个
    pattern = r"client\s+\d{3,5}"
    matches = re.findall(pattern, ps_aux_result[0])
    assert len(matches) == 3


def test_check_main_and_partner_processes():
    # 检测partner以及附属进程进程运行状态
    pass


@pytest.mark.parametrize('server', server_info)
def test_monitor_log_activity(server: dict):
    # 检测日志生成情况是否正常
    command = 'stat /root/EasyDebug/log/Partner_Log1.log |grep "Modify"'
    # 从服务器获取进程信息
    stat_output = sftp_utils.execute_remote_command(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        command=command
    )
    # print(stat_output)
    # 匹配修改时间
    pattern = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"
    matches = re.findall(pattern, stat_output[0])
    # 定义日期时间字符串的格式
    format_str = "%Y-%m-%d %H:%M:%S"
    # 使用strptime将字符串转换为datetime对象
    dt = datetime.strptime(matches[0], format_str)
    # 使用timestamp方法将datetime对象转换为时间戳
    timestamp = dt.timestamp()
    # 检查日志修改时间
    assert time.time() - timestamp < 600


@pytest.mark.parametrize('server', server_info)
def test_monitor_system_resources(server):
    # 检测cpu，内存，磁盘占用情况

    # 从服务器cpu信息
    idle_output = sftp_utils.execute_remote_command(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        command="top -b -n 1 |grep Cpu| awk -F '[ :%,]+' '{for(i=1;i<=NF;i++) if($i==\"id\") print $(i-1)}'"
    )

    # 检查idle是否大于等于20%
    assert float(idle_output[0]) >= 20

    # 从服务器free信息
    free_output = sftp_utils.execute_remote_command(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        command="free|grep Mem| awk '{print $2, $6}'"
    )
    # 检查可用内存占比是否大于10%
    free_list = free_output[0].split()
    assert int(free_list[1]) / int(free_list[0]) >= 0.1

    # 从服务器df信息
    df_output = sftp_utils.execute_remote_command(
        host=server.get('host'),
        port=server.get('prot'),
        username=server.get('username'),
        password=server.get('password'),
        command="df -h | awk 'NR>1 {print $5}'"
    )
    # 检查可用磁盘使用占比是否小于90%
    free_list = df_output[0].split()
    for percentage_str in free_list:
        assert float(percentage_str.rstrip('%')) / 100 <= 0.9


if __name__ == '__main__':
    pass
