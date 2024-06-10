import csv
import matplotlib.pyplot as plt
import cmath
from datetime import datetime


def tag_pos(a, b, c):
    cos_a = (b * b + c * c - a * a) / (2 * b * c)
    x = b * cos_a
    y = b * cmath.sqrt(1 - cos_a * cos_a)
    return round(x.real, 1), round(y.real, 1)

# CSV 檔案路徑
# csv_file = 'uwb_data.csv'
csv_file = 'uwb_data_example.csv'
# csv_file = 'uwb_data_1204.csv'
# csv_file = 'uwb_data_1607.csv'

# 讀取 CSV 資料
data = []
with open(csv_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        data.append({
            'Timestamp': datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S'),
            'Anchor': row['Anchor'],
            'Range': float(row['Range']) -0.6#/6*3.6#- 0.8  # 自動減去 1 米
        })

# 處理數據以獲取標籤位置
positions = []
timestamps = []
# anchor_positions = {
#     '1782': (0, 0),
#     '1783': (3.6, 0)  # 假設錨點之間的距離為3.0米
# }
distance_a1_a2 = 3.6

for i in range(0, len(data), 2):
    if i + 1 < len(data):
        if data[i]['Anchor'] == '84' and data[i + 1]['Anchor'] == '85':
            a1_range = data[i]['Range']
            a2_range = data[i + 1]['Range']
        elif data[i]['Anchor'] == '85' and data[i + 1]['Anchor'] == '84':
            a2_range = data[i]['Range']
            a1_range = data[i + 1]['Range']
        else:
            continue

        if(a1_range==0):
            a1_range=0.01
        if(a2_range==0):
            a2_range=0.01
        # if data[i]['Anchor'] == '1782' and data[i + 1]['Anchor'] == '1783':
        #     a1_range = data[i]['Range']
        #     a2_range = data[i + 1]['Range']
        # elif data[i]['Anchor'] == '1783' and data[i + 1]['Anchor'] == '1782':
        #     a2_range = data[i]['Range']
        #     a1_range = data[i + 1]['Range']
        # else:
        #     continue

        x, y = tag_pos(a2_range, a1_range, distance_a1_a2)
        positions.append((x, y))
        timestamps.append(data[i]['Timestamp'])

# 繪製位置圖
x_vals = [pos[0] for pos in positions]
y_vals = [pos[1] for pos in positions]

plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, linestyle='-', color='b', label='Tag Path')

# 使用quiver函數添加箭頭
for i in range(len(x_vals) - 1):
    plt.quiver(x_vals[i], y_vals[i], x_vals[i+1] - x_vals[i], y_vals[i+1] - y_vals[i], angles='xy', scale_units='xy', scale=1, color='b', alpha=0.6)

# 標註起始點和終點
plt.scatter([x_vals[0]], [y_vals[0]], color='g', s=100, label='Start Point')
plt.scatter([x_vals[-1]], [y_vals[-1]], color='r', s=100, label='End Point')
plt.annotate('Start', (x_vals[0], y_vals[0]), textcoords="offset points", xytext=(0, 10), ha='center', color='green')
plt.annotate('End', (x_vals[-1], y_vals[-1]), textcoords="offset points", xytext=(0, 10), ha='center', color='red')

# 標註錨點
plt.scatter([0, distance_a1_a2], [0, 0], color='orange', s=100, label='Anchors (84, 85)')

# 在 A1 和 A2 之間的中點添加停車格，缺口朝上

midpoint_x = distance_a1_a2 / 2
midpoint_y = 0
parking_lot_width = 0.6   #預設寬為0.35
parking_lot_height = 0.6  #預設長為0.45

parking_lot_x = [
    midpoint_x - parking_lot_width / 2, 
    midpoint_x - parking_lot_width / 2, 
    midpoint_x + parking_lot_width / 2,
    midpoint_x + parking_lot_width / 2
]
parking_lot_y = [
    midpoint_y + parking_lot_height, 
    midpoint_y, 
    midpoint_y, 
    midpoint_y + parking_lot_height
]

# midpoint_x = distance_a1_a2 / 2
# midpoint_y = 0
# parking_lot_size = 1.0
# parking_lot_x = [midpoint_x - parking_lot_size / 2, midpoint_x - parking_lot_size / 2, midpoint_x + parking_lot_size / 2,midpoint_x + parking_lot_size/2 ]
# parking_lot_y = [midpoint_y + parking_lot_size,midpoint_y, midpoint_y ,  midpoint_y + parking_lot_size]

plt.plot(parking_lot_x, parking_lot_y, 'green', label='Parking space')

