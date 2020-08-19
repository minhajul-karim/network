document.addEventListener('DOMContentLoaded', () => {
  // Post a status
  if (document.querySelector('#status-form')) {
    document
      .querySelector('#status-form')
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
                // Clear the textarea after status update
                document.querySelector('#status').value = ''
              }
            })
          // Remove error messages
          errorMessage.textContent = ''
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
