# @author JL
# @date 2023/9/25 16:41
import openpyxl
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


def write_excel_xlsx(path, sheet_name, value):
    """
    将坐标转换后的点集写回excel
    :param path:        文件存储路径
    :param sheet_name:  工作表名
    :param value:       需存储的数据
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for i in range(len(value)):
        for j in range(len(value[0])):
            sheet.cell(row=i + 1, column=j + 1, value=value[i][j])
    workbook.save(path)
    print("数据已存储在", path)


def judge_points(file_name):
    """
    散乱点集判别
    :param file_name: 文件存储路径
    """
    # 读取工作表
    workbook = load_workbook(filename=file_name, data_only=True)
    sheet = workbook["data"]
    print("数据表尺寸为：", sheet.dimensions)

    cell = sheet[sheet.dimensions]  # 确定处理数据范围
    points = []  # 存储点集平面坐标信息

    for point in cell:

        lon, lat = point[5].value, point[6].value  # 确保经度、纬度信息位于 F G 列
        x, y = transform_coordinates(lon, lat)

        if len(points) == 0 or [x, y] != points[len(points) - 1]:   # 点集去重复
            points.append([x, y])

    print("点集长度为：", len(points))

    points_angle = []  # 存储点集角度信息

    for i in range(len(points) - 1):
        point = points[i]
        point_next = points[i + 1]
        angle = math.degrees(math.atan2(point[1] - point_next[1], point[0] - point_next[0]))

        if angle > 90:
            angle -= 180
        elif angle <= -90:
            angle += 180

        points_angle.append(angle)

    print("有效点集的角度值：", points_angle)

    angle_sum_11 = 0
    for i in range(11):
        angle_sum_11 += points_angle[i]

    points_bias = []  # 瞬时角度偏差
    for i in range(len(points_angle) - 10):
        angle_c = points_angle[i + 5]   # 从第6个点开始计算瞬时角度偏差
        if i != 0:
            angle_sum_11 -= points_angle[i]
            angle_sum_11 += points_angle[i + 10]
        angle_bias = (angle_sum_11 / 11) - angle_c

        points_bias.append(angle_bias)

    print("角度瞬时偏差：", points_bias)

    point_bias_threshold = 10  # 角度偏差阈值
    point_num_threshold = 10  # 连续满足阈值条件的点数

    points_section = []
    begin_index = -1

    #  遍历查找满足条件的连续区间
    for i in range(len(points_bias) - 1):
        if points_bias[i] <= point_bias_threshold and begin_index == -1:
            begin_index = i
        elif points_bias[i] > point_bias_threshold:
            if begin_index != -1 and i - begin_index > point_num_threshold:
                points_section.append([begin_index, i - 1])
            begin_index = -1

    print("满足条件的连续区间：", points_section)

    isOperation = False
    section_angle = []  # 存储区间范围内的角度均值

    # 计算满足条件的连续区间点集的平均角度
    for section in points_section:
        begin = section[0]
        end = section[1]
        section_angle_sum = 0
        for index in range(begin, end + 1):
            section_angle_sum += points_angle[index + 5]    # points_bias和points_angle相差5个下标
        section_angle_mean = section_angle_sum / (end - begin + 1)
        section_angle.append(section_angle_mean)

    print(section_angle)

    section_bias_threshold = 10     # 区间角度差异阈值

    #   判断是否有两个连续区间的角度(斜率)差异满足阈值
    for i in range(len(section_angle) - 1):
        if math.fabs(section_angle[i] - section_angle[i + 1]) < section_bias_threshold:
            isOperation = True
            break

    if isOperation:
        print("正常作业点集")
    else:
        print("散乱点集")


if __name__ == "__main__":
    judge_points("../data/origin/machine_operation_1.xlsx")
