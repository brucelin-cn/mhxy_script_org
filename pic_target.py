



from enum import Enum
from mhxy import *
# 定义一个枚举类
class PicLocateType(Enum):
    OnScreen = 0
    CenterOnScreen = 1   
    

class PicClickType(Enum):  
    WidthHeight = 0
    XY =1
    CustomXy = 2
    
    
class PicClickInfo:
     def __init__(self, type=PicClickType.WidthHeight,x =0, y= 0 ):
        self.type = type
        self.x= x
        self.y= y


class PicTarget(object):
    def __init__(self, path="", confidence = 0.9, type=PicLocateType.OnScreen,clickInfo = PicClickInfo() ):
        self.path = path
        self.type = type
        self.confidence=confidence
        self.clickInfo=clickInfo

    def print(self):
        print(self.path,self.type)
# 使用


class PicTargetNode(object):

    def __init__(self, picTarget):
        self.picTarget = picTarget
        self.next = None
        
    def setNext(self, nxt):
        self.next = nxt

def locatePic(target):
    ms = None
    if target.type == PicLocateType.CenterOnScreen:
         ms = Util.locateCenterOnScreen(target.path)

    elif target.type == PicLocateType.OnScreen:
        ms = Util.locateOnScreen(target.path, target.confidence)
    else:
        log("error not PicLocateType", target.type)
    

    if ms is None:
        log("not found " + target.path)
    
    return ms

def  tryClickPic(target):
    ms = locatePic(target)
    if ms is None:
        return ms
    
    if target.clickInfo.type == PicClickType.CustomXy:
        pyautogui.leftClick(
            ms.left + target.clickInfo.x, ms.top + +target.clickInfo.y
        )
    elif target.clickInfo.type == PicClickType.XY:

        pyautogui.leftClick(ms.x, ms.y)
    else:
        pyautogui.leftClick(ms.left + ms.width, ms.top + ms.height)
    
    return ms


if __name__ == '__main__':

    PicTarget("test",0).print()
   