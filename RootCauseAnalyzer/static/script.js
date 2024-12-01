function updateProgress() {
            fetch('/progress')
                .then(response => response.json())
                .then(data => {
                    if (data.progress === -1) {
                        document.getElementById('progress').innerText = data.error;
                        document.getElementById('progress').classList.add('error');
                        document.getElementById('progressBar').style.display = 'none';
                        document.getElementById('backLink').style.display = 'block';
                    } else {
                        document.getElementById('progress').innerText = data.progress + '%';
                        document.getElementById('progressBar').value = data.progress;
                        document.getElementById('message').innerText = data.message;
                        if (data.progress < 100) {
                            setTimeout(updateProgress, 3000);
                        } else {
                            document.getElementById('message').innerText = "Root Causes generated";
                            document.getElementById('downloadLink').style.display = 'block';
                        }
                    }
                });
        }
        window.onload = updateProgress;