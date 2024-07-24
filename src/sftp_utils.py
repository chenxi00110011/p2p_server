import os.path
import time
import paramiko
from datetime import datetime


def list_remote_directory_as_dict(host, port, username, password, remote_directory):
    """
    Connects to an SFTP server, lists the contents of a remote directory,
    and returns a dictionary with file names as keys and dictionaries containing
    file size and modification time as values. Then, it closes the connection.

    :param host: The hostname or IP address of the SFTP server.
    :param port: The port number to connect on (default is 22).
    :param username: The username for authentication.
    :param password: The password for authentication.
    :param remote_directory: The path of the remote directory to list.
    :return: A dictionary with file metadata.
    """
    file_info_dict = {}

    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SFTP server
        ssh.connect(hostname=host, port=port, username=username, password=password)

        # Initialize SFTP session
        sftp_client = ssh.open_sftp()

        try:
            # List files in the remote directory with attributes
            remote_files_attrs = sftp_client.listdir_attr(remote_directory)

            for attr in remote_files_attrs:
                # Convert timestamp to human-readable format
                mod_time = datetime.fromtimestamp(attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                # Store the file info in the dictionary
                file_info_dict[attr.filename] = {
                    'size': attr.st_size,
                    'last_modified': mod_time
                }

        finally:
            # Close the SFTP session
            sftp_client.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None in case of an error
    finally:
        # Ensure the SSH connection is closed
        ssh.close()

    return file_info_dict


def download_file_from_sftp(host, port, username, password, remote_directory, remote_filename, local_path, local_file_name=None):
    """
    Connects to an SFTP server, lists the contents of a remote directory,
    downloads a specified file, and returns a dictionary with file metadata.
    Then, it closes the connection.

    :param host: The hostname or IP address of the SFTP server.
    :param port: The port number to connect on (default is 22).
    :param username: The username for authentication.
    :param password: The password for authentication.
    :param remote_directory: The path of the remote directory.
    :param remote_filename: The name of the remote file to download.
    :param local_path: The local path where the file will be saved.
    :return: A dictionary with file metadata or None in case of an error.
    """
    file_info_dict = list_remote_directory_as_dict(host, port, username, password, remote_directory)

    if file_info_dict and remote_filename in file_info_dict:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the SFTP server
            ssh.connect(hostname=host, port=port, username=username, password=password)

            # Initialize SFTP session
            sftp_client = ssh.open_sftp()

            try:
                # Construct full remote path
                remote_file_path = f"{remote_directory}/{remote_filename}"

                # Download the file
                if not local_file_name:
                    local_file_name = remote_filename
                local_file_path = f"{local_path}/{local_file_name}"
                sftp_client.get(remote_file_path, local_file_path)
                print(f"File '{remote_filename}' downloaded to '{local_file_path}'.")

            finally:
                # Close the SFTP session
                sftp_client.close()

        except Exception as e:
            print(f"An error occurred during download: {e}")
            return None

        finally:
            # Ensure the SSH connection is closed
            ssh.close()

    else:
        print(f"File '{remote_filename}' not found in the remote directory.")
        return None


def execute_remote_command(host, port, username, password, command):
    """
    使用paramiko执行远程SSH命令。

    :param host: 主机名或IP地址
    :param port: SSH端口号，默认为22
    :param username: 登录用户名
    :param password: 登录密码
    :param command: 要执行的命令
    :return: 命令的标准输出和标准错误
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output, error
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, str(e)
    finally:
        ssh.close()


def upload_file(host, port, username, password, local_file_path, remote_file_path):
    """
    使用paramiko上传本地文件到远程服务器。

    :param host: 主机名或IP地址
    :param port: SSH端口号，默认为22
    :param username: 登录用户名
    :param password: 登录密码
    :param local_file_path: 本地文件的完整路径
    :param remote_file_path: 远程服务器上文件的目标路径
    """
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        # 上传文件
        sftp.put(local_file_path, remote_file_path)
        print(f"File uploaded successfully to {remote_file_path}")
    except Exception as e:
        print(f"An error occurred while uploading the file: {str(e)}")
    finally:
        # 关闭SFTP和Transport连接
        if sftp:
            sftp.close()
        if transport:
            transport.close()


if __name__ == '__main__':
    host = '139.159.218.144'
    port = 22
    username = 'root'
    password = 'ZOWELL@123456'
    local_file_path = r'C:\Users\Administrator\P2pServerTest\p2p_server\tests\config.py'
    remote_file_path = '/root/tests/config.py'

    upload_file(host, port, username, password, local_file_path, remote_file_path)