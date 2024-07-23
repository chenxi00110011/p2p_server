import pytest
from src import sftp_utils
from config import *


class Command:
    GET_CRON_CONFIG = "crontab -l"
    CRON_CONFIG = '* * * * * python3 /root/tests/count_online_peers.py\n'
    ONE_MINUTE_ONE_TIMES = ("(echo '* * * * * python3 /root/tests/count_online_peers.py'; cat "
                            "/var/spool/cron/crontabs/root) | sudo tee /var/spool/cron/crontabs/root > /dev/null")


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
