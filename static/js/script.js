document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    let isThinking = false;

    // Send message when button is clicked
    sendButton.addEventListener('click', sendMessage);

    // Send message when Enter key is pressed
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !isThinking) {
            sendMessage();
        }
    });

    // Auto-focus input on page load
    userInput.focus();

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '' || isThinking) return;

        // Add user message to chat
        addMessage(message, 'user-message', 'You');
        userInput.value = '';
        isThinking = true;
        showTypingIndicator();

        // Get bot response
        fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_input: message }),
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            // Simulate typing delay based on response length
            const delay = Math.min(2000, Math.max(500, data.response.length * 30));
            setTimeout(() => {
                addMessage(data.response, 'bot-message', 'CoffeeBot');
                isThinking = false;
                // Suggest follow-up questions
                suggestFollowUps(data.tag);
            }, delay);
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage("Sorry, I'm having trouble responding. Please try again.", 'bot-message', 'CoffeeBot');
            isThinking = false;
        });
    }

    function addMessage(text, messageClass, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${messageClass}`;
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'bot-message';
        typingDiv.innerHTML = '<strong>CoffeeBot:</strong> <span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    function suggestFollowUps(lastTag) {
        // Simple follow-up suggestions based on last tag
        const suggestions = {
            'menu': ['What do you recommend?', 'Do you have any specials?'],
            'order': ['Can I add a pastry?', 'What sizes do you have?'],
            'specials': ['Tell me about happy hour', 'Do you have seasonal drinks?'],
            'hours': ['Are you open on holidays?', 'When is the busiest time?']
        };

        if (suggestions[lastTag]) {
            setTimeout(() => {
                const suggestionDiv = document.createElement('div');
                suggestionDiv.className = 'suggestions';
                suggestionDiv.innerHTML = `
                    <p>You might ask:</p>
                    <div class="suggestion-buttons">
                        ${suggestions[lastTag].map(text => 
                            `<button class="suggestion-btn">${text}</button>`
                        ).join('')}
                    </div>
                `;
                chatBox.appendChild(suggestionDiv);
                chatBox.scrollTop = chatBox.scrollHeight;

                // Add event listeners to suggestion buttons
                document.querySelectorAll('.suggestion-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        userInput.value = this.textContent;
                        sendMessage();
                        suggestionDiv.remove();
                    });
                });
            }, 500);
        }
    }
});