console.log('js loaded')
document.addEventListener("DOMContentLoaded", function () {
    console.log("HTML document fully loaded and parsed");



    //Follow functionality
    btn = document.getElementsByClassName('follow_btn')[0]
    if (btn) {
        btn.addEventListener('click', event => {
            let userProfile = btn.getAttribute('data-userprofile');
            url = `/toggle_follow/?follows=${userProfile}`
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.followed) {
                        btn.innerHTML = 'Unfollow'
                    } else {
                        btn.innerHTML = 'Follow'
                    }
                    document.getElementById('followers_count').innerText = data.follower_count
                })
        })

    }
    //Like functionality
    document.querySelectorAll('.like_btn').forEach(item => {
        item.addEventListener('click', event => {
            // handle click
            let button = event.currentTarget;;
            console.log(button); // Check if the correct button element is logged

            let postid = button.getAttribute('data-postid');
            console.log(postid); // Check the value of postid

            let likeCount = parseInt(button.getAttribute('data-likecount'));
            console.log(likeCount); // Check the value of likeCount
            fetch(`/toggle_like/?post_id=${postid}`)
                .then(response => response.json())
                .then(data => {
                    if (data.liked) {
                        likeCount--;
                        likeCount = likeCount.toString()
                        button.innerHTML = `<i class="far fa-thumbs-up"></i> Like <span class="badge badge-light">${likeCount}</span>`;
                    } else {
                        likeCount++;
                        button.innerHTML = `<i class="far fa-thumbs-up"></i> Unlike <span class="badge badge-light">${likeCount}</span>`;
                    }
                    // Update the like count in the button's dataset
                    button.setAttribute('data-likecount', likeCount);
                })
        })
    })

    document.querySelectorAll('.edit_btn').forEach(item => {
        item.addEventListener('click', event => {
            // handle click
            let button = event.currentTarget;;
            console.log(button); // Check if the correct button element is logged

            let postid = button.getAttribute('data-postid');
            let post_content = button.getAttribute('data-content');
            console.log(postid); // Check the value of postid
            document.getElementById(`body_${postid}`).classList.add('hidden')
            document.getElementById(`textarea_${postid}`).classList.remove('hidden')

            document.getElementById(`save_${postid}`).classList.remove('hidden')
            button.classList.add('hidden')
        })
    })

});
document.querySelectorAll('.save_btn').forEach(item => {
    item.addEventListener('click', event => {
        // handle click
        let button = event.currentTarget;
        let postid = button.getAttribute('data-postid');
        console.log(postid)
        console.log(button);
        button.classList.add('hidden')
        document.getElementById(`edit_${postid}`).classList.remove('hidden')
        console.log(document.getElementById(`textarea_${postid}`))
        document.getElementById(`body_${postid}`).querySelector('p').innerText = document.getElementById(`textarea_${postid}`).querySelector('textarea').value
        document.getElementById(`body_${postid}`).classList.remove('hidden')
        document.getElementById(`textarea_${postid}`).classList.add('hidden')

        //Send fetch to change data
        postid = button.getAttribute('data-postid');
        let content = document.getElementById(`textarea_${postid}`).querySelector('textarea').value
        let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(`/posts/${postid}/`, { // Replace with your actual API endpoint
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ content: content }),
        }).then(response => {
            return response.json();
        }).then(data => {
            console.log('Success:', data);
        })
    })
})