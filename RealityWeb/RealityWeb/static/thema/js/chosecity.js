// console.log('hello world')
var ploty_width
ploty_width = window.screen.width * window.devicePixelRatio;
var ploty_height
ploty_height = window.screen.height * window.devicePixelRatio;

$(document).on("click", "a", function() {
    if($(this).attr("targetLink")=="yes"){
        document.cookie = "city="+$(this).attr("targetCity");
        document.cookie = "my_width="+$(window).width();;
        document.cookie = "my_height="+$(window).height();
    }
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

