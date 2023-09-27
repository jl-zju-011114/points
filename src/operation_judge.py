# @author JL
# @date 2023/9/25 16:41
from openpyxl import load_workbook
from pyproj import Transformer
from pyproj import CRS
import math


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


# 读取工作表
file_name = "../data/machine_operation_4.xlsx"
workbook = load_workbook(filename=file_name, data_only=True)
sheet = workbook["data"]
print("数据表尺寸为：", sheet.dimensions)

# 确定处理数据范围
cell = sheet["F1:H1000"]
points = []

# 存储点集平面坐标信息
for point in cell:

    lon, lat = point[0].value, point[1].value
    speed = point[2].value
    x, y = transform_coordinates(lon, lat)

    # 点集去重复
    if len(points) == 0 or [x, y] != points[len(points) - 1]:
        points.append([x, y])

print("点集长度为：", len(points))

# 计算斜率、角度
points_angle = []
for i in range(len(points) - 1):

    point = points[i]
    point_next = points[i + 1]
    angle = math.atan2(point[1] - point_next[1], point[0] - point_next[0])

    points_angle.append(math.degrees(angle))

print("点集的角度值", points_angle)

# 滑动窗口，用于计算角度均值
angle_sum_11 = 0
for i in range(11):
    angle_sum_11 += points_angle[i]

points_bias = []    # 瞬时角度偏差
for i in range(len(points_angle) - 10):
    angle_c = points_angle[i + 5]
    if i != 0:
        angle_sum_11 -= points_angle[i]
        angle_sum_11 += points_angle[i + 10]
    angle_bias = (angle_sum_11 / 11) - angle_c

    points_bias.append(angle_bias)

print("角度瞬时偏差", points_bias)

bias_threshold = 20     # 角度偏差阈值
point_con_num = 25      # 连续满足阈值条件的点数

point_sections = []
begin_index = -1

for i in range(len(points_bias) - 1):
    if points_bias[i] <= bias_threshold and begin_index == -1:
        begin_index = i
    elif points_bias[i] > bias_threshold:
        if begin_index != -1 and i - begin_index > point_con_num:
            point_sections.append([begin_index, i - 1])
        begin_index = -1

print("满足条件的连续区间：", point_sections)




