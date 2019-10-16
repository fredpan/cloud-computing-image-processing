// function init(){
//     console.log("inited");
//     var form = document.getElementById("register");
//         form.addEventListener("submit", event =>{
//         event.preventDefault();
//         var noErr = true;
//         // get all the inputs within the submitted form
//         var inputs = form.getElementsByClassName('field');
//         for (var i = 0; i < inputs.length; i++) {
//             // only validate the inputs that have the required attribute
//             if(inputs[i].value === ""){
//                 // found an empty field that is required
//                 alert("Please fill all required fields");
//                 noErr = false;
//             }
//         }
//         if (noErr) {
//             form.submit();
//         }
//     }, false);
// }
// //window.addEventListener("load", init, false);