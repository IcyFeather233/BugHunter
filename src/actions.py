import os


def get_bounds(bound):
    a, b, c, d = [int(i) for i in bound]
    return a, b, c, d


def click_node(bound, device_name):
    pos_x_start, pos_y_start, pos_x_end, pos_y_end = get_bounds(bound)
    cmd = "adb -s {} shell input tap {} {}".format(device_name, str((pos_x_start + pos_x_end) // 2), str((pos_y_start + pos_y_end) // 2))
    os.system(cmd)

def long_press_node(bound, device_name, duration = 1000):
    pos_x_start, pos_y_start, pos_x_end, pos_y_end = get_bounds(bound)
    pos_x = (pos_x_start + pos_x_end) // 2
    pos_y = (pos_y_start + pos_y_end) // 2

    cmd = "adb -s {} shell input swipe {} {} {} {} {}".format(device_name, pos_x, pos_y, pos_x, pos_y, duration)
    os.system(cmd)


def swipe_left(device_name, duration=500):
    cmd = "adb -s {} shell wm size".format(device_name)
    output = os.popen(cmd).read()
    width, height = map(int, output.split("Physical size:")[1].strip().split("x"))

    start_x = width * 3 // 4
    start_y = height // 2
    end_x = width // 4
    end_y = height // 2

    cmd = "adb -s {} shell input swipe {} {} {} {} {}".format(device_name, start_x, start_y, end_x, end_y, duration)
    os.system(cmd)

def swipe_right(device_name, duration=500):
    cmd = "adb -s {} shell wm size".format(device_name)
    output = os.popen(cmd).read()
    width, height = map(int, output.split("Physical size:")[1].strip().split("x"))

    start_x = width // 4
    start_y = height // 2
    end_x = width * 3 // 4
    end_y = height // 2

    cmd = "adb -s {} shell input swipe {} {} {} {} {}".format(device_name, start_x, start_y, end_x, end_y, duration)
    os.system(cmd)


def go_back(device_name):
    cmd = "adb -s {} shell input keyevent 4".format(device_name)
    os.system(cmd)


def change_orientation(device_name):
    raise NotImplementedError("You can implement this function by pyautogui.click(x, y) to click your Android Simulator.")