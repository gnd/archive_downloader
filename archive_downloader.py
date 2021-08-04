import os
import re
import sys
import json
import time
import argparse
import configparser
import requests

# Some globals
TIMEOUT = 30                    # timeout connection after 30 seconds
MAX_ERRORS = 10                 # how many times can the download fail in order for the downloader to stop
MIN_RESPONSE_SIZE = 5000        # if response size under 5000, we are not getting real data

# Some default values
START_PAGE = 0                  # default start page is 0
DEFAULT_VERBOSE = 0             # by default verbose is off
DEFAULT_SLEEP_INTERVAL = 100    # default sleep interval

# 
# This object will be used to store input params
#
class class_params:
    cookies = ""
    user_agent = ""
    book_url = ""
    end_page = ""
    start_page = START_PAGE
    download_dir = ""
    sleep_interval = DEFAULT_SLEEP_INTERVAL 
    verbose = DEFAULT_VERBOSE
    
    def __init__(self, cookies, user_agent, book_url, start_page, end_page, download_dir, sleep_interval, verbose): 
        self.cookies = cookies
        self.user_agent = user_agent
        self.book_url = book_url
        self.start_page = start_page
        self.end_page = end_page
        self.download_dir = download_dir
        self.sleep_interval = sleep_interval
        self.verbose = verbose

#
# This oject will be used to store book info gathred from archive.org
#
class class_book_info:
    book_id = ""
    book_path = ""
    image_format = ""
    server = ""
    
    def __init__(self, book_id, book_path, image_format, server):
        self.book_id = book_id
        self.book_path = book_path
        self.image_format = image_format
        self.server = server
        
    def __str__(self):
        return "\nbook_info is:\n - book_id: {}\n - book_path: {}\n - image_format: {}\n - server: {}\n".format(
            self.book_id, 
            self.book_path,
            self.image_format,
            self.server)

# 
# This function processes the input parameters
# The prameters are taken either all from the command line or all from th config file
# 
# After getting the params, the function checks for pramater sanity
#
def process_input_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config_file", help="Configuration file. If set, other command line parameters will be ignored")
    parser.add_argument("-c", "--cookies", help="Browser cookies after borrowing the book")
    parser.add_argument("-u", "--user_agent", help="Browser User-Agent string")
    parser.add_argument("-b", "--book_url", help="The url where the book was borrowed")
    parser.add_argument("-s", "--start_page", help="Start from page", type=int)
    parser.add_argument("-p", "--end_page", help="How many pages to download", type=int)
    parser.add_argument("-d", "--download_dir", help="Absolute path to the dir where the images will be downloaded")
    parser.add_argument("-i", "--sleep_interval", help="How long to sleep between requests", type=int, default=DEFAULT_SLEEP_INTERVAL)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true", default=DEFAULT_VERBOSE)
    args = parser.parse_args()
    
    if (args.config_file):
        print("Config file set. Reading all parameters from the config file {}".format(args.config_file))
        mode = "config file"
        #settings_file = os.path.join(sys.path[0], args.config_file)

        config = configparser.ConfigParser(interpolation=None)
        config.read(args.config_file)
        cookies = config.get('browser_data', 'cookies').strip(';')
        user_agent = config.get('browser_data', 'user_agent')
        book_url = config.get('book_data', 'book_url')
        start_page = int(config.get('book_data', 'start_page'))
        end_page = int(config.get('book_data', 'end_page'))
        download_dir = config.get('globals', 'download_dir').rstrip('/')
        sleep_interval = int(config.get('globals', 'sleep_interval'))
        verbose = int(config.get('globals', 'verbose'))
    else:
        print("No config file set. Expecting all parameters from command line.")
        mode = "command line"
        cookies = args.cookies
        user_agent = args.user_agent
        book_url = args.book_url
        start_page = args.start_page
        end_page = args.end_page
        download_dir = args.download_dir
        sleep_interval = args.sleep_interval
    
    # allow command line verbose to override config_file verbose
    verbose = args.verbose
        
    # do some simple sanity checks
    if cookies == None:
        print("Error: No cookies provided via the {}. Exiting.".format(mode))
        sys.exit()
    if user_agent == None:
        print("Error: No user_agent provided via the {}. Exiting.".format(mode))
        sys.exit()
    if book_url == None:
        print("Error: No book_url provided via the {}. Exiting.".format(mode))
        sys.exit()
    if end_page == None:
        print("Error: No end_page provided via the {}. Exiting.".format(mode))
        sys.exit()
    if download_dir:
        if (not os.path.exists(download_dir)):
            print("Error: download_dir {} provided via the {} doesn't exist. Exiting.".format(download_dir, mode))
            sys.exit()
    else:
        print("No download_dir set. Downloading into the local directory.   ")
        
    # make sure the book_url doesn't already contain page
    if ("page" in book_url):
        if verbose:
            print("Removing page from book_url")
        book_url = re.sub(r'/page\/[0-9]+', '', book_url)
        
    # remove trailing ; from cookies
    cookies = cookies.strip(';')
    
    # remove trailing / from download_dir
    download_dir = download_dir.rstrip('/')
        
    # create and return params object
    return class_params(cookies, user_agent, book_url, start_page, end_page, download_dir, sleep_interval, verbose)

