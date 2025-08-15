const messagesContainer = document.getElementById("alertsFixedContainer");
const messages = messagesContainer.querySelectorAll('div');

function deleteMessage(message){
    message.remove();
}

function deleteMessages(){
    let step = 800;
    let numMessage = 0;
    for (let message of messages){
        setTimeout(deleteMessage,2000 + step*numMessage, message);
        console.log(`${numMessage}`)
        numMessage++;
    }
}

deleteMessages();


// document.addEventListener("DOMContentLoaded", function () {
//     // Найти все алерты Bootstrap
//     const alerts = document.querySelectorAll(".alerts-fixed-container .alert");
//
//     // Через 5 секунд закрыть каждый
//     setTimeout(() => {
//         alerts.forEach(alert => {
//             const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
//             bsAlert.close();
//         });
//     }, 3000);
// });
