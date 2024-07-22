document.getElementById('loadData').addEventListener('click', function() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            let dataContainer = document.getElementById('dataContainer');
            dataContainer.innerHTML = ''; // Clear previous content
            data.forEach(item => {
                let itemElement = document.createElement('p');
                itemElement.textContent = `Item: ${item[1]}`; // Assuming item[1] is the name field
                dataContainer.appendChild(itemElement);
            });
        });
});

document.getElementById('addItemForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form from submitting normally

    let itemName = document.getElementById('itemName').value;

    fetch('/add_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: itemName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear the input field
            document.getElementById('itemName').value = '';

            // Reload the item list
            document.getElementById('loadData').click();
        } else {
            alert('Failed to add item');
        }
    });
});
