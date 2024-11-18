import os
import re
import requests

def find_urls(text):
    # Updated regex to match valid URLs
    url_pattern = re.compile(r'http[s]?://[^\s<]+')
    return url_pattern.findall(text)

def clean_url(url):
    # Remove unwanted characters at the end of the URL
    url = url.split('>')[0]  # Remove everything after '>'
    url = url.split('<')[0]  # Remove everything after '<'
    url = url.split('&')[0]  # Remove everything after '&'
    url = url.split(';')[0]   # Remove everything after ';'
    url = url.split('"')[0]   # Remove everything after '"'
    url = url.split("'")[0]   # Remove everything after "'"
    url = url.split(')')[0]   # Remove everything after ')'
    url = url.split('(')[0]   # Remove everything after '('
    url = url.split(']')[0]   # Remove everything after ']'
    url = url.split('}')[0]   # Remove everything after '}'
    url = url.split(',')[0]   # Remove everything after ','
    url = url.split(' ')[0]   # Remove everything after ' '
    url = url.split('\n')[0]  # Remove everything after newline
    url = url.split('\r')[0]  # Remove everything after carriage return
    url = url.split('\t')[0]  # Remove everything after tab
    url = url.split('!')[0]   # Remove everything after '!'
    url = url.strip()  # Remove leading/trailing whitespace
    return url

def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        print(f"Checked URL: {url} - Status Code: {response.status_code}")
        return response.status_code
    except requests.RequestException as e:
        print(f"Error checking URL: {url} - Exception: {e}")
        return None  # Return None for any request exception

def check_broken_links_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        urls = find_urls(content)
        # Clean URLs to ensure proper format
        cleaned_urls = [clean_url(url) for url in urls]
        print(f"Found cleaned URLs in {file_path}: {cleaned_urls}")  # Debugging output
        broken_links = []
        for url in cleaned_urls:
            status_code = check_url(url)
            if status_code == 404:
                broken_links.append(url)
        return cleaned_urls, broken_links

def check_broken_links_in_directories(directories):
    broken_links_report = {}
    total_links_checked = 0
    total_broken_links = 0
    total_working_links = 0
    total_folders_checked = 0

    for directory in directories:
        print(f"Scanning directory: {directory}")  # Indicate which directory is being scanned
        total_folders_checked += 1  # Count the folder being checked
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.html', '.md', '.txt', '.py', '.js', '.rst', '.css')):
                    file_path = os.path.join(root, file)
                    cleaned_urls, broken_links = check_broken_links_in_file(file_path)
                    total_links_checked += len(cleaned_urls)
                    total_broken_links += len(broken_links)
                    total_working_links += (len(cleaned_urls) - len(broken_links))
                    if broken_links:
                        for url in broken_links:
                            broken_links_report[(directory, url)] = 404  # Store broken links with their directory

    return broken_links_report, total_links_checked, total_broken_links, total_working_links, total_folders_checked

if __name__ == "__main__":
    # List of directories to scan
    directories_to_scan = [
        '../docs/build/',  # Add additional paths as needed
        '../docs/source/',  # Example additional directory
        '../src/scribe_data/'  # Example additional directory
    ]
    
    report, total_links_checked, total_broken_links, total_working_links, total_folders_checked = check_broken_links_in_directories(directories_to_scan)

    # Print the report of broken links
    if report:
        print("\nBroken Links Report:")
        print(f"{'Folder':<30} {'URL':<60} {'Status':<10} {'Code'}")
        for (folder, url), code in report.items():
            print(f"{folder:<30} {url:<60} {'broken':<10} {code}")
    else:
        print("No broken links found.")

    # Print summary statistics
    print("\nStatistics:")
    print(f"Total links checked: {total_links_checked}")
    print(f"Total broken links: {total_broken_links}")
    print(f"Total working links: {total_working_links}")
    print(f"Total folders checked: {total_folders_checked}")
