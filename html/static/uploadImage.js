document.addEventListener('DOMContentLoaded', function () {
    // File input change event listener
    var cropper = null;

    document.getElementById('uploadInput').addEventListener('change', function (event) {
        var file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            if (cropper != null) {
                cropper.destroy();
                cropper = null;
            }
            var reader = new FileReader();
            reader.onload = function (event) {
                var img = document.getElementById('imgPreview');
                img.src = event.target.result;
                img.onload = function () {
                    // Initialize Cropper once image is loaded
                    cropper = new Cropper(img, {
                        aspectRatio: 0,
                        viewMode: 0,
                        rotatable: true,
                    });

                    var rotationSlider = document.getElementById('rotationSlider');
                    rotationSlider.addEventListener('input', function () {
                        var rotationVal = parseInt(rotationSlider.value);
                        cropper.rotateTo(rotationVal);
                    });
                    // Add event listener for crop button
                    document.getElementById('cropBtn').addEventListener('click', function () {
                        sendBtn = document.getElementById('sendImg');
                        var croppedImage = cropper.getCroppedCanvas().toDataURL("image/png");
                        document.getElementById('croppedImg').src = croppedImage;
                        sendBtn.disabled = false;
                    });
                };
            };
            reader.readAsDataURL(file);
        } else {
            alert('Παρακαλώ επιλέξτε αρχείο φωτογραφίας.');
        }
    });
});
