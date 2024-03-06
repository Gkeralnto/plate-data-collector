document.getElementById('sendImg').addEventListener('click', function () {
    var imgElement = document.getElementById('croppedImg');
    var imgData = getBase64Image(imgElement);

    sendDataToBackend(imgData);
});

function getBase64Image(imgElement) {
    if (imgElement.src.startsWith('data:image')) {
        return imgElement.src.split(',')[1];
    }
    else {
        var canvas = document.createElement('canvas');
        canvas.width = imgElement.width;
        canvas.height = imgElement.height;

        var ctx = canvas.getContext('2d');
        ctx.drawImage(imgElement, 0, 0);

        var dataURL = canvas.toDataURL('image/png');
        return dataURL.replace(/^data:image\/(jpg|png);base64,/, '');
    };
};

function sendDataToBackend(imgData) {
    fetch('https://pinakides.azurewebsites.net/process-image', {
        method: 'POST',
        body: JSON.stringify({ image: imgData }),
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(response => {
            if (response.ok) {
                console.log('Image sent succesfully');
            } else {
                console.error('Error sending image');
            }
        })
        .catch(error => {
            console.error('Error sending image:', error);
        });
};
