# @author JL
# @date 2023/9/25 16:41
from openpyxl import load_workbook
from pyproj import Transformer

# 改用pyproj2
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
print(transformer.transform(12, 12))

# workbook = load_workbook(filename="../data/machine_operation_4.xlsx", data_only=True)
# sheet = workbook["data"]
# print(sheet.dimensions)
#
# # 确定处理数据范围
# cell = sheet["F1:H3"]
# print(cell)
#
# data = []
#
# for i in cell:
#     point = []
#     for j in i:
#         print(j.value)