#
# a simple helper function that uses Python's requests to get HTML data from a url
#
def simple_get_url(url):
    response = requests.get(url, timeout=TIMEOUT)
    return response.text

#    
# This function accesses the book's page on archive.org
# and serches for a url stub that looks similar to this one:
# //ia801703.us.archive.org/BookReader/BookReaderJSIA.php?id=somebookid000herp&itemPath=/10/items/somebookid000herp&server=ia801703.us.archive.org&format=jsonp&subPrefix=somebookid000herp&requestUri=/details/somebookid000herp/mode/2up'
# we call this url the reader_url later on
#
def extract_reader_url(url, verbose):
    print("Extracting reader_url..")
    reader_url = ""
    
    html = simple_get_url(url)
    for line in html.split():
        if 'BookReaderJSIA.php' in line:
            reader_url = line.strip("'")
    print("reader_url extracted")
    if verbose:
        print("\nreader_url is:\n" + reader_url)
    return reader_url

#
# This function accesses the reaader_url of the book and gets some additional
# information about the book. In general we are interested in:
#   - book_id
#   - book_path
#   - image_format
#   - server
#
# These data can be used later on to construct the "image_url" where we can
# access the image of individual pages:
#    
def extract_book_info(url, verbose):
    print("Extracting book_info..")
    
    html = simple_get_url('https:' + url)
    reader_json = json.loads(html)
    book_id = reader_json['data']['brOptions']['bookId']
    book_path = reader_json['data']['brOptions']['bookPath']
    image_format = reader_json['data']['brOptions']['imageFormat']
    server = reader_json['data']['brOptions']['server']
    book_info = class_book_info(book_id, book_path, image_format, server)
    print("book_info extracted")
    
    if verbose:
        print("\nFirst 20 items from reader_url:")
        print(html.split(',')[0:20])
        print(book_info)
        
    return book_info
    
#
# This function uses data extracted from the reader_url to compose the "image_url"
# where we can download individual pages
#
# we need sth like this:
# https://ia601703.us.archive.org/BookReader/BookReaderImages.php?zip=/10/items/somebookid000herp/somebookid000herp_jp2.zip&file=somebookid000herp_jp2/somebookid000herp_0011.jp2&id=somebookid000herp&scale=4&rotate=0
#
def create_image_url(book_info, verbose):
    image_url = "https://{server}/BookReader/BookReaderImages.php?zip={book_path}_{image_format}.zip&file={book_id}_{image_format}/{book_id}_PAGENUMBER.{image_format}&id={book_id}&scale=4&rotate=0".format(
        server = book_info.server,
        book_path = book_info.book_path, 
        image_format = book_info.image_format, 
        book_id = book_info.book_id
    )
    
    if verbose:
        print("image_url is:\n{}".format(image_url))
    
    return image_url
    
