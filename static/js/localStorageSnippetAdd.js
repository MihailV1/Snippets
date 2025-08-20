// Находим форму
// const form = document.querySelector('form[action="/snippets/add"]');
const form = document.getElementById("addForm") || document.getElementById("editForm");

// Поля формы
const nameField = document.getElementById("id_name");
const publicCheck = document.getElementById("id_public");
const langSelector =document.querySelector('select[name="lang"]')
const descriptionField = document.getElementById("id_description");
const codeField = document.getElementById("id_code");

// Кнопка для очистки черновика
const clearButton = document.createElement("button");
clearButton.textContent = "Очистить черновик";
clearButton.type = "button";
clearButton.classList.add("btn", "btn-secondary", "mt-2");  //secondary warning
// form.appendChild(clearButton);

// Кнопка для восстановления черновика
const recoveryButton = document.createElement("button");
recoveryButton.textContent = "Восстановить черновик";
recoveryButton.type = "button";
recoveryButton.classList.add("btn", "btn-warning", "mt-2");  //secondary warning
// form.appendChild(recoveryButton);

let debounceTimer;
const draftKey = "snippetDraft_" + window.location.pathname;

// 🔹 Функция сохранения черновика
function saveDraft() {
    const draft = {
        name: nameField.value,
        publicCheck: publicCheck.checked,
        lang : langSelector.value,
        descriptionText: descriptionField.value,
        code: codeField.value,
    };
    localStorage.setItem("draftKey", JSON.stringify(draft));
    console.log("✅ Черновик сохранен");
}

// 🔹 Функция автосохранения (с debounce)
function startAutosave() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(saveDraft, 3000); // ждём 3 секунды после остановки ввода
}

// 🔹 Восстановление черновика
function loadDraft() {
    const draft = localStorage.getItem("draftKey");
    if (draft) {
        const draftData = JSON.parse(draft);
        nameField.value = draftData.name || "";
        publicCheck.checked = draftData.publicCheck || false;
        langSelector.value = draftData.lang || "";
        descriptionField.value = draftData.descriptionText || "";
        codeField.value = draftData.code || "";
        hideButtons();
        console.log("♻️ Черновик восстановлен");
    }
}

function hideButtons() {
    clearButton.style.display = "none";   // скрыть
    recoveryButton.style.display = "none";
}

// 🔹 Очистка черновика
function clearDraft() {
    localStorage.removeItem("snippetDraft");
    hideButtons();
    console.log("🗑️ Черновик удален");
}

// --- События ---
[nameField, publicCheck, langSelector, descriptionField, codeField].forEach(el => {
    el.addEventListener("input", startAutosave);
    el.addEventListener("change", startAutosave);
});

// Очистка черновика вручную
clearButton.addEventListener("click", clearDraft);
// Восстановление черновика вручную
recoveryButton.addEventListener("click", loadDraft);

// Очистка при отправке формы
if (form) {
    form.addEventListener("submit", () => {
        console.log("🚀 Форма отправлена!");
        clearDraft();
    });
}

// При загрузке страницы восстанавливаем черновик
// loadDraft();

if (localStorage.getItem("snippetDraft")) {
    form.appendChild(recoveryButton);
    form.appendChild(clearButton);
}


// // ищем именно по action или id
// const form = document.querySelector('form[action="/snippets/add"]');
//
// const nameField = document.getElementById("id_name");
// let previousNameField = nameField.value;
//
// const publicCheck = document.getElementById("id_public");
// let previousPublicCheck = publicCheck.checked;
//
// const descriptionField = document.getElementById("id_description");
// let previousDescriptionField = descriptionField.value;
//
// const codeField = document.getElementById("id_code");
// let previousCodeField = codeField.value;
//
// // const restoreButton = document.getElementById('restoreDraftBtn');
// // const rejectButton = document.getElementById('rejectDraftBtn');
//
// let autosaveInterval;
//
// function startAutosave() {
//     // Предотвращаем многократный запуск
//     if (autosaveInterval) {
//         return;
//     }
//
//     autosaveInterval = setInterval(() => {
//         // Сохраняем, только если есть изменения
//         if ((previousCodeField !== codeField.value) || (previousNameField !== nameField.value) ||
//             (previousPublicCheck !== publicCheck.checked) || (previousDescriptionField !== descriptionField.value)) {
//             const draft = {
//                 name: nameField.value,
//                 publicCheck: publicCheck.checked,
//                 description: descriptionField.value,
//                 code: codeField.value,
//             };
//             localStorage.setItem('snippetDraft', JSON.stringify(draft));
//             console.log('Черновик сохранен.');
//         }
//     }, 10000);
// }
//
// function stopAutosave() {
//     if (autosaveInterval) {
//         clearInterval(autosaveInterval);
//         autosaveInterval = null; // Обнуляем таймер
//         console.log('Автосохранение остановлено.');
//     }
// }
//
// function clearDraft() {
//     localStorage.removeItem('snippetDraft');
// }
//
// function loadDraft() {
//     const draft = localStorage.getItem('snippetDraft');
//     if (draft) {
//         const draftData = JSON.parse(draft);
//
//         nameField.value = draftData.name;
//         publicCheck.checked = draftData.publicCheck;
//         descriptionField.value = draftData.description;
//         codeField.value = draftData.code;
//         clearDraft()
//         alert('Черновик восстановлен.');
//
//     }
// }
//
// // Запускаем автосохранение при вводе в любое из полей
// codeField.addEventListener('input', startAutosave);
// nameField.addEventListener('input', startAutosave);
// publicCheck.addEventListener('change', startAutosave);
// descriptionField.addEventListener('input', startAutosave);
//
// if (form) {
//     form.addEventListener("submit", function (event) {
//         console.log("🚀 Форма отправлена!");
//         stopAutosave();
//         clearDraft();
//     });
// }
//
//
// // Запускаем проверку при загрузке страницы
// loadDraft();

