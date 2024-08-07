import os
import time

import schedule

if __name__ == '__main__':

    def job():
        os.system('pytest  -vs test_monitor_server_status.py')


    # 每天凌晨1点运行 job 函数
    job()
    schedule.every().day.at("01:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
