function showForm(id){
    if(document.getElementById(id+'_1')) {
        document.getElementById(id+'_1').style.display = "block";
        document.getElementById(id+'_2').style.display = "block";
    }
}

function hideForm(id){
    if(document.getElementById(id+'_1')) {
        document.getElementById(id+'_1').style.display = "none";
        document.getElementById(id+'_2').style.display = "none";
    }
}
