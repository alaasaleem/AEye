function startTimer(element, endText, duration, hideAfter) {
    let timeLeft = duration; 
    element.style.display = 'block';

    const countdown = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(countdown);
            element.textContent = endText; 
            setTimeout(() => {
                element.style.display = 'none';
            }, hideAfter);
        } else {
            element.textContent = timeLeft;
            timeLeft -= 1;
        }
    }, 1000);
}

export { startTimer };
