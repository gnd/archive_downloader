# Archive_downloader
A book downloader from Archive.org.

Formerly written in nodejs, now completely overwritten in Python.

# Install
For downloading borrowed books from Archive.org you will first need:

* A working install of Python 3
* Some additional Python packages

Install the additional packages like this:
```
pip install -r requirements.txt
```

Python should make this run on all platforms. I am too lazy to check if its truly so, and have only checked on Linux.

If you encounter any problems, feel free to open a issue. 

## Downloading a book:
1. Login to archive.org
2. Borrow a book and leave the browser open
3. Prepare some configuration variables:

    * You will need the URL of the book you want to get.
    This is the url where you are able to leaf through the book. It usually looks like this:
    
    `https://archive.org/details/somebookid0000derp/mode/2up`
    
    * You will need your cookies from archive.org.  
    You can extract them using plugins such as *EditThisCookie* for Chrome. Cookies should be a single string looking like this:
    
    `donation-identifier=764b3b6a97aedcd5ba62d2d666ef5b7b;abtest-identifier=3a18fd05a38e76deaff91b00b1337acab;test-cookie=1;etc;etc;etc`
    
    In *EditThisCookie* you can easily extract the cookies like this: 
      * First set in options of the extension the preferred export format to *Semicolon separated name=value pairs*
      * Then click on the *Export* icon and paste the cookies (without the comments) into the settings file or your command line.
    
    * Lastly you will need your browser's User-Agent. You can get it by visiting eg. http://my-user-agent.com/
    
    * You will also need the number of pages of the book and some other variables. See the settings file or command line parameters for more info:
    
    ```python archive_downloader -h```
    

4. Grab the latest source code of archive_downloader:

```
git clone https://github.com/gnd/archive_downloader.git
cd archive_downloader
```

5. Edit the settings and add configurations variables there. You can also provide them directly via the command line.

6. Run ```python archive_downloader -f settings.cfg```

# Converting a book into a searchable OCR'ed PDF

You can additionally use the script make_pdf.sh to convert and OCR the downloaded images into a pdf.

Please note this script runs only on Linux (and maybe Mac).

You will need:

```
apt-get install git imagemagick tesseract-ocr poppler-utils
```

To create the PDF you should run:

```
./make_pdf.sh /path/to/directory/with/images output_name
```

This will:
- convert all jp2 files in the folder `/path/to/directory/with/images` into jpegs
- OCR the jpegs with tesseract
- output the text into separate pdf's 
- and finally join all pdfs into `output_name.pdf`

I haven't tested this for a while now so again, feel free to open an issue if something doesn't work.