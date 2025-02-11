import uiautomator2 as u2
from datetime import datetime
import xml.etree.ElementTree as ET
import json
import os
import subprocess

from process_image import *


class Record:
    def __init__(self, device_name=None):
        self.device_name = device_name
        self.device = u2.connect(device_name)
        self.current_activity = "None"
        self.current_steps = 0
        self.last_action = "None, this is the first step"
        self.action_history = []
        self.last_record_time = "None"
        self.hierarchy_path = "hierarchy_files"
        self.screenshot_path = "screenshots"
        self.annotated_image_path = "annotated_images"
        self.components_path = "components"
        self.reset()

    def record(self):
        print("record")
        self.current_steps += 1
        self.last_record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # screenshot
        os.makedirs(self.screenshot_path, exist_ok=True)
        self.device.screenshot(f"{self.screenshot_path}/{self.current_steps}.jpg")
        # page hierarchy file
        self.save_page_hierarchy()
        # current activity
        self.current_activity = self.get_running_info()['activity']
        self.process_current()

    def reset(self):
        self.current_activity = "None"
        self.current_steps = 0
        self.last_record_time = "None"

        # clear these dirs
        directories = [self.hierarchy_path, self.screenshot_path, self.annotated_image_path, self.components_path]

        for directory in directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

        os.makedirs(self.screenshot_path, exist_ok=True)
        os.makedirs(self.hierarchy_path, exist_ok=True)
        os.makedirs(self.annotated_image_path, exist_ok=True)
        os.makedirs(self.components_path, exist_ok=True)

    def save_page_hierarchy(self):
        os.makedirs(self.hierarchy_path, exist_ok=True)
        path = self.hierarchy_path + "/" + str(self.current_steps) + ".xml"
        with open(path, 'w', encoding='utf-8') as hierarchy_file:
            page_source = self.device.dump_hierarchy(compressed=True, pretty=True)
            hierarchy_file.write(page_source)

    def subprocess_getoutput(self, stmt):
        result = subprocess.getoutput(stmt)
        return result

    def get_running_info(self):
        platform = os.name
        if platform == 'nt':
            if self.device_name:
                cmd = f"adb -s {self.device_name} shell dumpsys activity activities | findstr Activities"
            else:
                cmd = r"adb shell dumpsys activity activities | findstr Activities"
        elif platform == 'posix':
            if self.device_name:
                cmd = f"adb -s {self.device_name} shell dumpsys activity activities | grep mActivityComponent="
            else:
                cmd = r"adb shell dumpsys activity activities | grep mActivityComponent="
        else:
            raise Exception("Unsupported platform")
        
        res = self.subprocess_getoutput(cmd)
        pattern = r'Activities=\[(.*?)\]'
        match = re.search(pattern, res)
        real_res = match.group(1).split(' ')[-2]
        app_name = real_res.split('/')[0]
        activity_name = real_res.split('/')[1]
        return {'app': app_name, 'activity': activity_name}

    def process_current(self):
        tree = ET.parse(f"hierarchy_files/{self.current_steps}.xml")
        root = tree.getroot()
        enabled_components = extract_enabled_components(root)
        idx = 1
        for e in enabled_components:
            e.id = idx
            idx += 1
            
        print(f'Before process there is {len(enabled_components)} components')

        image_path = f'screenshots/{self.current_steps}.jpg'
        image = cv2.imread(image_path)

        # Drawing the bounds on the image
        enabled_bounds = [e.bound for e in enabled_components]
        image_with_bounds = draw_bounds(image, enabled_bounds)

        # Save the image with drawn bounds
        output_path = f'annotated_images/{self.current_steps}.jpg'
        cv2.imwrite(output_path, image_with_bounds)

        dict_list = [component.to_dict() for component in enabled_components]
        json_str = json.dumps(dict_list, ensure_ascii=False)
        print(json_str)

        with open(f"components/{self.current_steps}.json", 'w', encoding='utf-8') as f:
            f.write(json_str)

        print('ok!')