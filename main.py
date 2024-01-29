import requests
import json
from bs4 import BeautifulSoup
import re

uvic_catalog_url = 'https://uvic.kuali.co/api/v1/catalog/courses/63580b862ddbf3001d4805b5?q='
uvic_api_url = 'https://uvic.kuali.co/api/v1/catalog/course/63580b862ddbf3001d4805b5/'
uvic_view_url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/'

class Department:
    def __init__(self, id, name) -> None:
        self.id = id # 5be366a356a15d000126de93
        self.name = name # Department of Computer Science

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Course:
    def __init__(self) -> None:
        self.url = None # https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf4f167a5c324003b0bcd
        self.course_name = None # Numerical Analysis
        self.catalog_id = None # CSC349A
        self.pre_reqs = []
        self.core_reqs = []
        self.all_connections = []
        self.id = None # 5cbdf4f167a5c324003b0bcd
        self.pid = None # ryelsJdp7N
        self.department = None # Department(Department of Computer Science)
        self.credits = None
        self.description = None # An introduction to selected topics in Numerical 
        # Analysis. Typical areas covered: error analysis, roots of equations, systems 
        # of linear equations, linear programming, interpolation, numerical integration, 
        # and ordinary differential equations.

        # reqs will be formated like [int, [array]]
        # -1 means do all the following, anything else means do that much
        # example: 
        # [-1, [
        #   [1, [
        #       "CSC110", "CSC111"
        #       ]
        #   ],
        #   [1, [
        #       "MATH110", "MATH211"
        #       ]
        #   ], 
        #   [1, [
        #       [-1, [
        #           "MATH200", "MATH201"
        #           ]
        #       ],
        #       [-1, [
        #           "MATH202"
        #           ]
        #       ], 
        #       [-1, [
        #           "MATH204"
        #           ]
        #       ]]
        #   ]
        # ]]

    def to_dict(self):
        return {
            'url': self.url,
            'course_name': self.course_name,
            'catalog_id': self.catalog_id,
            'pre_reqs': self.pre_reqs,
            'core_reqs': self.core_reqs,
            'all_connections': self.all_connections,
            'id': self.id,
            'pid': self.pid,
            'department': self.department.to_dict() if self.department else None,
            'credits': self.credits,
            'description': self.description,
        }

def main():
    course_dict, department_dict = create_graph()
    converted_department_dict = {}
    for key in department_dict:
        converted_department_dict[key] = department_dict[key].to_dict()
    converted_course_dict = {}
    for key in course_dict:
        valid_connections = []
        for connect in course_dict[key].all_connections:
            if connect in course_dict:
                valid_connections.append(connect)
        course_dict[key].all_connections = valid_connections
        converted_course_dict[key] = course_dict[key].to_dict()
    data = {
        'departments': converted_department_dict,
        'courses': converted_course_dict
    }
    with open('data.json', 'w') as file:
        json.dump(data, file)

def get_key_from_url(url):
    start_index = url.find("courses/") + len("courses/")
    end_index = url.find("?", start_index)
    if end_index != -1:
        course_id = url[start_index:end_index]
    else:
        raise Exception("Cannot get key from that URL !")
    return course_id

def add_reqs(course, reqs):
    pass

def create_graph():
    course_dict = {}
    deparment_dict = {}
    course_array = json.loads(requests.get(uvic_catalog_url).text)

    for course in course_array:
        new_course = Course()
        new_course.course_name = course["title"]
        new_course.catalog_id = course["__catalogCourseId"]
        new_course.pid = course["pid"]
        new_course.id = course["id"]
        course_page = json.loads(requests.get(uvic_api_url + new_course.pid).text)
        if "groupFilter1" in  course_page:
            deparment_name = course_page["groupFilter1"]["name"]
            if deparment_name not in deparment_dict:
                deparment_id = course_page["subjectCode"]["id"]
                deparment_dict[deparment_name] = Department(deparment_id, deparment_name)
            new_course.department = deparment_dict[deparment_name]
        new_course.credits = course_page["credits"]["credits"]["max"]
        new_course.description = course_page["description"].replace("</p>", "").replace("<p>", "")
        new_course.url = uvic_view_url + new_course.pid
        if "preAndCorequisites" in course_page:
            new_course.all_connections = re.findall(r'target="_blank">(.*?)<', course_page["preAndCorequisites"])
            add_reqs(new_course, course_page["preAndCorequisites"])
        course_dict[new_course.catalog_id] = new_course

    return course_dict, deparment_dict


if __name__ == "__main__":
    main()