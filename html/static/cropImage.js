document.addEventListener('DOMContentLoaded', function () {
    const image = document.getElementById('imgPreview');

    const cropper = new Cropper(image, {
        aspectRatio: 0,
        viewMode: 0,
        zoomable: true,
    });

    document.getElementById('cropBtn').addEventListener('click', function () {
        var croppedImage = cropper.getCroppedCanvas().toDataURL("image/png");
        document.getElementById('croppedImg').src = croppedImage;
    });
});