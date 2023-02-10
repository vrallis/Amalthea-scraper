import requests
import concurrent.futures
import re
import sys
import getpass
from bs4 import BeautifulSoup
import time

login_url = "https://amalthea.anatolia.edu.gr/lms/login/index.php"
dashboard_url = "https://amalthea.anatolia.edu.gr/lms/my/"

# User login
def user_login():
    global username
    global password
    print("This program scrapes amalthea and opens your courses for you and sends over random packet requests. Developed by me Bill (Notice: Credentials are not stored. This app/script is expiremental. Use at your own risk!)")
    username = str(input("Username: "))
    password = getpass.getpass(prompt='Password(Does not echo to console for security purposes): ')
    

#Call first login
user_login()

# Start session with the amalthea server
session = requests.Session()
login_page = session.get(login_url)

# Extract the CSRF token from the HTML
soup = BeautifulSoup(login_page.text, "html.parser")
form_action = soup.find("form")["action"]
form_token = soup.find("input", {"name": "logintoken"})["value"]

# Define the login form data
data = {
    "username": username,
    "password": password,
    "logintoken": form_token
}

# Submit the login form
response = session.post(form_action, data=data)

# Check if login was successful by accessing the dashboard page and searching if the page title matches the dashboards page title
dashboard_page = session.get(dashboard_url)
    

soup = BeautifulSoup(response.text, 'html.parser')
title = soup.find('title')
print("Logging in...")
if title.text == "Dashboard":
    print("Login Successful!")
    print("Scraping dashboard for available courses! This may take a moment. Be patient.")
else:
    print("Login Failed. Check your credentials.")
    print("Exiting")
    input("press any key to continue")
    sys.exit() 


response = session.get(dashboard_url)
soup = BeautifulSoup(response.text, "html.parser")
elements = soup.find_all(role="treeitem", class_="type_system depth_2 contains_branch")

#Searching for courses
url_pattern = re.compile(r"^https?://amalthea.anatolia.edu.gr/lms/course")
seen = set()
courses = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if url_pattern.match(href) and href not in seen:
        seen.add(href)
        courses.append(href)

if courses:
    print("Courses found:")
    for i in courses:
        m = requests.get(i)
        soup = BeautifulSoup(m.text, 'html.parser')
        ctitle = soup.find("title")
        str_ctitle = str(ctitle)
        filtered_title = re.sub("<[/]*title>", "", str_ctitle)
        print(filtered_title)
    
    
else:
    print("Something went wrong. No cources found.")
    print('Exiting... You will need to re-run the program.')
    input("press any key to continue")
    sys.exit()    

#Multithreading Sessions
def fetch_url(session, cources):
    for p in courses:
        response = session.get(p)
        return response.content
#User input on sessions/requests
secs = int(input("Enter the amount of time (in seconds) the sessions should stay open per url (the bigger the number the longer between session requests): "))
session_count = int(input("Enter the number of sessions you want to open per course: "))
request = int(input("Enter amount of requests to send in each session: "))

option = input("Proceed? y/n ")
if option == "y":
    pass
else:
    print("Exiting")
    input("press any key to continue")
    sys.exit()   
print("Warning: Executing request using mutlithreading. Please wait.")
#Multithreading Sessions again
with concurrent.futures.ThreadPoolExecutor() as executor:
    for k in courses:
        futures = [executor.submit(fetch_url, requests.Session(), courses) for i in range(session_count)]
        for f in concurrent.futures.as_completed(futures):
            for l in range(request):
                print("Treadpool started for session:",k,"for",secs,"second/s")
                for p in range(secs):
                    session.get(k)
                    f = requests.get(k)


print("proccess finished")
input("press any key to continue")
sys.exit()   








