let currentId = 'starting';

function getRandomImage() {
    fetch('https://pinakides.azurewebsites.net/random-pic', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                curElement = document.getElementById(currentId);
                curElement.src = '';
                currentId = 'starting';
                curElement.id = currentId;
                console.error(data.error)
                return;
            } else {
                curElement = document.getElementById(currentId);
                curElement.src = 'data:image/png;base64,' + data.image_blob;
                currentId = data.id;
                curElement.id = currentId;
            }
        })
        .catch(error => console.error('Error:', error));
}

function submitUserInput(id) {
    const userInput = document.getElementById('userinputinner').value;
    var currentImage = document.getElementById(id);
    if (currentImage.id !== 'starting') {
        //Send the user's input and ID to the server
        fetch('https://pinakides.azurewebsites.net/process-user-input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: currentImage.id, label: userInput })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => console.error('Error', error));
    } else {
        console.error('Image ID or user input is missing')
    }
    getRandomImage();
};

document.addEventListener('DOMContentLoaded', function () {
    getRandomImage();
    document.getElementById('nextbtn').addEventListener('click', function () {
        submitUserInput(currentId)
    })
});
