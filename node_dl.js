/*
This uses node.js to download images from borrowed Archive.org books

Instalation:
- install node.js
- install request and sleep (eg. npm install request sleep)

How to save a book:
- request the book
- login in your fav browser and start reading the book
- copy your cookies into the script
- fill out the rest of the globals
- run like: node node_dl.js


gnd, 2018, initial impulse by db @ mnskp
*/

/* GLOBALS */
// the actual url of the archive.org server, get it from the html source when reading the book
var url_stub = 'https://ia601900.us.archive.org/BookReader/BookReaderImages.php?zip=/19/items/ARes22722/ARes22722_jp2.zip&file=ARes22722_jp2/ARes22722_0'
// copy your cookies when reading the book, use a plugin like HTTP Headers (or EditThisCookie) for Chrome,
var cookies = ''
// how many pages to download
var pages = 10
// how should the images be called
var local_name = 'aristophanes'
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
    var padding_a = "";
    var padding_b = "";
    if (i < 10) {
        padding_a = "0";
    }
    if (i < 100) {
        padding_b = "0";
    }
    var url = url_stub + padding_a + padding_b + i + ".jp2&scale=2&rotate=0";
    var options = {
        url: url,
        headers: {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cookie': cookies
        }
    };
    var filename = local_name + i + ".jp2";
    download(options, filename, function() {
        console.log('Image downloaded');
    });
    sleep.msleep(sleep_ms);
}
