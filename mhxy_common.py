import argparse
import os
import time
import subprocess
import psutil
from configparser import ConfigParser

from mhxy import *
from pic_target import *
from game_conf import *
from game_watcher import *


# 定义一个枚举类
class CommonOpType(Enum):
    # 任务栏
    TaskBar = 0
    # 道具使用
    Tool = 1
    # npc交互
    NpcTargets = 2
    # 过场动画
    Cutscene = 3
    # 战斗场景
    Battle = 4
    # 任务特殊
    MissionSpe = 5
    # 完成标记
    Done = 6


class Common(MhxyScript):
    _chasepos = 2

    def __init__(
        self,
        idx=0,
        changWinPos=True,
        resizeToSmall=False,
        config=None,
        stopCheck=None,
        activityPic="",
    ) -> None:
        super().__init__(idx, changWinPos, resizeToSmall, config, stopCheck=stopCheck)

        log("newMession", "common")

        self.conf = GameConf()

        self.try_pics = []

        self.targets = [
            # PicTarget(
            #     path="resources/shimeng/renwulan_shimeng.png",
            #     confidence=0.7,
            #     type=PicLocateType.OnScreen,
            #     clickInfo=PicClickInfo(PicClickType.WidthHeight),
            # ),
        ]

        self.done_pics = [
            # PicTarget(
            #     path="resources/shimeng/wancheng_queding.png",
            #     type=PicLocateType.OnScreen,
            # ),
        ]

        self.activityPic = activityPic

        self.close_targets = [
            PicTarget(
                path="resources/common/close.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
                path="resources/common/close2.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
                path="resources/common/close3.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
                path="resources/common/close4.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
                path="resources/common/close5.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
                path="resources/common/close6.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
            PicTarget(
            path="resources/common/close7.png",
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.CustomXy, x=2, y=2),
            ),
        ]
        self.autoClose = True

        # 任务栏
        self.taskBarTargets = []

        # 道具使用
        self.toolTargets = []

        # npc交互
        self.npcTargets = []

        # 过场动画
        self.cutsceneTargets = []

        # 战斗场景
        self.battleTargets = []

        # 任务特殊
        self.missionSpeTargets = []

        # 完成标记
        self.doneTargets = []

        self.opTypeTargetListMap = {
            CommonOpType.TaskBar: self.taskBarTargets,
            CommonOpType.Tool: self.toolTargets,
            CommonOpType.NpcTargets: self.npcTargets,
            CommonOpType.Cutscene: self.cutsceneTargets,
            CommonOpType.Battle: self.battleTargets,
            CommonOpType.MissionSpe: self.missionSpeTargets,
            CommonOpType.Done: self.doneTargets,
        }

        self.timeOutSesc = 60 * 60

    def addTrigger(self, picTarget):
        self.targets.append(picTarget)

    def addOpTypeTrigger(self, optype, picTarget):

        self.opTypeTargetListMap[optype].append(picTarget)

    def addDone(self, picTargat):
        self.done_pics.append(picTargat)

    def runExe(self):
        log("")

    def autoClosEnable(self, b):
        self.autoClose = b

    def killExe(self):
        log("")

    def close(self):
        for index, target in enumerate(self.close_targets):
            ms = tryClickPic(target)
            if ms is not None:
                log("close pic")

            else:
                cooldown(5)

    def mission(self):

        start_time = time.perf_counter()

        opTypesOder = [
            CommonOpType.TaskBar,
            CommonOpType.Tool,
            CommonOpType.NpcTargets,
            CommonOpType.Cutscene,
            CommonOpType.Battle,
            CommonOpType.MissionSpe,
            CommonOpType.Done,
        ]

        passTaskBar = False

        while 1:
            
            CheckIfDis()
            pass
            end_time = time.perf_counter()

            elapsed_time = end_time - start_time
            log("Elapsed time:", elapsed_time)
            if elapsed_time > self.timeOutSesc:
                log("mission timeOut:", elapsed_time)
                break

            hasLocatedPic = False
            for _, op in enumerate(opTypesOder):

                if passTaskBar == True and op == CommonOpType.TaskBar:
                    passTaskBar = False
                    continue

                targets = self.opTypeTargetListMap[op]

                for index, target in enumerate(targets):
                    log("common",index)
                    ms = tryClickPic(target)
                    if ms is not None:
                        hasLocatedPic = True
                        cooldown(5)
                    else:
                        cooldown(2)
            if self.autoClose and hasLocatedPic == False:
                log("common","autoclose")
                self.close()

            if hasLocatedPic == True:
                passTaskBar = True
                pass

        # while 1:

        #     hasLocatedPic = False
        #     end_time = time.perf_counter()
        #     elapsed_time = end_time - start_time
        #     log("Elapsed time:", elapsed_time)
        #     if elapsed_time > 60 * 60:

        #         log("mission timeOut:", elapsed_time)
        #         break

        #     if self.autoClose:
        #         self.close()

        #     for index, target in enumerate(self.try_pics):

        #         ms = tryClickPic(target)
        #         if ms is not None:
        #             hasLocatedPic = True
        #             cooldown(5)
        #         else:
        #             cooldown(2)

        #     log("targs-----------------------------")
        #     for index, target in enumerate(self.targets):
        #         cooldown(5)
        #         ms = tryClickPic(target)
        #         if ms is not None:

        #             hasLocatedPic = True

        #     for index, target in enumerate(self.done_pics):

        #         ms = tryClickPic(target)
        #         if ms is not None:
        #             log("done", target.path, index)
        #             hasLocatedPic = True
        #             return

        #     if not hasLocatedPic:

        #         # 获取屏幕的宽度和高度
        #         screen_width, screen_height = pyautogui.size()

        #         # 计算屏幕中心的坐标
        #         center_x = screen_width // 2
        #         center_y = screen_height // 2

        #         # 在屏幕中心点击
        #         # pyautogui.click(center_x, center_y)

        #     cooldown(2)
        # log("end")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OF Generate")
    parser.add_argument("-i", "--idx", default=0, type=int)
    parser.add_argument(
        "-m", "--mission", default="shimeng,zhuxian,jingyanlian,baotu,dati", type=str
    )
    args = parser.parse_args()
    missionSet = set(args.mission.split(","))

    log("-------------")
    config = init(idx=args.idx)
    if "shimeng" in missionSet:
        if gotoActivity(r"resources/richang/shimeng2.png"):
            common = Common(idx=args.idx)
            cooldown(2)
            pictarget_shimeng = PicTarget(
                path="resources/shimeng/renwulan_shimeng.png",
                confidence=0.7,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            )

            common.addOpTypeTrigger(CommonOpType.TaskBar, pictarget_shimeng)
            pictarget_shimeng2 = PicTarget(
                path="resources/shimeng/renwulan_shimeng2.png",
                confidence=0.7,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            )

            common.addOpTypeTrigger(CommonOpType.TaskBar, pictarget_shimeng2)

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/shimeng/xuanzhe.png",
                    confidence=0.9,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            # common.addOpTypeTrigger(
            #     CommonOpType.NpcTargets,
            #     PicTarget(
            #         path="resources/common/qing_xuanzhe_yao_zuo_de_shi.png",
            #         confidence=0.6,
            #         type=PicLocateType.CenterOnScreen,
            #         clickInfo=PicClickInfo(PicClickType.XY, 76, 76),
            #     ),
            # )

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/common/quwancheng.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/common/quwancheng2.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/common/yaozhuodeshi.png",
                    confidence=0.7,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Tool,
                PicTarget(
                    path="resources/common/goumai.png",
                    # confidence=0.6,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Tool,
                PicTarget(
                    path="resources/common/shangjiao.png",
                    # confidence=0.6,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Tool,
                PicTarget(
                    path="resources/common/goumai2.png",
                    # confidence=0.6,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Tool,
                PicTarget(
                    path="resources/common/shiyong.png",
                    # confidence=0.6,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Tool,
                PicTarget(
                    path="resources/common/lingqu.png",
                    # confidence=0.6,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/common/quwancheng.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/shimeng/npc_shimeng.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Cutscene,
                PicTarget(
                    path="resources/common/kuaijin.png",
                    # confidence=0.6,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Cutscene,
                PicTarget(
                    path="resources/common/dianji_renyi_jixu.png",
                    confidence=0.9,
                    type=PicLocateType.OnScreen,
                    clickInfo=PicClickInfo(PicClickType.WidthHeight),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.MissionSpe,
                PicTarget(
                    path="resources/shimeng/jixurenwu.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )

            common.addOpTypeTrigger(
                CommonOpType.Done,
                PicTarget(
                    path="resources/shimeng/wancheng_queding.png",
                    type=PicLocateType.OnScreen,
                ),
            )

            common.mission()
    if "zhuxian" in missionSet:
        log("zhuxian111")
        pictarget_1 = PicTarget(
            path="resources/common/renwulan_zhuxian.png",
            confidence=0.6,
            type=PicLocateType.OnScreen,
            clickInfo=PicClickInfo(PicClickType.WidthHeight),
        )

        common = Common(idx=args.idx)
        common.addOpTypeTrigger(CommonOpType.TaskBar, pictarget_1)
        common.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/queren.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )
        common.addOpTypeTrigger(
            CommonOpType.Cutscene,
            PicTarget(
                path="resources/common/kuaijin.png",
                # confidence=0.6,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        common.addOpTypeTrigger(
            CommonOpType.Cutscene,
            PicTarget(
                path="resources/common/dianji_renyi_jixu.png",
                confidence=0.9,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )
        # common.addOpTypeTrigger(
        #         CommonOpType.NpcTargets,
        #         PicTarget(
        #             path="resources/common/qing_xuanzhe_yao_zuo_de_shi.png",
        #             confidence=0.6,
        #             type=PicLocateType.CenterOnScreen,
        #             clickInfo=PicClickInfo(PicClickType.XY, 76, 76),
        #         ),
        #     )

        common.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/yaozhuodeshi.png",
                confidence=0.7,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        common.addOpTypeTrigger(
            CommonOpType.Battle,
            PicTarget(
                path="resources/common/zidong_da.png",
                confidence=0.7,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )
        # common.addTrigger(pictarget_xuanze)
        # common.addDone(donePic)

        log(common.targets)
        common.mission()

    if "jingyanlian" in missionSet:

        pictarget_1 = PicTarget(
            path="resources/common/renwulan_jingyanlian.png",
            confidence=0.6,
            type=PicLocateType.OnScreen,
            clickInfo=PicClickInfo(PicClickType.WidthHeight),
        )

        common = Common(idx=args.idx)

        common.addTrigger(pictarget_1)

        log("zhuxian22")

        log(common.targets)
        common.mission()
    if "kaishi" in missionSet:
        
        common = Common(idx=args.idx)
        common.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/kaishi_youxi.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )


        log("zhuxian22")

        log(common.targets)
        common.mission()
    if "baotu" in missionSet:
        
        common = Common(idx=args.idx)
        common.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/kaishi_youxi.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )


        log("zhuxian22")

        log(common.targets)
        common.mission()
