/**
 * Run.js
 * Run this in the console on http://na5b.com:8901/
 * Enable multiple download from browser if the browser asks
 */
function init() {
    setband(2);
    set_mode('usb');
    setmf('usb', 0.29, 2.00);
    rememberpreset();
    setfreqif(7038.6);
    wfset(2);
}
function delay() {
    const now = new Date();
    const min = now.getMinutes();
    const sec = now.getSeconds();
    return ((1 - (min % 2))*60 + (60-sec))*1000;
};
function restartRecord() {
    document.querySelector("#recbutton").click();
    console.log("Downloading recording at: ", new Date());
    document.querySelector("#reccontrol>a")?.click();
    startRecord();
}
function startRecord() {
    console.log("Starting recording at: ", new Date());
    document.querySelector("#recbutton").click();
    restartTimer = setTimeout(restartRecord, delay());
};
init();
let restartTimer;
let initTimer = setTimeout(startRecord, delay());