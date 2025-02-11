import cv2
import re

from component import Component


def extract_enabled_components(node):
    components = []

    if node.attrib.get('resource-id') == 'true' and 'com.android.systemui' in node.attrib.get('resource-id'):
        return

    def get_info_from_child(node, attrib):
        if node.attrib.get(attrib):
            return node.attrib.get(attrib)
        for child in node:
            info = get_info_from_child(child, attrib)
            if info:
                return info
        return ''
    
    if node.attrib.get('clickable') == 'true':
        bound_str = node.attrib.get('bounds')
        coords = list(map(int, re.findall(r'\d+', bound_str)))
        text = get_info_from_child(node, 'text') or ''
        resource_id = get_info_from_child(node, 'resource-id') or 'None'
        content_desc = get_info_from_child(node, 'content-desc') or 'None'
        name = f'text field is {text}, resource_id field is {resource_id}, content_desc field is {content_desc}'
        component = Component(name=name, bound=coords)
        components.append(component)

    # Recursively check for any child nodes
    for child in node:
        components.extend(extract_enabled_components(child))

    return components


def draw_bounds(image, bounds_list):
    num = 0
    for coords in bounds_list:
        num += 1
        x1, y1, x2, y2 = coords
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (0, 0, 255)  # Red color
        text = str(num)
        cv2.putText(image, text, (x1, y1+30), font, font_scale, font_color, 2)
    return image
