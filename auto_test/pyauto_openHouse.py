import pyautogui as pygui
import time
import os

proDir = os.path.split(os.path.realpath(__file__))[0]
layoutImagePath = os.path.join(proDir, "layoutImage_result")


# 搜索户型并进入户型绘制页面
def searchHouse(houseid):
    # 点击菜单中项目户型 Point(x=427, y=78)
    pygui.click(x=427, y=78)
    time.sleep(1)
    # 点击切换户型id  Point(x=817, y=161)  ---》Point(x=799, y=262)
    # 先点击下拉框
    pygui.click(x=817, y=161)
    time.sleep(0.5)
    # 点击户型ID
    pygui.click(x=799, y=262)
    # 点击户型搜索输入框Point(x=950, y=155)
    # 输入户型点击搜索 --需要先双击选中后点击删除操作清空之前的输入内容
    pygui.doubleClick(x=950, y=155)
    pygui.press('backspace')
    # 输入户型id
    pygui.typewrite(houseid, 0.25)
    pygui.press('enter')
    time.sleep(1)
    # 点击绘制户型进入户型页面Point(x=220, y=422)
    pygui.click(x=220, y=422)
    time.sleep(10)


# 从户型创建方案
def creatSolution():
    # 点击创建方案 Point(x=1825, y=57)
    pygui.click(x=1825, y=57)
    time.sleep(8)


# 搜索DNA并点击
def searchDNA(dnaid):
    # 点击搜索DNA输入框Point(x=120, y=233)
    pygui.click(x=131, y=234)
    time.sleep(1)
    # 输入DNAid
    pygui.typewrite(dnaid, 0.5)
    time.sleep(1)
    # 输入DNAID回车点击搜索
    pygui.press('enter')
    # 点击该DNA Point(x=130, y=370)
    time.sleep(3)
    # 点击该DNA面板展示各户型详情
    pygui.click(x=130, y=370)
    time.sleep(2)


# 点击全屋套用
def fullHouseLayout():
    time.sleep(1)
    # 点击【全屋套用】按钮 Point(x=400, y=238) 弹出套用方式选择框
    pygui.click(x=400, y=238)
    time.sleep(3)
    # 套用方式选择框，选择【确定】按钮Point(x=896, y=626)
    pygui.click(x=896, y=626)


def mkImageDir(houseid, dnaid):
    # 生成json图片目录
    layoutImagePath_dir = layoutImagePath + '/solutionId_dnaid'+'/' + "{}_{}".format(houseid, dnaid)
    if not os.path.exists(layoutImagePath_dir):
        os.makedirs(layoutImagePath_dir)
        return layoutImagePath_dir
    else:
        # print('该目录已经存在')
        return layoutImagePath_dir


# 切换至顶视图鼠标滚轮向下滑动调整最佳视角截取当前顶视图
def screenshotVerImage(houseid, dnaid):
    # 点击切换到顶视图
    time.sleep(1)
    pygui.click(x=985, y=101)
    time.sleep(2)
    # 点击N按钮去掉吊顶
    pygui.press('N')
    time.sleep(1)
    # 鼠标向下滚动
    pygui.scroll(-20)
    # 鼠标向下拖拽
    pygui.dragRel(0, 200, duration=1, button='right')
    time.sleep(3)
    # 截取当前顶视图并保存到结果目录中
    pygui.screenshot(mkImageDir(houseid, dnaid) + "/{}_{}_VerImage.png".format(houseid, dnaid))


# 点击保存方案户型_dna_test
def saveSolution(houseid, dnaid):
    # 点击【保存】按钮Point(x=145, y=52)，弹出方案名称输入框
    pygui.click(x=145, y=52)
    time.sleep(1)
    # 点击方案名称输入框Point(x=989, y=454)
    pygui.click(x=989, y=454)
    time.sleep(1)
    # 输入格式（户型id_dnaid_test，如11033_66177_test）
    pygui.typewrite("{}_{}_test".format(houseid, dnaid), 0.5)
    # 点击【确认提交】按钮Point(x=1043, y=588) 等待5秒确认保存成功
    time.sleep(1)
    pygui.click(x=1043, y=588)
    time.sleep(5)


# 进入渲染页面截图
def screenshotRenderImage(houseid, dnaid):
    # 点击渲染Point(x=1003, y=49)
    # pygui.click(x=1003, y=49)
    pygui.moveTo(200, 300)
    time.sleep(1)
    pygui.dragTo(600, 300, duration=0.5)
    print("第一次转动视角")
    time.sleep(1)
    # 截取当前渲染视图1并保存到结果目录中
    pygui.screenshot(mkImageDir(houseid, dnaid) + "/{}_{}_RenderImage1.png".format(houseid, dnaid))
    time.sleep(1)

    pygui.dragTo(1150, 300, duration=1)
    print("第二次转动视角")
    # 截取当前渲染视图2并保存到结果目录中
    pygui.screenshot(mkImageDir(houseid, dnaid) + "/{}_{}_RenderImage2.png".format(houseid, dnaid))
    time.sleep(1)

    pygui.dragTo(1700, 300, duration=1)
    print("第三次转动视角")
    # 截取当前渲染视图3并保存到结果目录中
    pygui.screenshot(mkImageDir(houseid, dnaid) + "/{}_{}_RenderImage3.png".format(houseid, dnaid))
    time.sleep(1)

    pygui.dragTo(2250, 300, duration=1)
    print("第四次转动视角")
    # 截取当前渲染视图4并保存到结果目录中
    pygui.screenshot(mkImageDir(houseid, dnaid) + "/{}_{}_RenderImage4.png".format(houseid, dnaid))
    time.sleep(1)


# 退出渲染页面
def exit_RenderPage():
    time.sleep(1)
    pygui.click(x=1861, y=47)


# 退出方案页面
def exit_SolutionPage():
    # 方案页面点击退出按钮 Point(x=1882, y=52)
    pygui.click(x=1882, y=52)
    time.sleep(1)
    # 弹出提示框中点击【确定】按钮 Point(x=952, y=520)
    pygui.click(x=952, y=520)


def adjustView():
    # pygui.click(x=800, y=100)
    pygui.moveTo(100, 281)
    time.sleep(1)
    pygui.dragTo(600, 281, duration=1)



# adjustView()
# screenshotRenderImage('1030810', '66177')

if __name__ == '__main__':
    # 输入搜索户型并进入户型页面
    searchHouse('1030810')
    # #从户型页面点击创建方案
    creatSolution()
    # # 搜索DNA并点击
    searchDNA('66177')
    # time.sleep(2)
    #点击选择全屋套用
    fullHouseLayout()
    time.sleep(40)
    screenshotVerImage('1030810', '66177')
    saveSolution('1030810', '66177')
    screenshotRenderImage('1030810', '66177')
    exit_RenderPage()
    #点击退出方案
    time.sleep(2)
    exit_SolutionPage()
