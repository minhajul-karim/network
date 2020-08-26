document.addEventListener('DOMContentLoaded', () => {
  // Post a status
  if (document.querySelector('#new-post')) {
    document
      .querySelector('#new-post-form')
      .addEventListener('submit', (event) => {
        event.preventDefault()
        const errorMessage = document.querySelector('#status-error')
        let content = event.target.content.value
        // Dispaly error message for emtpy status
        if (content.length === 0) {
          errorMessage.textContent = 'You must write something!'
        } else {
          fetch('/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
              content: event.target.content.value,
            }),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.invalid_post) {
                // When content passed to server was empty
                errorMessage.textContent = 'You must write something!'
              } else if (data.updated) {
                // Reload page to display updated posts
                window.location.reload()
              }
            })
          // Remove error messages
          errorMessage.textContent = ''
        }
      })
  }

  // Follow - unfollow a user
  if (
    document.querySelector('#profile') &&
    document.querySelector('#follow-btn')
  ) {
    document.querySelector('#follow-btn').addEventListener('click', (event) => {
      fetch('/follow-unfollow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          userId: event.target.dataset.userId,
          alreadyFollows: event.target.dataset.alreadyFollows,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.followed || data.unfollowed) {
            window.location.reload()
            // TODO: Can we just edit the follow button text
            // with follower/following count and avoid page reload?
          }
        })
    })
  }

  // Like-unlike and edit posts
  if (document.querySelector('.posts')) {
    document.querySelector('.posts').addEventListener('click', (event) => {
      if (event.target.id === 'like-btn') {
        const { postId, hasLiked } = event.target.dataset
        let numOfLikes = document.querySelector(`#num-of-likes-${postId}`)
        fetch('/like-unlike', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            postId: postId,
            hasLiked: hasLiked,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.liked) {
              // Change like button color, data-has-liked attribute and like count
              event.target.style.color = '#dc3545'
              event.target.dataset.hasLiked = 'True'
              numOfLikes.textContent = parseInt(numOfLikes.textContent) + 1
            } else if (data.unliked) {
              // Change like button color, data-has-liked attribute and like count
              event.target.style.color = '#343a40'
              event.target.dataset.hasLiked = 'False'
              numOfLikes.textContent = parseInt(numOfLikes.textContent) - 1
            }
          })
      } else if (event.target.className.includes('edit-post')) {
        // Place post content in a textarea upon clicking 'Edit post'
        const postId = event.target.dataset.postId
        let content = document.querySelector(`#post-${postId}`).textContent
        document.querySelector('#edit-post-textarea').value = content
        document
          .querySelector('#edit-post-btn')
          .addEventListener('click', (event) => {
            const newContent = document.querySelector('#edit-post-textarea')
              .value
            $('#myModal').modal('hide')
            // Send new content with post id to server
            fetch('/edit-post', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
              },
              body: JSON.stringify({
                postId: postId,
                content: newContent,
              }),
            })
              .then((response) => response.json())
              .then((data) => {
                if (data.edited) {
                  // Hide modal and update content
                  $('#editPostModal').modal('hide')
                  document.querySelector(
                    `#post-${postId}`
                  ).textContent = newContent
                }
              })
          })
      }
    })
  }
})

// Get CSRF token
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
