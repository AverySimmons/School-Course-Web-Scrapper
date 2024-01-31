
# School Course Web Scrapper

---

**Tools Used:** Python, Requests library, JSON, Pygame &nbsp;&nbsp;&nbsp;&nbsp; **Keywords:** Web scraping, Interactive graph, Data storage

---

### Description:
&nbsp;&nbsp;&nbsp;&nbsp;When I was registering for courses for my first year of university, graphs were quickly becoming my favorite data structure as I was chewing through a large number of LeetCode problems that required them. I wanted to do something more than just optimize algorithms, so I decided to create a program that would web-scrape my university's course catalog and compile the classes into a sorted, interactable display.


### Features:
- &nbsp;&nbsp;&nbsp;&nbsp;**Web Scapping:**  
The primary roadblock of web scrapping my course catalog was that each course page (as well as the catalog itself) was dynamically loaded, meaning that web logic was received from an API after the page was loaded. This meant that the requests library I was using was unable to read the web pages. To combat this, I carefully observed the incoming data to each page, and soon enough, I struck gold. Each class page loaded around 5 files that gave it data on its statistics, text, and most importantly, prerequisites. By looking at each course's file that held its prerequisites, I was able to notice a pattern. Each file was the same address followed by a different key that corresponded to the class; even better, the classes these keys belonged to were kept in a loaded file on the main course catalog page. From that knowledge, it was a simple matter of sticking each key at the end of the web address and reading all the data into memory.

- &nbsp;&nbsp;&nbsp;&nbsp;**Parsing Data:**  
The prerequisites for classes became somewhat complex quite quickly; courses could require a certain number of preconditions, and each of those preconditions could be a certain number (or all) of another set of preconditions. To make sense of all of this, I devised a custom JSON file storage system that would allow me to read the complex prerequisite tree. I then stored this data, along with various other useful class information, in a dictionary.

- &nbsp;&nbsp;&nbsp;&nbsp;**Displaying Data:**  
To display the web of courses, I created a custom game in Pygame. I set up the ability to zoom and pan with the mouse, then created a dot for each course with a color corresponding to the subject area. Then, I ran a physics simulation on each of these dots where those that are connected by a prerequisite are pulled together and those that are not are pushed apart. Finally, I added the ability to hover over each dot to show its web of connections to other courses, as well as click on each course to display its data.

### Code Breakdown:
- &nbsp;&nbsp;&nbsp;&nbsp;**Main:**  
This file contains all the logic to scrape and organize the course data.

- &nbsp;&nbsp;&nbsp;&nbsp;**Display:**  
This is the file that holds the code to simulate physics on and display the courses (as well as logic to control the camera).
