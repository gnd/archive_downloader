# Archive_downloader
A node.js book downloader from Archive.org

# Install
For downloading borrowed books from Archive.org you will first need:

```
apt-get install npm
npm install sleep
npm install request
```

To convert and OCR the downloaded images into a pdf with make_pdf.sh you will also need:

```
apt-get install imagemagick tesseract-ocr poppler-tools
```

## Downloading a book:
0. Install EditThisCookie for Chrome, or use something else for cookie extraction
1. Login to archive.org
2. Borrow a book
3. Copy your cookies:
  - In EditThisCookie options, first set the preferred export format to 'Semicolon separated name=value pairs'
  - Click export and paste just the cookies (without comments) into the ```cookies = '';``` in the node_dl.js
  - If you are using another way to retrieve your cookies, just put your cookies into the cookies variable in node_dl.js
  - Set other variables like ```ua``` (user-agent), ```pages``` (how many pages the book has), ```local_name``` (where to download and how to name the files)
4. You might want to create a directory for the files, eg. ```books/my_book```. In that case the local_name should be ```books/my_book/book_name```
5. Run ```node node_dl.js```

## Converting downloaded files into searchable OCR'ed pdf:
0. Run ```make_pdf.sh books/my_book output_name```
1. This will convert all jp2 files in the folder ```books/my_book``` into jpg's, OCR those jpg files and output into separate pdfs and finally join all pdfs into ```output_name.pdf```
