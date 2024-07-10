document.addEventListener("DOMContentLoaded", function () {
    const searchbar = document.getElementById("q");

    const fetchSearchResult = (query) => {
        fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => {
            if (response.ok)
                return response.json();
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
    }

    let timeout = null;

    searchbar.addEventListener("input", () => {
        if (!searchbar.value) {
            clearTimeout(timeout);
            return;
        }
        clearTimeout(timeout);
        let query = searchbar.value;

        timeout = setTimeout(() => {
            fetchSearchResult(query);
        }, 1250);
    })

    if (searchbar.value)
        fetchSearchResult(searchbar.value);
})