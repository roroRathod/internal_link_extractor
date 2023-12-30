# README

This Python script is designed to crawl websites and save the results into a SQLite database. It uses the `requests` library to send HTTP requests and the `sqlite3` library to interact with the SQLite database.

## Features

- Parses command-line arguments to customize the behavior of the crawler.
- Extracts links, scripts, and forms from the HTML content of a webpage.
- Handles redirects and timeouts.
- Can filter results based on domain names.
- Can limit the size of the body of the HTTP responses.
- Can handle proxies.
- Stores the results in a SQLite database.

## Usage

To use this script, you need to pass URLs via stdin. Here's an example of how to use it:

```bash
cat url.txt | python crawler.py
```

or 

```bash
echo -e "http://example.com\nhttp://example2.com" | python crawler.py
```

This will make the script crawl `http://example.com` and `http://example2.com`.

## Command-Line Arguments

The script supports the following command-line arguments:

- `-i`: Crawls only the internal links of the website.
- `-t`: Specifies the number of threads to use.
- `-d`: Specifies the maximum depth of the crawl.
- `-size`: Limits the size of the HTTP response bodies.
- `-insecure`: Ignores SSL certificate errors.
- `-subs`: Allows crawling of subdomains.
- `-json`: Prints the results in JSON format.
- `-s`: Shows the source of each result.
- `-w`: Shows the location of each result.
- `-h`: Sets the headers of the HTTP requests.
- `-u`: Only shows unique results.
- `-proxy`: Sets the proxy to use for the HTTP requests.
- `-timeout`: Sets the timeout for the HTTP requests.
- `-dr`: Disables redirects.

## Database Structure

The script creates a SQLite database named `results.db` and a table named `Results`. The table has three columns: `Source`, `URL`, and `Location`. Each row represents a result found by the crawler.

- `Source`: The type of the result (e.g., `href`, `script`, `form`).
- `URL`: The URL of the result.
- `Location`: The location where the result was found.

## Dependencies

This script requires the following Python libraries:

- `requests`: For sending HTTP requests.
- `sqlite3`: For interacting with the SQLite database.
- `os`: For interacting with the operating system.
- `signal`: For handling signals.
- `re`: For regular expressions.
- `json`: For handling JSON data.
- `urllib.parse`: For parsing and manipulating URLs.
