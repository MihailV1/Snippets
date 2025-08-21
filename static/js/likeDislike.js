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
            if (data.success) {
                // location.reload(); // обновляем страницу и видим новые счётчики
                // обновляем только цифры под конкретным комментарием
                document.querySelector(`#likes-${commentId}`).textContent = data.likes;
                document.querySelector(`#dislikes-${commentId}`).textContent = data.dislikes;
            } else {
                alert(data.message);
            }
        });
}