// // Функция для копирования текста с использованием промисов
// function copyToClipboard(text) {
//     if (!navigator.clipboard) {
//         // Если API недоступно, выводим ошибку
//         alert('API буфера обмена недоступно в этом браузере.');
//         return;
//     }
//
//     // Вызываем writeText(), который возвращает промис
//     navigator.clipboard.writeText(text)
//         .then(function () {
//             // Этот код выполнится, если промис разрешился (успешное копирование)
//             // alert('Текст успешно скопирован!');
//             let btn = document.querySelector('.copy-button');
//             btn.classList.add('copied'); // меняем иконку на ✅
//
//             // Вернуть обратно через 2 секунды
//             setTimeout(() => btn.classList.remove('copied'), 3000);
//         })
//         .catch(function (err) {
//             // Этот код выполнится, если промис был отклонён (ошибка копирования)
//             // console.error('Ошибка копирования:', err);
//             // alert('Не удалось скопировать текст. Проверьте консоль.');
//             let btn = document.querySelector('.copy-button');
//             btn.classList.add('copied'); // меняем иконку на ❌
//
//             // Вернуть обратно через 2 секунды
//             setTimeout(() => btn.classList.remove('copied'), 3000);
//         });
// }
//
// // Функция для копирования текста из поля ввода
// function copyFromInput() {
//     const input = document.getElementById('codeSnippet');
//     copyToClipboard(input.value);
// }


/////////////////

function copyToBuffer(text) {
    navigator.clipboard.writeText(text)
        .then(function () {
            // Этот код выполнится, если промис разрешился (успешное копирование)
            let btn = document.querySelector('.copy-button');
            btn.classList.add('copied'); // меняем иконку на ✅
            // Вернуть обратно через 3 секунды
            setTimeout(() => btn.classList.remove('copied'), 3000);
            console.log('Текст успешно скопирован!');
        })
        .catch(function (err) {
            let btn = document.querySelector('.copy-button');
            btn.classList.add('copied'); // меняем иконку на ❌
            // Вернуть обратно через 3 секунды
            setTimeout(() => btn.classList.remove('copied'), 3000);
            // Этот код выполнится, если промис был отклонён (ошибка копирования)
            console.error('Ошибка копирования:', err);
        });
}

