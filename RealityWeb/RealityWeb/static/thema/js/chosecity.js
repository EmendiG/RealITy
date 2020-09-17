// console.log('hello world')

$(document).on("click", "a", function() {
    if($(this).attr("targetLink")=="yes"){
        document.cookie = "city="+$(this).attr("targetCity");
        console.log(document.cookie)
    }
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

