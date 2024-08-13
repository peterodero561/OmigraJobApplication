function applyForJob(jobTitle) {
    window.location.href = `apply.html?job=${encodeURIComponent(jobTitle)}`;
}

window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const jobTitle = urlParams.get('job');
    if (jobTitle) {
        const jobTitleElement = document.getElementById('job-title');
        if (jobTitleElement) {
            jobTitleElement.textContent = `Apply for ${jobTitle}`;
        }
    }

    const applyForm = document.getElementById('apply-form');
    if (applyForm) {
        applyForm.onsubmit = function (event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            console.log('Form data:', Object.fromEntries(formData.entries()));

            // Here you would typically send the formData to the server
            alert('Application submitted successfully!');
        };
    }

    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.onsubmit = function (event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            console.log('Form data:', Object.fromEntries(formData.entries()));

            // Here you would typically send the formData to the server
            alert('Message sent successfully!');
        };
    }
};
