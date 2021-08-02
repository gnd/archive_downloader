var fs = require('fs'),
    request = require('request'),
    sleep = require('sleep'),
    readline = require('readline-sync');

/* FUNCTIONS */
var download = function(options, filename, callback) {
    request(options).pipe(fs.createWriteStream(filename)).on('close', callback);
};

const https = require("https")
var cookie = "donation-identifier=792b3a5a97aedcd5ba62c2d554ef5b7b; abtest-identifier=3a18ed05a38e67beafe91b25de9267ac; test-cookie=1; G_ENABLED_IDPS=google; logged-in-sig=1659349772%201627813772%20xvAvYGLUBP1nQHYnrRV2%2BPaswDkrA20%2FKffzaXhCwwvHb536bnD9STMM76h998kFSSGmT77yVXEMl8jsEZ4JmG0ARO%2BgKX%2BHhzZLC0gK5H47bd1uxq9MN3XqLpU8qQ5341abMu98LJd2Tj4iiO4pUvPMPIAjgOMSMIi6BAdNF6k%3D; logged-in-user=gnd%40itchybit.org; collections=inlibrary; PHPSESSID=kqgf1qscuie40rpv324j1vm574; br-loan-burningveilnovel0000gran=1; ol-auth-url=%2F%2Farchive.org%2Fservices%2Fborrow%2FXXX%3Fmode%3Dauth; loan-burningveilnovel0000gran=1627847371-b4c0f579b310e53d57373e2b42709220";
var ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36";
var url = "https://ia601703.us.archive.org/BookReader/BookReaderImages.php?zip=/10/items/burningveilnovel0000gran/burningveilnovel0000gran_jp2.zip&file=burningveilnovel0000gran_jp2/burningveilnovel0000gran_0011.jp2&id=burningveilnovel0000gran&scale=4&rotate=0";
var options = {
    url: url,
    pool: {maxSockets: 1},
    headers: {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'User-Agent': ua,
        'Cookie': cookie,
        'Referer': 'https://archive.org/details/burningveilnovel0000gran/page/8/mode/2up'
    }
};

var filename = "test.jp2";
download(options, filename, function() {
    console.log('Image downloaded');
});