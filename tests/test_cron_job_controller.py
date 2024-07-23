import pytest
from src import sftp_utils
from config import *


class Command:
    # 获取cron配置
    GET_CRON_CONFIG = "crontab -l"

    # 执行python脚本的正确配置
    CRON_CONFIG = '* * * * * python3 /root/tests/count_online_peers.py\n'

    # 设置cron配置，用于执行python脚本
    ONE_MINUTE_ONE_TIMES = ("(echo '* * * * * python3 /root/tests/count_online_peers.py'; cat "
                            "/var/spool/cron/crontabs/root) | sudo tee /var/spool/cron/crontabs/root > /dev/null")
    # 修改cron临时文件的权限为600
    CHMOD_COMMAND = 'chmod 600 /tmp/my_crontab'

    # 将cron配置写到临时文件中
    CRONTAB_EXPORT_COMMAND = 'crontab -l > /tmp/my_crontab'

    # 将临时文件读到cron配置中
    CRONTAB_IMPORT_COMMAND = 'crontab /tmp/my_crontab'


@pytest.mark.cron
@pytest.mark.parametrize("host", hosts)
def test_check_cron_configuration(host: str):
    # 检查服务器的cron配置
    # 第一步获取cron配置
    cron_configuration = sftp_utils.execute_remote_command(
        host=host,
        port=port,
        username=username,
        password=password,
        command=Command.GET_CRON_CONFIG)
    # 检查cron是否已配置
    if Command.CRON_CONFIG not in cron_configuration:
        # 如果没有配置，则上传测试代码
        files = ['count_online_peers.py', 'json_util.py']
        local_file_dir = r'C:\Users\Administrator\P2pServerTest\p2p_server\tests/'
        remote_file_dir = '/root/tests/'
        sftp_utils.execute_remote_command(
            host=host,
            port=port,
            username=username,
            password=password,
            command="mkdir {}".format(remote_file_dir))
        for file in files:
            local_file_path = local_file_dir + file
            remote_file_path = remote_file_dir + file
            sftp_utils.upload_file(host, port, username, password, local_file_path, remote_file_path)

        # 再配置cron
        sftp_utils.execute_remote_command(
            host=host,
            port=port,
            username=username,
            password=password,
            command=Command.ONE_MINUTE_ONE_TIMES)

    # 检查cron权限，暂时先不写代码


@pytest.mark.cron
@pytest.mark.parametrize("host", hosts)
def test_set_cron_permissions(host: str):
    commands = [Command.CRONTAB_EXPORT_COMMAND,
                Command.CHMOD_COMMAND,
                Command.CRONTAB_IMPORT_COMMAND]
    for command in commands:
        sftp_utils.execute_remote_command(
            host=host,
            port=port,
            username=username,
            password=password,
            command=command)
