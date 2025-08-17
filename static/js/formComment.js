const code = document.getElementById("commentText");
const charCount = document.getElementById("charCount");
const buttonComment = document.getElementById("buttonCom");

// При загрузке страницы делаем кнопку неактивной
buttonComment.disabled = true;

code.addEventListener('input', () =>{
    const count = code.value.length;
    if (count === 0 || 500 < count){
         buttonComment.disabled = true;
    } else {
        buttonComment.disabled = false;
    }
    let text = `${count}/500`
    charCount.innerHTML = text;
})
