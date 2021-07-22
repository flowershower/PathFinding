from PIL import Image
import json


# функция формирует двумерный массив
# 0 и 1 на основе квадратного изображения
def get_grid_from_img(path='maze.png'):
    image = Image.open(path)
    size = image.size[0]
    data = [1 if x > 128 else 0 for x in list(image.getdata(0))]
    result = []

    for i in range(0, size * size, size):
        result.append(data[i:i + size])

    return result


# функция загрузки двумерного массива из json файла
def get_grid_from_json(path):
    return json.loads(path)
