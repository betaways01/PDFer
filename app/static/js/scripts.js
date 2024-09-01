document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('progress-section').classList.remove('hidden');
    document.querySelector('.progress').style.width = '50%'; // Mock progress
    setTimeout(function() {
        document.querySelector('.progress').style.width = '100%';
    }, 2000);
    setTimeout(function() {
        event.target.submit(); // Submit form after progress
    }, 2500);
});