# 設置灰色網格，間距為0.6米
plt.gca().set_xticks([x * 0.6 for x in range(int(distance_a1_a2 / 0.6) + 1)])
plt.gca().set_yticks([y * 0.6 for y in range(int(max(y_vals) / 0.6) + 1)])
plt.grid(color='gray', linestyle='--', linewidth=0.5)

plt.title('Tag Path Over Time')
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
# plt.ylim(top=0.5)
plt.ylim(bottom=-0.5)  # 設置 y 軸最小值為 0
plt.gca().invert_yaxis()#y的上下軸互換
plt.legend()
plt.grid(True)
plt.show()


# import csv
# import matplotlib.pyplot as plt
# import cmath
# from datetime import datetime

# def tag_pos(a, b, c):
#     cos_a = (b * b + c * c - a * a) / (2 * b * c)
#     x = b * cos_a
#     y = b * cmath.sqrt(1 - cos_a * cos_a)
#     return round(x.real, 1), round(y.real, 1)

# # CSV 檔案路徑
# csv_file = 'uwb_data_1619.csv'

# # 讀取 CSV 資料
# data = []
# with open(csv_file, mode='r') as file:
#     csv_reader = csv.DictReader(file)
#     for row in csv_reader:
#         data.append({
#             'Timestamp': datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S'),
#             'Anchor': row['Anchor'],
#             'Range': float(row['Range']) - 1.0  # 自動減去 1 米
#         })

# # 處理數據以獲取標籤位置
# positions = []
# timestamps = []
# anchor_positions = {
#     '1782': (0, 0),
#     '1783': (3.6, 0)  # 假設錨點之間的距離為3.0米
# }
# distance_a1_a2 = 4.0

# for i in range(0, len(data), 2):
#     if i + 1 < len(data):
#         if data[i]['Anchor'] == '1782' and data[i + 1]['Anchor'] == '1783':
#             a1_range = data[i]['Range']
#             a2_range = data[i + 1]['Range']
#         elif data[i]['Anchor'] == '1783' and data[i + 1]['Anchor'] == '1782':
#             a2_range = data[i]['Range']
#             a1_range = data[i + 1]['Range']
#         else:
#             continue

#         x, y = tag_pos(a2_range, a1_range, distance_a1_a2)
#         positions.append((x, y))
#         timestamps.append(data[i]['Timestamp'])

# # 繪製位置圖
# x_vals = [pos[0] for pos in positions]
# y_vals = [pos[1] for pos in positions]

# plt.figure(figsize=(10, 6))
# plt.plot(x_vals, y_vals, linestyle='-', color='b', label='Tag Path')

# # 使用quiver函數添加箭頭
# for i in range(len(x_vals) - 1):
#     plt.quiver(x_vals[i], y_vals[i], x_vals[i+1] - x_vals[i], y_vals[i+1] - y_vals[i], angles='xy', scale_units='xy', scale=1, color='b', alpha=0.6)

# # 標註起始點和終點
# plt.scatter([x_vals[0]], [y_vals[0]], color='g', s=100, label='Start Point')
# plt.scatter([x_vals[-1]], [y_vals[-1]], color='r', s=100, label='End Point')
# plt.annotate('Start', (x_vals[0], y_vals[0]), textcoords="offset points", xytext=(0, 10), ha='center', color='green')
# plt.annotate('End', (x_vals[-1], y_vals[-1]), textcoords="offset points", xytext=(0, 10), ha='center', color='red')

# # 標註錨點
# plt.scatter([0, distance_a1_a2], [0, 0], color='orange', s=100, label='Anchors (1782, 1783)')

# # 在 A1 和 A2 之間的中點添加停車格
# midpoint_x = distance_a1_a2 / 2
# midpoint_y = 0
# parking_lot_size = 1.0
# parking_lot_x = [midpoint_x - parking_lot_size / 2, midpoint_x + parking_lot_size / 2, midpoint_x + parking_lot_size / 2, midpoint_x - parking_lot_size / 2, midpoint_x - parking_lot_size / 2]
# parking_lot_y = [midpoint_y, midpoint_y, midpoint_y + parking_lot_size, midpoint_y + parking_lot_size, midpoint_y]

# plt.plot(parking_lot_x, parking_lot_y, 'green', label='Parking Lot')

# plt.title('Tag Path Over Time')
# plt.xlabel('X Position (m)')
# plt.ylabel('Y Position (m)')
# # plt.ylim(bottom=-0.5)  # 設置 y 軸最小值為 0
# # plt.gca().invert_yaxis()#y的上下軸互換
# plt.ylim(bottom=-0.5)  # 設置 y 軸最小值為 0
# plt.legend()
# plt.grid(True)
# plt.show()
