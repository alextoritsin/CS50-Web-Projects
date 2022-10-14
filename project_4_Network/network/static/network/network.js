document.addEventListener('DOMContentLoaded', () => {

    // add event listeners to all like icons
    document.querySelectorAll('i').forEach(e => {
        e.addEventListener('click', () => changeLikes(e));
    })

    // managing followers
    const button = document.querySelector('button.follow')
    if (button) {
        button.addEventListener('click', event => manageFollow(event.currentTarget));
    }

    // post content editing
    document.querySelectorAll('div.edit').forEach(e => {
        e.addEventListener('click', () => postEditing(e.parentNode));
    })
});

// get CSRF token cookie
// https://docs.djangoproject.com/en/4.0/ref/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// changing likes count
function changeLikes(element) {

    // define the action: was it like or dislike
    const is_liked = element.className == 'bi bi-heart like' ? true : false;
    
    // get csrftoken
    let csrftoken = getCookie('csrftoken');
    
    // send AJAX to change likes count
    fetch(`likes/${element.id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            liked: is_liked
        })
    })
        .then(responce => responce.json())
        .then(post => {

            // get the number of likes
            let likes = post.likes.length;

            // change icon appearance based on action
            if (is_liked) {
                element.classList.replace("bi-heart", "bi-heart-fill");
                element.nextElementSibling.innerHTML = likes;
            } else {
                element.classList.replace("bi-heart-fill", "bi-heart");
                element.nextElementSibling.innerHTML = likes > 0 ? likes : '';
            }
        })
}


function manageFollow(element) {
    // check button
    const is_followed = element.classList.contains('btn-outline-danger')
    
    // get subs element
    let subs = document.querySelector('b.subs')

    // get csrf token
    let csrftoken = getCookie('csrftoken');
    
    fetch(`follow/${element.id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            followed: is_followed
        })
    })
        .then(response => response.json())
        .then(user => {
            if (is_followed) {
                element.classList.replace('btn-outline-danger', 'btn-outline-primary');
                element.innerHTML = 'Follow';
            } else {
                element.classList.replace('btn-outline-primary', 'btn-outline-danger');
                element.innerHTML = 'Unfollow';
            }
            subs.innerHTML = user.followers.length;
        })
}

function postEditing(element) {
    
    // get post that will be edited
    let post = element.parentElement;
    let currentText = element.children[0].innerText;
    element.style.display = 'none';

    // get div header and text area
    const header = post.children[0];
    const div_textarea = post.children[1];
    div_textarea.style.display = 'block';
    const form = div_textarea.children[0];
    
    // cancel button function
    let btn_csl = document.querySelector(`button[data-cancel="${post.dataset.content}"]`)
    btn_csl.onclick = () => {
        div_textarea.style.display = 'none';
        element.style.display = 'block';
    }

    // submit button function
    form.addEventListener('submit', event => {
        
        let content = form.elements['post'].value;
        if (currentText == content.trim()) {

            // if text not changed
            element.style.display = 'block';
            div_textarea.style.display = 'none';
        } else {

            // text was changed
            let csrftoken = getCookie('csrftoken');
    
            fetch(`edit_post/${post.dataset.content}`, {
                method: "PUT",
                headers: {'X-CSRFToken': csrftoken},
                body: JSON.stringify({
                    content: content,
                })
            })
                .then(responce => responce.json())
                .then(data => {
                    header.children[1].innerText = data.timestamp;
                    header.lastElementChild.innerText = '(edited)';
                    element.children[0].innerHTML = content;
                    element.style.display = 'block';
                    div_textarea.style.display = 'none';
                })
        }
        event.preventDefault();
    });
}