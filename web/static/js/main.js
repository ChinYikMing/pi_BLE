function getPeopleCounter(elem, url){
  setInterval(async function(){
    const response = await fetch(url);
    const text = await response.text();
    console.log(text)
    //elem.textContent = text;
  }, 1000);     
}
