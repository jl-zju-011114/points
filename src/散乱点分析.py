# 假设提供一个文件data.txt，每行中是一个点的坐标，如（3，4）,且已经按照时间序列排好
import math
from pyproj import Transformer
from pyproj import CRS


def transform_coordinates(lon, lat):
    """
    坐标转换函数
    :param lon:     经度
    :param lat:     纬度
    :return:    返回平面坐标
    """
    crs = CRS.from_epsg(4326)  # 大地坐标系（先纬度 再经度）
    crs_cs = CRS.from_epsg(3857)  # 墨卡托投影坐标系

    transformer = Transformer.from_crs(crs, crs_cs)
    x, y = transformer.transform(lat, lon)
    return x, y


def main():

    file = open('data.txt', 'rt')
    data = file.readlines()  # data存储原始坐标信息，按照时间序列分布
    file.close()

    pos = {}  # pos字典存储坐标信息，键为时间，值为x,y坐标构成的元组，如 1：（3，4）
    angle = {}  # angle字典存储除了起始点之外，每个点的瞬时角度
    judge = []  # judge列表存储寻找到的直线的倾斜角
    finish = 0  # finish表示判断出是不是散乱点（即有没有找到平行直线）,finish为1则说明不是散乱点
    cnt = 0  # cnt用来记录有连续几个点满足在同一条直线上的要求

    VE = float(input('输入角度阈值1,用于判断某点角度是否和拟合直线角度吻合：\n'))
    VK = float(input('输入角度阈值2，用于判断两条直线的斜率是否相同\n'))
    C = int(input('按照时间连续C个点角度偏差小于阈值，则视作直线运动，输入C：\n'))

    for i in range(0, len(data)):  # 将data字符串中坐标录入pos字典
        coordinates = transform_coordinates(data[i][0], data[i][1])
        pos[i] = coordinates


    for i in range(1, len(data)):  # 利用每个点和之前一点的位置，算出瞬时角度，存入angle字典
        if pos[i][0] == pos[i - 1][0] and pos[i][1] != pos[i - 1][1]:  # 两点x坐标相同，角度为pi/2
            angle[i] = math.pi / 2
        elif pos[i][0] == pos[i - 1][0] and pos[i][1] == pos[i - 1][1]:  # 两点重合（概率很小），角度用一个奇怪的值10标识，表示重合点
            angle[i] = 1000
        else:
            angle[i] = math.atan(
                (pos[i][1] - pos[i - 1][1]) / (pos[i][0] - pos[i - 1][0])) * 180 / math.pi  # 一般情况，利用反三角函数算出角度，使用角度制

    for i in range(6, len(angle) - 4):  # 按照11个点为一个窗口，移动窗口寻找直线，得到斜率
        flag = 0
        for k in range(i - 5, i + 6):  # 如果窗口内有重合点，移动窗口直到窗口内不存在这种点
            if angle[k] == 1000:
                flag = 1
                break
        if flag == 1:
            cnt = 0
            continue
        A = sum([angle[j] for j in range(i - 5, i + 6)]) / 11  # 计算拟合直线倾斜角
        E = angle[i] - A  # 计算瞬时角度和拟合直线角度之间的偏差
        if abs(E) < VE:  # 偏差小于阈值，表示找到一个在直线上的点
            cnt += 1
        else:
            cnt = 0
        if cnt == C:  # 当连续满足条件的点达到C时，找到一条直线
            result = sum([angle[t] for t in range(i - C + 1, i + 1)]) / C  # result存储这条直线的倾斜角，为直线上C个点瞬时角度的平均值
            for item in judge:  # 判断此次找到直线是否和之前找到的直线相平行，平行则结束程序，finish=1
                if abs(item - result) < VK:
                    finish = 1
                    break
            if finish == 1:
                break
            cnt = 0
            judge.append(result)
    if finish == 1:
        print('不是散乱点')
    else:
        print('是散乱点')


if __name__ == "__main__":
    main()
