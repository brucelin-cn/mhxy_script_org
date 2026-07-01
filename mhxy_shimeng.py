import argparse
import os
from configparser import ConfigParser

from mhxy_common import *

from mhxy import *


class Shimeng(Common):
    _chasepos = 2

    def __init__(
        self,
        idx=0,
        changWinPos=True,
        resizeToSmall=False,
        config=None,
        stopCheck=None,
    ) -> None:
        super().__init__(idx, changWinPos, resizeToSmall, config, stopCheck=stopCheck)

        log("newMession", "common")

        pictarget_shimeng = PicTarget(
            path="resources/shimeng/renwulan_shimeng.png",
            confidence=0.7,
            type=PicLocateType.OnScreen,
            clickInfo=PicClickInfo(PicClickType.WidthHeight),
        )

        self.addOpTypeTrigger(CommonOpType.TaskBar, pictarget_shimeng)
        pictarget_shimeng2 = PicTarget(
            path="resources/shimeng/renwulan_shimeng2.png",
            confidence=0.7,
            type=PicLocateType.OnScreen,
            clickInfo=PicClickInfo(PicClickType.WidthHeight),
        )

        self.addOpTypeTrigger(CommonOpType.TaskBar, pictarget_shimeng2)

        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/shimeng/xuanzhe.png",
                confidence=0.9,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )


        self.addOpTypeTrigger(
                CommonOpType.NpcTargets,
                PicTarget(
                    path="resources/common/queren.png",
                    confidence=0.9,
                    type=PicLocateType.CenterOnScreen,
                    clickInfo=PicClickInfo(PicClickType.XY),
                ),
            )


        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/quwancheng.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/quwancheng2.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/yaozhuodeshi.png",
                confidence=0.7,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Tool,
            PicTarget(
                path="resources/common/goumai.png",
                # confidence=0.6,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Tool,
            PicTarget(
                path="resources/common/shangjiao.png",
                # confidence=0.6,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Tool,
            PicTarget(
                path="resources/common/goumai2.png",
                # confidence=0.6,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Tool,
            PicTarget(
                path="resources/common/shiyong.png",
                # confidence=0.6,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Tool,
            PicTarget(
                path="resources/common/lingqu.png",
                # confidence=0.6,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/common/quwancheng.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.NpcTargets,
            PicTarget(
                path="resources/shimeng/npc_shimeng.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Cutscene,
            PicTarget(
                path="resources/common/kuaijin.png",
                # confidence=0.6,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Cutscene,
            PicTarget(
                path="resources/common/dianji_renyi_jixu.png",
                confidence=0.9,
                type=PicLocateType.OnScreen,
                clickInfo=PicClickInfo(PicClickType.WidthHeight),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.MissionSpe,
            PicTarget(
                path="resources/shimeng/jixurenwu.png",
                confidence=0.9,
                type=PicLocateType.CenterOnScreen,
                clickInfo=PicClickInfo(PicClickType.XY),
            ),
        )

        self.addOpTypeTrigger(
            CommonOpType.Done,
            PicTarget(
                path="resources/shimeng/wancheng_queding.png",
                type=PicLocateType.OnScreen,
            ),
        )
        
    def do(self):
        self.autoClosEnable(True)
        self.mission()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OF Generate")
    parser.add_argument('-ir', '--idxArray', required=False, default='0', type=str)
    args = parser.parse_args()

    log("-------------")
    
    indexArr = args.idxArray.split(',')
    
    def func(idx):
        log("shimeng do1",idx)       
        log("shimeng do")
        s = Shimeng(idx=idx)
        s.do()


 
    func(int(indexArr[0]))

    