def extract_cookies(cookie_jar, domain):
    cookie_dict = cookie_jar.get_dict(domain=domain)
    found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
    return ';'.join(found)
    
def get_book_page(image_url, params, page_index):
    print("* Downloading page {} .. ".format(page_index), end="")
    
    # without a correct referer header archive will deauth the session
    referer_page_index = 0
    if (page_index > 6):
        referer_page_index = page_index - 6
    referer = params.book_url.replace("mode", "page/{}/mode".format(referer_page_index))
    if params.verbose:
        print("referer is:\n{}".format(referer))
        
    # replace PAGENUMBER with page_index
    image_url = image_url.replace("PAGENUMBER", "{:04}".format(page_index))
    
    # prepare request headers
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'User-Agent': params.user_agent,
        'Cookie': params.cookies,
        'Referer': referer
    }
    if params.verbose:
        print("Setting request headers: ")
        print(headers)
        
    # try and get the data
    try:
        # timeout is set to 30 seconds
        response = requests.get(image_url, headers=headers, timeout=TIMEOUT)
        error = None
    except requests.exceptions.RequestException as e:
        response = ''
        error = e
        
    return (response, error)
    
def save_page(download_dir, page_index, page):
    page_file = download_dir + "/" + "page_{:04}.jp2".format(page_index)
    print("* Saving page to {}".format(page_file))
    file = open(page_file, "wb")
    file.write(page)
    file.close()

def main():
    # process input parameters
    params = process_input_params()
        
    # get the general book page first
    reader_url = extract_reader_url(params.book_url, params.verbose)
            
    # get book info from the reader_url
    book_info = extract_book_info(reader_url, params.verbose)

    # create url of page image files
    image_url = create_image_url(book_info, params.verbose)

    # get individual pages of the book
    errors = 0
    start_time = time.time()
    bytes_downloaded = 0
    
    
    #for page_index in range(params.start_page, params.end_page):
    page_index = params.start_page
    for (attempt in RANGE(MAX_TRIES)):
        # if we reached MAX_TRIES, stop the download
        if (attempt == MAX_TRIES-1):
            sys.exit("Max tries reached. Exiting.")
            
        (response, error) = get_book_page(image_url, params, page_index)
        
        # if no error - process and save the data
        if (error is None):
            cookies = extract_cookies(response.cookies, ".archive.org")
            length = len(response.content)
            bytes_downloaded += length
            duration = time.time() - start_time
            if (page_index > 0):
                time_per_page = duration / page_index
            else: time_per_page = 0
            pages_per_minute = page_index / (duration / 60)
            bytes_per_minute = bytes_downloaded / (duration / 60)
            
            # TODO - remove after testing
            print("* Total bytes: {}, Total duration: {:0.0f}s, Time per page: {:0.2f}s, Pages per minute: {:0.2f}, Bytes per minute: {:0.0f}".format(
                bytes_downloaded, 
                duration, 
                time_per_page,
                pages_per_minute,
                bytes_per_minute))
            if (cookies != ''):
                print("Cookies returned: {}".format(cookies))
                
            # check if size big enough
            if (length > MIN_RESPONSE_SIZE):
                print("OK. {} bytes received".format(length))
                if (page_index+1 <= params.end_page):
                    page_index += 1
                    break
                else:
                    # C'est fini
                    print("\nDone. Downloaded pages {}..{}".format(params.start_page, params.end_page))
            else:
                print("NOT OK. Response size too small: {} bytes".format(length))
                print("Will try again.")
            
            # save image file and advance to next page
            save_page(params.download_dir, page_index, response.content)
            
        # otherwise - report error
        else:
            print("Error while downloading page {}:".format(page_index))
            print(str(error))
            
        # show some debug info
        if params.verbose:
            print("* Cookies returned: {}".format(cookies))
            print("* Response size: {}".format(length))    
            print("* Total size: {}".format(bytes_downloaded))

# Run archive_downloader
if __name__ == "__main__":
    main()
