document.addEventListener('DOMContentLoaded', (event) => {
    let userUUID = localStorage.getItem('userUUID');

    if (!userUUID) {
        fetch('/insert-user')
        .then(response => response.json())
        .then(data => {
            if(data.success){
                localStorage.setItem('userUUID', data.UUID);
                console.log("UUID processed:", data);
            }
            else {

                 
            }
        })
        .catch((error) => {
            console.error('Error processing UUID:', error);
        });
    }
});
