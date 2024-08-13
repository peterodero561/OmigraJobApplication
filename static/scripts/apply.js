function applyForJob(jobTitle) {
    window.location.href = `/applyHome?job=${encodeURIComponent(jobTitle)}`;
}

window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const jobTitle = urlParams.get('job');
    if (jobTitle) {
        document.getElementById('job-title').textContent = `Apply for ${jobTitle}`;
    }

    document.getElementById('apply-form').onsubmit = async function (event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        try {
            const response = await fetch('/apply', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                alert('Application submitted successfully!');
                event.target.reset();  // Clear the form
            } else {
                const errorText = await response.text();
                alert(`Failed to submit application: ${errorText}`);
            }
        } catch (error) {
            alert(`An error occurred: ${error.message}`);
        }
        // console.log('Form data:', Object.fromEntries(formData.entries()));

        // // Here you would typically send the formData to the server
        // alert('Application submitted successfully!');
    };
};
