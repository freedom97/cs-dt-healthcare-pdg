
var title = document.getElementById("titleCharts");
var containerTitle = document.getElementById("titleCharts");
var im = document.getElementById("loadingScheme");

function showWeight(){
    im.style.display = "none";
    containerTitle.style.backgroundColor= document.getElementById("weght").style.backgroundColor;
    document.getElementById("HRate").style.display = "none";
    document.getElementById("nrStp").style.display = "none";
    document.getElementById("weght").style.display = "block";
    document.getElementById("foods").style.display = "none";
    document.getElementById("fdChr").style.display = "none";
    document.getElementById("HBigD").style.display = "none";
    title.textContent ="Peso";
    getDataFitbitWeight("sum text Weight");
}
function showHR(spectrum){    
    im.style.display = "none";
    containerTitle.style.backgroundColor= document.getElementById("HRate").style.backgroundColor;
    if ( spectrum == 'month'|| spectrum =='week') {
    document.getElementById("HRate").style.display = "none";
    document.getElementById("HBigD").style.display = "block";}
    else{
    document.getElementById("HBigD").style.display = "none";
    document.getElementById("HRate").style.display = "block";}
    document.getElementById("nrStp").style.display = "none";
    document.getElementById("weght").style.display = "none";
    document.getElementById("foods").style.display = "none";
    document.getElementById("fdChr").style.display = "none";
    title.textContent ="Actividad Cardiaca";
    getDataFitbitCharts("HR",spectrum);
}
function showSteps(spectrum){
    im.style.display = "none";
    containerTitle.style.backgroundColor= document.getElementById("nrStp").style.backgroundColor;
    document.getElementById("HRate").style.display = "none";
    document.getElementById("nrStp").style.display = "block";
    document.getElementById("weght").style.display = "none";
    document.getElementById("foods").style.display = "none";
    document.getElementById("fdChr").style.display = "none";
    document.getElementById("HBigD").style.display = "none";
    title.textContent ="Pasos";
    getDataFitbitCharts("ST",spectrum);
}
function showFood(spectrum){
    im.style.display = "none";
    containerTitle.style.backgroundColor= document.getElementById("foods").style.backgroundColor;
    if ( spectrum == 'month') {
    document.getElementById("fdChr").style.display = "block";
    document.getElementById("HRate").style.display = "none";
    document.getElementById("nrStp").style.display = "none";
    document.getElementById("weght").style.display = "none";
    document.getElementById("foods").style.display = "none";
    document.getElementById("HBigD").style.display = "none";
    getDataFitbitFoodsChart("alers",spectrum); 
    } else {
    document.getElementById("fdChr").style.display = "none";
    document.getElementById("HRate").style.display = "none";
    document.getElementById("nrStp").style.display = "none";
    document.getElementById("weght").style.display = "none";
    document.getElementById("foods").style.display = "block";
    document.getElementById("HBigD").style.display = "none"; q
    getDataFitbitFoods("alers",spectrum);    
    }
    title.textContent ="Comidas";
}

