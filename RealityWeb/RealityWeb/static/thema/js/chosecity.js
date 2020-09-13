console.log('hello world')

$(document).on("click", "a", function() {
    if($(this).attr("targetLink")=="yes"){
        document.cookie = "city="+$(this).attr("targetCity");
        console.log(document.cookie)
    }
});

