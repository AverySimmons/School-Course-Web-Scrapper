import pygame as py
import json
import collections
import random

WINDOW_SIZE = py.Vector2(1280, 720)
POP_UP_SIZE = py.Vector2(400, 300)

def main():

    with open('data.json', 'r') as file:
        data = json.load(file)
    department_dict = data.get('departments', {})
    course_dict = data.get('courses', {})

    for depart in department_dict.values():
        depart["color"] = py.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    for course in course_dict.values():
        course["pos"] = py.Vector2(WINDOW_SIZE.x * random.random(), WINDOW_SIZE.y * random.random()) # if random positions are needed before calculating positions
        if course["department"] != None:
            course["color"] = department_dict[course["department"]["name"]]["color"]
        else:
            course["color"] = py.Color(255, 255, 255)

    for i in range(50):
        print(i)
        for course in course_dict.values():
            # set positions
            for target in course_dict:
                norm_vector = (course_dict[target]["pos"] - course["pos"])
                if norm_vector.length() == 0:
                    norm_vector.x = random.random()
                if norm_vector.length() < 10:
                    speed = -50
                elif  target in course["all_connections"] or course["course_name"] in course_dict[target]["all_connections"]:
                    speed = 200
                else:
                    speed = -0.1
                course["pos"] += norm_vector.normalize() * speed
    
    run_pygame(course_dict, department_dict)

def get_level(catalog_id):
    for char in catalog_id:
        if char.isdigit():
            return min(int(char), 4)
    return None

def render_text(text, font, surface, y_offset):
    text_render = font.render(text, True, "black")
    text_x = 10
    text_y = y_offset
    surface.blit(text_render, (text_x, text_y))
    return text_render.get_height() + 5

def split_text_into_lines(text, font, max_width, max_height):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_width, text_height = font.size(test_line)
        
        if text_width <= max_width and text_height <= max_height:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def create_pop_up(course):
    title_font = py.font.Font(None, 24)
    sub_title_font = py.font.Font(None, 14)
    normal_text_font = py.font.Font(None, 16)

    title_text = course["catalog_id"] + " " + course["course_name"]
    department_text = course["department"]["name"]
    credits_text = str(course["credits"])
    uvic_link_text = course["url"]
    description_text = course["description"]
    requisites_text = str(course["all_connections"])

    popup_surface = py.Surface(POP_UP_SIZE)
    popup_surface.fill(py.Color(230, 230, 230))

    y_offset = 10
    y_offset += render_text(title_text, title_font, popup_surface, y_offset)
    y_offset += render_text(department_text, sub_title_font, popup_surface, y_offset)
    y_offset += render_text("Credits: " + credits_text, sub_title_font, popup_surface, y_offset)
    y_offset += render_text("Link: " + uvic_link_text, sub_title_font, popup_surface, y_offset)
    y_offset += render_text("Description:", normal_text_font, popup_surface, y_offset)
    
    description_lines = split_text_into_lines(description_text, normal_text_font, POP_UP_SIZE.x - 20, POP_UP_SIZE.y - y_offset)
    for line in description_lines:
        y_offset += render_text(line, normal_text_font, popup_surface, y_offset)
    
    y_offset += render_text("Requisites:", normal_text_font, popup_surface, y_offset)
    y_offset += render_text(requisites_text, normal_text_font, popup_surface, y_offset)

    return popup_surface


def run_pygame(course_dict, department_dict):
    
    py.init()
    py.font.init()
    screen = py.display.set_mode(WINDOW_SIZE)
    clock = py.time.Clock()
    running = True
    offset = py.Vector2(0, 0)
    old_offset = py.Vector2(0, 0)
    starting_mouse_position = py.Vector2(0, 0)
    zoom = 1
    left_mouse_down = False
    space_down = False
    display_pop_up = False
    current_course = None

    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            if event.type == py.MOUSEBUTTONDOWN:
                if event.button == 1:
                    old_offset = offset
                    starting_mouse_position = py.mouse.get_pos()
                    left_mouse_down = True
                if event.button == 3:
                    display_pop_up = False
                    current_course = None
                    for course in course_dict.values():
                        if (py.Vector2(py.mouse.get_pos()) - (course["pos"] + offset) * zoom).length() < 6:
                            popup_surface = create_pop_up(course)
                            display_pop_up = True
                            current_course = course
                            break

                if event.button == 4:
                    zoom *= 1.1
                if event.button == 5:
                    zoom /= 1.1
            if event.type == py.MOUSEBUTTONUP:
                if event.button == 1:
                    left_mouse_down = False
            
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    if current_course != None and space_down == False:
                        space_down = True
                        print(current_course["url"])
            
            if event.type == py.KEYUP:
                if event.key == py.K_SPACE:
                    space_down = False
        

        if left_mouse_down:
            offset = old_offset + (py.Vector2(py.mouse.get_pos()) - starting_mouse_position) *  (1 / zoom)

        screen.fill("white")
        for key, course in course_dict.items():
            color = course["color"]
            color.a = get_level(course["catalog_id"]) * 50
            

            py.draw.circle(screen, color, (course["pos"] + offset) * zoom, 3)
            if (py.Vector2(py.mouse.get_pos()) - (course["pos"] + offset) * zoom).length() < 6:
                queue = collections.deque()
                seen = set()
                queue.append(key)
                while queue:
                    cur_node = queue.pop()
                    seen.add(cur_node)
                    for connect in course_dict[cur_node]["all_connections"]:
                        if connect in seen: continue
                        py.draw.line(screen, course_dict[cur_node]["color"], (course_dict[cur_node]["pos"] + offset) * zoom, (course_dict[connect]["pos"] + offset) * zoom)
                        queue.append(connect)
        if display_pop_up:
            screen.blit(popup_surface, WINDOW_SIZE / 10)
        py.display.flip()

        clock.tick(60)
    
    py.quit()

if __name__ == "__main__":
    main()