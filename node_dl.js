/*
This uses node.js to download images from borrowed Archive.org books

Instalation:
- install node.js
- install request and sleep (eg. npm install request sleep)

How to save a book:
- request the book
- login in your fav browser (make sure you are not using any proxy or VPN for that) and start reading the book
- copy your cookies into the script
    - you can use the extension EditThisCookie in Chrome. In Options of the extension first set the preffered export format to be 'Semicolo separated name=value pairs'
    - export the cookies and just copy the into this file
- fill out the rest of the globals, eg. user agent and number of pages
- run like: node node_dl.js

gnd, 2018-2019, initial impulse by db @ mnskp
*/

/* GLOBALS */
// the actual url of the archive.org server, get it from the html source when reading the book
var url_stub = 'https://ia902307.us.archive.org/BookReader/BookReaderImages.php?zip=/0/items/isbn_9780805067811/isbn_9780805067811_jp2.zip&file=isbn_9780805067811_jp2/isbn_9780805067811_'
// copy your cookies when reading the book, use a plugin like HTTP Headers (or EditThisCookie) for Chrome,
var cookies = '';
// copy your User-Agent here
var ua = 'Mozilla/5.0 (X11; Linux x86_64)';
// how many pages to download
var pages = 252
// how should the images be called
var local_name = 'books/life_death/life_death'
// how long to wait between requests (in ms)
var sleep_ms = 100


/* MAIN */
var fs = require('fs'),
    request = require('request'),
    sleep = require('sleep');

var download = function(options, filename, callback) {
    request(options).pipe(fs.createWriteStream(filename)).on('close', callback);
};

// check if cookies set
if (cookies === "") {
    console.log('No cookies set');
    process.exit();
}

// start download
for (var i = 1; i < pages + 1; i++) {
    var padding = ("000" + i).slice(-4)
    var url = url_stub + padding + ".jp2&scale=0&rotate=0";
    //console.log("Getting: " + url);
    var options = {
        url: url,
        headers: {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': ua,
            'Cookie': cookies
        }
    };
    var filename = local_name + '_' + padding + ".jp2";
    download(options, filename, function() {
        console.log('Image downloaded');
    });
    sleep.msleep(sleep_ms);
}
