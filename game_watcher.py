import argparse
import os


from game_exehelp import *


from game_conf import *
from game_process import *


class WathDis:
    def __init__(self) -> None:
        pass


class DisconnectError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)  # 初始化基类
        self.errors = errors  # 可以添加额外的属性


def CheckIfDis():
    ms = Util.locateCenterOnScreen("resources/common/duanxian.png")

    if ms is not None:
        raise DisconnectError("is Disconnect")
    return ms


def CheckRelogin():
    targs = [
        PicTarget(
            path="resources/common/jinru_youxi.png",
            confidence=0.9,
            type=PicLocateType.CenterOnScreen,
            clickInfo=PicClickInfo(PicClickType.XY),
        ),
        PicTarget(
            path="resources/common/denglu_youxi.png",
            confidence=0.9,
            type=PicLocateType.CenterOnScreen,
            clickInfo=PicClickInfo(PicClickType.XY),
        ),
        PicTarget(
            path="resources/common/denglu_youxi2.png",
            confidence=0.9,
            type=PicLocateType.CenterOnScreen,
            clickInfo=PicClickInfo(PicClickType.XY),
        ),
    ]

    for _, target in enumerate(targs):
        ms = tryClickPic(target)
        if ms is not None:
            cooldown(10)
            log("CheckRelogin")
    pass


class GameWatcher:

    def __init__(self):

        self.conf = GameConf()
        self.playerIndex = 0

    def getNextPlayer(self):

        res = self.playerIndex
        self.playerIndex += 1
        if self.playerIndex >= len(self.conf.players):
            self.playerIndex = 0

    def getCurPlayer(self):
        res = self.playerIndex

    def start(self):

        help = GameExeHelp()

        orderList = [
            PicTargetNode(
                PicTarget(
                    path="resources/common/kaishi_youxi.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                )
            ),
            PicTargetNode(
                PicTarget(
                    path="resources/common/xiala_wanjia.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                )
            ),
            PicTargetNode(
                PicTarget(
                    path="resources/common/jinru_youxi.png.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                )
            ),
        ]

        top = orderList[0]
        i = 0
        while i < len(orderList) - 1:
            orderList[i].setNext(orderList[i + 1])
            i += 1

        while True:

            if help.hasExe():
                ms = Util.locateCenterOnScreen("resources/common/duanxian.png")
                if ms is None:
                    cooldown(30)
                    continue

                help.stopExe()
                cooldown(5)
                help.runExe()
            else:
                help.runExe()

            cooldown(10)

            resize = GameProcess()
            resize.moveZhuomianban()

            log("resized")

            findPicNode = top
            while findPicNode is not None:
                findPicNode = top
                ms = tryClickPic(findPicNode.picTarget)
                if ms is not None:
                    log("done")
                    findPicNode = findPicNode.next

                else:
                    cooldown(10)

            pass
        pass


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='OF Generate')
    # parser.add_argument('-s', '--size', default='small', type=str)
    # parser.add_argument('-d', '--direct', default='horizontal', type=str)
    # parser.add_argument('--type', default='zhuomian', type=str)
    # args = parser.parse_args()
    w = GameWatcher()
    w.start()
