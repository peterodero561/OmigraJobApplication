function applyForJob(jobTitle) {
    // Store the job title in localStorage or pass it via query parameters
    localStorage.setItem('jobTitle', jobTitle);
    
    // Redirect to apply.html
    window.location.href = '/applyHome';
}