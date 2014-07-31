function checkPath(){
    /* Get the current directory name */
    var curPath = document.location.pathname;
    var locarray = curPath.split("/");
    curDir = locarray[locarray.length-2];
    if (curDir !== 'latest'){
        /* current directory name is not 'latest'.
           So remove the link to previous archieve. */
        document.getElementById("archdate").innerHTML="Previous Archive Not Available";
        }
}
/* Calling the above function while loding the page */
window.onload = checkPath;
