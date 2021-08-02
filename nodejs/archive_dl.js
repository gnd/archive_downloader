/*
This uses node.js to download images from borrowed Archive.org books

Instalation:
- install node.js
- install request, sleep, readline-sync (eg. npm install request sleep readline-sync)

How to save a book:
- request the book
- login in your fav browser (make sure you are not using any proxy or VPN for that) and start reading the book
- copy your cookies into config.js
    - you can use the extension EditThisCookie in Chrome. In Options of the extension first set the preffered export format to be 'Semicolo separated name=value pairs'
    - export the cookies and just copy the into this file
- fill out the rest of the config.js, eg. user agent and number of pages
- run like: node archive_dl.js

gnd, 2018-2019, initial impulse by db @ mnskp

TODO: how did i start to code this in nodejs anyway ? async my ass..
TODO: rewrite in python
TODO: make sure filed download of images is noted and immediately retried
TODO: add a switch to manually redownload a single page or a range
*/

/* REQUIRES*/
var config = require('./config.json');
var fs = require('fs'),
    request = require('request'),
    sleep = require('sleep'),
    readline = require('readline-sync');

/* FUNCTIONS */
var download = function(options, filename, callback) {
    request(options).pipe(fs.createWriteStream(filename)).on('close', callback);
};

/* LOAD VARIABLES
    Check if all variables are set & eventually ask for values.
    Variables are setup in config.json (see config.json.orig for reference)
        - url_stub is the partial url to the borrowed book, eg:
            https://ia902307.us.archive.org/BookReader/BookReaderImages.php?zip=/0/items/isbn_9780805067811/isbn_9780805067811_jp2.zip&file=isbn_9780805067811_jp2/isbn_9780805067811_",
        - cookies are cookies exported from the browser that borrowed the book
        - ua is the User Agent string of your browser
        - pages is the amount of pages to be downloaded
        - local_name is the location & name of the downloaded .jp2 files
        - sleep_ms is how long should archive_dl wait between creating new sockets
        - batch_size is how many concurrent connections are allowed
*/
if (config.url_stub === "") {
    console.log('No url_stub defined. Please set the value in config.json.');
    process.exit();
} else {
    console.log('Using url_stub: \n' + config.url_stub);
}
if (config.cookies === "") {
    console.log('No cookies defined. Please set the value in config.json');
    process.exit();
} else {
    console.log('Using cookies: \n' + config.cookies);
}
if (config.ua === "") {
    console.log('No User Agent defined. Please set the value in config.json');
    process.exit();
} else {
    console.log('Using user agent: ' + config.ua);
}
if (config.pages === "") {
    console.log('Number of pages not defined.');
    config.pages = parseInt(readline.question('Please provide the number of pages to download: '), 10);
    console.log(`Downloading ${config.pages} pages.`);
}
if (config.local_dir === "") {
    console.log('Location where to download images not provided.')
    config.local_dir = readline.question('Please provide the name of the directory where to download the images: ');
    console.log(`Downloading into ${config.local_dir}`)
}
if (!fs.existsSync(config.local_dir)) {
    console.log(`Directory ${config.local_dir} doesnt exist. Creating`)
    fs.mkdirSync(config.local_dir);
} else {
    console.log(`Directory ${config.local_dir} exists. Will overwrite any files in it`)
}
if (config.sleep_ms === "") {
    console.log('No sleep_ms defined. Please set the value in config.json');
    process.exit();
} else {
    console.log('Using delay: ' + config.sleep_ms + 'ms.');
}
if (config.batch_size === "") {
    console.log('No batch size defined. Please set the value in config.json');
    process.exit();
} else {
    console.log('Using batch size: ' + config.batch_size);
}

/* START DOWNLOAD */
for (var i = 1; i < config.pages + 1; i++) {
    var padding = ("000" + i).slice(-4)
    var url = config.url_stub + padding + ".jp2&scale=0&rotate=0";
    var req_pool = {maxSockets: config.batch_size};
    //console.log("Getting: " + url);
    var options = {
        url: url,
        pool: req_pool,
        headers: {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': config.ua,
            'Cookie': config.cookies
        }
    };
    var filename = config.local_dir + '/'  + 'page_' + padding + ".jp2";
    download(options, filename, function() {
        console.log('Image downloaded');
    });
    sleep.msleep(config.sleep_ms);
}
