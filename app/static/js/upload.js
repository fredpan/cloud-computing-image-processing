var submitbtn;

window.addEventListener("load", event=>{
    submitbtn = document.getElementById("upload_file_btn");
    submitbtn.addEventListener("click", ev => {
        var size = document.getElementById("upload_file").files[0].size;
        if (size >= 1024*1024*2){
            ev.preventDefault();
            alert("File too big!")
        } else {
            return true
        }
    }, false);
}, false);