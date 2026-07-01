import argparse
import os

from configparser import ConfigParser

from mhxy import *
from pic_target import *



class GameConf:

    def __init__(self):

        conn = ConfigParser()
        file_path = os.path.join(os.path.abspath("."), "resources/common.ini")
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")
        conn.read(file_path, encoding="utf-8")
        self.exepath = conn.get("main", "path")
        self.launcher= conn.get("main","launcher")
        players = conn.get("main","players")
        
        self.players = list(players.split(","))

    def print(self):
        log("path",self.exepath)
        log("launcher",self.launcher)
        log("players",self.players)



if __name__ == "__main__":
    common = GameConf()
    common.print()
