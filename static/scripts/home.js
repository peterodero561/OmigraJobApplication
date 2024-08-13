function applyForJob(jobTitle) {
    window.location.href = `/applyHome?job=${encodeURIComponent(jobTitle)}`;
}

window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const jobTitle = urlParams.get('job');
    if (jobTitle) {
        document.getElementById('job-title').textContent = `Apply for ${jobTitle}`;
    }

    document.getElementById('apply-form').onsubmit = function (event) {
        event.preventDefault();

        const formData = new FormData(event.target); 
        console.log('Form data:', Object.fromEntries(formData.entries()));

        // Here you would typically send the formData to the server
        alert('Application submitted successfully!');
    };
};
