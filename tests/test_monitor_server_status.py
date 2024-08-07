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
import os.path
import pytest
from src import sftp_utils, filetools
from config import *


@pytest.mark.parametrize('server', server_info)
def test_validate_config_file(server: dict):
    # 检测配置是否配置正确
    # 定义配置参数
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

def test_check_main_program_status():
    # 检测主程序（P2P和Relay）的运行状态
    pass


def test_check_main_and_partner_processes():
    # 检测partner以及附属进程进程运行状态
    pass


def test_monitor_log_activity():
    # 检测日志生成情况是否正常
    pass


def test_monitor_system_resources():
    # 检测cpu，内存，磁盘占用情况
    pass

if __name__ == '__main__':
    pass