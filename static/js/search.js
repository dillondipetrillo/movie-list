const searchbar = document.getElementById("search");

let timeout = null;

searchbar.addEventListener("input", () => {
    if (searchbar.value.length < 2) {
        clearTimeout(timeout);
        return;
    }
    clearTimeout(timeout);
    let query = searchbar.value;

    timeout = setTimeout(() => {
        fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (response.ok)
                return response.json();
            throw new Error("Reponse status: " + response.status);
        })
        .then(data => {
            let result;
            if (data.Search) {
                result = data.Search;
            } else if (data.Error === "Too many results.") {
                result = `${data.Error} Please be more specific.`;
            } else {
                result = data.Error;
            }
            console.log(result);
        })
        .catch(error => {
            console.log(error);
        })
    }, 1500);
})