import argparse
import os
import time
import subprocess
import psutil
from configparser import ConfigParser

from mhxy import *
from pic_target import *


def runExe_(exePath):
    # 启动程序
    process = subprocess.Popen(exePath, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return process


def stopExe_(exePath):
    for proc in psutil.process_iter():
        try:
            # 检查进程的可执行文件路径是否与给定路径匹配
            # log(f"进程ID {proc.exe() }",exePath)
            if proc.exe() == exePath:
                # 找到进程后，获取其PID
                pid = proc.pid
                # 使用os.kill结束进程
                os.kill(pid, 9)  # 9是SIGKILL信号，强制结束进程
                log(f"已结束进程ID {pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            # 这些异常处理确保了如果进程不存在、访问被拒绝或进程是僵尸进程时，代码不会崩溃
            log(f"结束进程ID", "失败", e)
            pass


def hasExe_(exePath):
    for proc in psutil.process_iter():
        try:
            # 检查进程的可执行文件路径是否与给定路径匹配
            # log(f"进程ID {proc.exe() }",exePath)
            if proc.exe() == exePath:
                log(f"found进程ID")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            # 这些异常处理确保了如果进程不存在、访问被拒绝或进程是僵尸进程时，代码不会崩溃
            log(f"结束进程ID", "失败", e)
            pass

    return False
class GameExeHelp:

    def __init__(self):

        conn = ConfigParser()
        file_path = os.path.join(os.path.abspath("."), "resources/common.ini")
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")
        conn.read(file_path, encoding="utf-8")
        self.exepath = conn.get("main", "path")
        self.launcher= conn.get("main","launcher")

    def runExe(self):
        runExe_(exePath=self.launcher)

    def stopExe(self):
        stopExe_(exePath=self.exepath)
    
    def hasExe(self):
        hasExe_(exePath=self.exepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OF Generate")
    parser.add_argument("-i", "--idx", default=0, type=int)
    parser.add_argument(
        "-m", "--mission", default="shimeng,zhuxian,jingyanlian", type=str
    )
    args = parser.parse_args()
   
    exeHelp = GameExeHelp()
    exeHelp.stopExe()
    exeHelp.runExe()

   
    
    log("runed")
