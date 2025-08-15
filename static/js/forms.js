const code = document.getElementById("id_code");
const charCount = document.getElementById("charCount");

code.addEventListener('input', () =>{
    const count = code.value.length;
    let text = `${count}/5000`
    charCount.innerHTML = text;
})

