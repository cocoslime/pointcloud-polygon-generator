import numpy as np
import csv


def pairwise(iterable):
    """s -> (s0, s1), (s2, s3), (s4, s5), ..."""
    a = iter(iterable)
    return zip(a, a)


def grid(data, x_num, y_num, data_range):
    result = []
    one_cell_x = (data_range[1] - data_range[0]) / x_num
    one_cell_y = (data_range[3] - data_range[2]) / y_num
    for i_data in data:
        index = 0
        grid_data = np.zeros((x_num, y_num))
        for x, y in pairwise(i_data):
            x_index = (x - data_range[0]) / one_cell_x
            x_index = int(x_index)
            y_index = int((y - data_range[2]) / one_cell_y)
            if x_index == x_num:
                x_index -= 1
            if y_index == y_num:
                y_index -= 1
            if index == 0:
                grid_data[x_index][y_index] = 2
            else:
                grid_data[x_index][y_index] = 1
            index += 1
        grid_data = grid_data.reshape([x_num, y_num, 1])

        result.append(grid_data.tolist())
    return result




def load_data(pre_path, data_num):
    x_data = []
    y_data = []
    for i in range(data_num):
        file_path = pre_path + str(i) + ".csv"
        csvfile = open(file_path, newline='')
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)

        i_data_num = 0
        i_x_data = []
        i_boundary = []
        for index, row in enumerate(reader):
            if index == 0:
                for label in row:
                    y_data.append([label])
                i_data_num = len(row)
            elif index <= i_data_num:
                i_x_data.append([row[0], row[1]])
            else:
                i_boundary.extend([row[0], row[1]])

        for i_data in i_x_data:
            i_data.extend(i_boundary)

        x_data.extend(i_x_data)

    return x_data, y_data
