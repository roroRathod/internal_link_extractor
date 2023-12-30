import sys
import re
import json
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin
import os 
import signal
import sqlite3


# Establish a connection to the SQLite database
conn = sqlite3.connect('results.db')

# Create a cursor object
cur = conn.cursor()

# Execute a command to create a table if it doesn't exist
cur.execute('''CREATE TABLE IF NOT EXISTS Results 
            (Source TEXT, URL TEXT, Location TEXT)''')

class Result:
    def __init__(self, source, url, location):
        self.Source = source
        self.URL = url
        self.Location = location 

headers = {}

def main():
    inside = False
    threads = 8
    depth = 2
    maxSize = -1
    insecure = False
    subsInScope = False
    showJson = False
    showSource = False
    showWhere = False
    rawHeaders = ""
    unique = False
    proxy = ""
    timeout = -1
    disableRedirects = False

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == "-i":
            inside = True
        elif arg == "-t":
            threads = int(args.pop(0))
        elif arg == "-d":
            depth = int(args.pop(0))
        elif arg == "-size":
            maxSize = int(args.pop(0))
        elif arg == "-insecure":
            insecure = True
        elif arg == "-subs":
            subsInScope = True
        elif arg == "-json":
            showJson = True
        elif arg == "-s":
            showSource = True
        elif arg == "-w":
            showWhere = True
        elif arg == "-h":
            rawHeaders = args.pop(0)
        elif arg == "-u":
            unique = True
        elif arg == "-proxy":
            proxy = args.pop(0)
        elif arg == "-timeout":
            timeout = int(args.pop(0))
        elif arg == "-dr":
            disableRedirects = True

    if proxy != "":
        os.environ["PROXY"] = proxy
    proxyURL = urlparse(os.environ.get("PROXY"))

    try:
        parseHeaders(rawHeaders)
    except Exception as e:
        print("Error parsing headers:", e)
        sys.exit(1)

    if sys.stdin.isatty():
        print("No urls detected. Hint: cat urls.txt | hakrawler")
        sys.exit(1)

    results = []
    for url in sys.stdin:
        url = url.strip()
        hostname = extractHostname(url)
        allowed_domains = [hostname]

        if headers:
            if "Host" in headers:
                allowed_domains.append(headers["Host"])

        c = requests.Session()

        if maxSize != -1:
            c.max_body_size = maxSize * 1024

        if subsInScope:
            c.allowed_domains = None
            c.url_filters = [re.compile(".*(\\.|\\/\\/)" + re.escape(hostname).replace(".", "\\.") + "((#|\\/|\\?).*)?")]

        if disableRedirects:
            c.redirect_handler = lambda req, resp: resp

        c.headers = headers

        if proxy != "":
            c.proxies = {
                "http": proxyURL.geturl(),
                "https": proxyURL.geturl()
            }
            c.verify = not insecure
        else:
            c.verify = not insecure

        if timeout == -1:
            visit(url, c, inside, showSource, showWhere, showJson, results)
        else:
            try:
                visit_with_timeout(url, c, inside, showSource, showWhere, showJson, results, timeout)
            except TimeoutError:
                print("[timeout] " + url)

    if unique:
        results = list(set(results))

    if showJson:
        for result in results:
            print(json.dumps(result.__dict__))
    # else:
    #     for result in results:
    #         if showSource:
    #             print("[" + result.Source + "] " + result.URL)
    #         elif showWhere:
    #             print("[" + result.Where + "] " + result.URL)
    #         else:
    #             print(result.URL)

def parseHeaders(rawHeaders):
    global headers
    if rawHeaders != "":
        if ":" not in rawHeaders:
            raise Exception("headers flag not formatted properly (no colon to separate header and value)")
        headers = {}
        rawHeaders = rawHeaders.split(";;")
        for header in rawHeaders:
            parts = re.split(": ?", header, 1)
            if len(parts) != 2:
                continue
            headers[parts[0].strip()] = parts[1].strip()

def extractHostname(urlString):
    u = urlparse(urlString)
    if not u.netloc:
        raise Exception("Input must be a valid absolute URL")
    return u.netloc

def visit(url, c, inside, showSource, showWhere, showJson, results):
    r = c.get(url)
    r.raise_for_status()
    html = r.text

    links = re.findall(r'<a[^>]*href=["\'](.*?)["\']', html)
    for link in links:
        if not link.startswith('http'):
           continue
        abs_link = c.get(link).url
        if abs_link in url or not inside:
            printResult(link, "href", showSource, showWhere, showJson, results, url)

    scripts = re.findall(r'<script[^>]*src=["\'](.*?)["\']', html)
    for script in scripts:
        printResult(script, "script", showSource, showWhere, showJson, results, url)

    forms = re.findall(r'<form[^>]*action=["\'](.*?)["\']', html)
    for form in forms:
        printResult(form, "form", showSource, showWhere, showJson, results, url)

def visit_with_timeout(url, c, inside, showSource, showWhere, showJson, results, timeout):
    def timeout_handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        visit(url, c, inside, showSource, showWhere, showJson, results)
    finally:
        signal.alarm(0)

def printResult(link, sourceName, showSource, showWhere, showJson, results, url):
  # Ensure 'link' is an absolute URL
  link = urljoin(url, link)
  result = link
  locationURL = url
  if result:
      location = ""
      if showWhere:
          location = locationURL
      if showJson:
          result = Result(sourceName, result, location)
      else:
          result = Result(sourceName, "[" + sourceName + "] " + result, location)
      results.append(result)

      # Insert the result into the databasef
      cur.execute("INSERT INTO Results VALUES (?, ?, ?)",
                (result.Source, result.URL, result.Location))
      conn.commit()
    #   print(result.URL, "\n\n")
# conn.close()

if __name__ == "__main__":
    main()


