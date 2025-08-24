function voteComment(commentId, vote) {
    fetch('/api/comment/vote/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            comment_id: commentId,
            vote: vote
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log("Ответ сервера:", data);
            // console.log("Ответ сервера data.likes:", data.likes);
            if (data.success) {
                // location.reload(); // обновляем страницу и видим новые счётчики
                // обновляем только цифры под конкретным комментарием
                document.querySelector(`#likes-${commentId}`).textContent = data.likes;
                document.querySelector(`#dislikes-${commentId}`).textContent = data.dislikes;
            } else {
                alert(JSON.stringify(data, null, 2));

            }
        })
        // если сервер недоступен
        .catch(error => {
            alert("Ошибка запроса: " + error);
        });
}

function voteSnippet(snippetId, vote) {
    fetch('/api/snippet/vote/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            snippet_id: snippetId,
            vote: vote
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log("Ответ сервера Snippet:", data);
            if (data.success) {
                // location.reload(); // обновляем страницу и видим новые счётчики
                // обновляем только цифры под конкретным snippet
                document.querySelector(`#likes-${snippetId}`).textContent = data.likes;
                document.querySelector(`#dislikes-${snippetId}`).textContent = data.dislikes;
            } else {
                alert(JSON.stringify(data, null, 2));

            }
        })
        // если сервер недоступен
        .catch(error => {
            alert("Ошибка запроса: " + error);
        });
}