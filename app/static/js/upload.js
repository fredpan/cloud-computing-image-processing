var submitbtn;

window.addEventListener("load", event=>{
    submitbtn = document.getElementById("upload_file_btn");
    submitbtn.addEventListener("click", ev => {
        //ev.preventDefault();
        var size = document.getElementById("upload_file").files[0].size;
        if (size >= 1024*1024*5){
            alert("File too big!")
        }
    }, false);
}, false);