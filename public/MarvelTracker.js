'use strict';

(function() {
    let seenBefore = null;
    let wantToSee = null;
    let numToSearch = 0;
    let rule = null;

    window.addEventListener("load", LoadData);

    function LoadData() {
        document.getElementById("next").addEventListener("click", screen2);
        fetch('/main')
            .then(checkStatus)
            .then(res => res.json())
            .then(populateScreen)
            .catch(console.error);
    }

    function screen2() {
        document.getElementById("next").removeEventListener("click", screen2);
        document.getElementById("next").addEventListener("click", screen3);
        document.getElementById("previous").addEventListener("click", backto1);
        document.querySelector("h2").textContent = "Step 2. Select the movies you're interested in seeing";
        seenBefore = document.querySelectorAll(".selected");
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.remove("selected");
            seenBefore[i].classList.add("disabled");
            seenBefore[i].classList.add("seen");
        }
        if (wantToSee) {
            for (let i = 0; i < wantToSee.length; i++) {
                wantToSee[i].classList.remove("disabled");
                wantToSee[i].classList.remove("wantToSee");
                wantToSee[i].classList.add("selected");
            }
        }
        document.getElementById('previous').disabled = false;
    }

    function screen3() {
        wantToSee = document.querySelectorAll(".selected");
        if (wantToSee.length === 0) {
            document.querySelector("h2").textContent = "Must select at least one movie you want to see.";
            return;
        }
        document.getElementById("next").removeEventListener("click", screen3);
        document.getElementById("next").addEventListener("click", submit);
        document.getElementById("next").textContent = "Submit";
        document.getElementById("previous").removeEventListener("click", backto1);
        document.getElementById("previous").addEventListener("click", backto2);
        document.querySelector("h2").textContent = "Step 3. Options";
        document.getElementById("options").classList.remove("hidden");
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.remove("selected");
            wantToSee[i].classList.add("wantToSee");
        }
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.add("seen");
        }
        let allMovies = document.querySelectorAll("#movies p");
        for (let i = 0; i < allMovies.length; i++) {
            allMovies[i].classList.add("disabled");
        }
    }

    function backto1() {
        document.querySelector("h2").textContent = "Step 1: Select the movies you've already seen";
        wantToSee = document.querySelectorAll(".selected");
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.remove("selected");
            wantToSee[i].classList.add("disabled");
            wantToSee[i].classList.add("wantToSee");
        }
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.remove("disabled");
            seenBefore[i].classList.add("selected");
            seenBefore[i].classList.remove("seen");
        }
        document.getElementById('previous').disabled = true;
        document.getElementById("next").removeEventListener("click", screen3);
        document.getElementById("next").addEventListener("click", screen2);
    }

    function backto2() {
        document.getElementById("next").removeEventListener("click", submit);
        document.getElementById("next").addEventListener("click", screen3);
        document.getElementById("next").textContent = "Next";
        document.getElementById("previous").removeEventListener("click", backto2);
        document.getElementById("previous").addEventListener("click", backto1);
        let allMovies = document.querySelectorAll("#movies p");
        for (let i = 0; i < allMovies.length; i++) {
            allMovies[i].classList.remove("disabled");
            allMovies[i].classList.remove("wantToSee");
            allMovies[i].classList.remove("recommended");
        }
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.add("selected");
        }
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.add("disabled");
        }

        document.querySelector("h2").textContent = "Step 2. Select the movies you're interested in seeing";
        document.getElementById("options").classList.add("hidden");
    }

    function backto3() {
        document.getElementById("options").classList.remove("hidden");
        document.getElementById("recs").classList.add("hidden");
        document.querySelector("h2").textContent = "Step 3. Options";

        document.getElementById("next").disabled = false;
        document.getElementById("previous").removeEventListener("click", backto3);
        document.getElementById("previous").addEventListener("click", backto2);

    }

    function submit() {
        let body = new FormData;
        let options = {};
        options['parents'] = JSON.parse(stringifyMovieList(seenBefore));
        options['children'] = JSON.parse(stringifyMovieList(wantToSee));
        // get input rule
        rule = document.querySelector('input[name=heuristic]:checked');
        numToSearch = document.getElementById("count").value;
        options['rule'] = rule.value;
        options['count'] = numToSearch;
        // get number of films
        body.append("options", JSON.stringify(options));
        fetch('/results', {method: 'POST', body: body})
            .then(checkStatus)
            .then(res => res.text())
            .then(outputResult)
            .catch(console.error);
    }

    function stringifyMovieList(list) {
        let result = '["';
        if (list.length > 0) {
            result += list[0].textContent;
        }
        for (let i = 1; i < list.length; i++) {
            result += '", "' + list[i].textContent;
        }
        result += '"]';
        return result;
    }

    function outputResult(response) {
        // clear the movies recommended last time
        let lastrecs = document.querySelectorAll(".recommended");
        for (let i = 0; i < lastrecs.length; i++) {
            lastrecs[i].classList.remove("recommended");
        }
        // must replace ' with " or else JSON won't parse
        let films = JSON.parse(response.replace(/'/g, '"'));
        let recs = document.getElementById("recs");
        let result = "";
        for (let i = 0; i < films.length; i++) {
            let movie = films[i];
            // Add this movie to the list
            result += ("\n\n" + movie);
            // highlight this movie in the graphics
            let movieObj = document.getElementById(cleanString(movie));
            let requested = false;
            for (let i = 0; i < wantToSee.length; i++) {
                if (wantToSee[i].textContent === movie) {
                    requested = true;
                }
            }
            if (!requested) {
                movieObj.classList.add("recommended");
            }
        }
        recs.textContent = result;

        // update instructions box
        document.querySelector("h2").textContent = "Results";
        document.getElementById("options").classList.add("hidden");
        recs.classList.remove("hidden");
        document.getElementById("next").disabled = true;
        document.getElementById("previous").removeEventListener("click", backto2);
        document.getElementById("previous").addEventListener("click", backto3);
    }

    function checkStatus(response) {
        if (response.ok) {
            return response;
        } else {
            throw Error("Error in request: " + response.statusText);
        }
    }

    function populateScreen(res) {
        let series = res["All Series"];
        series.sort(compareFilms());
        for (let i = 0; i < series.length; i++) {
            let div = document.createElement("div");
            for (let j = 0; j < series[i]["Films"].length; j++) {
                let p = document.createElement("p");
                p.textContent = series[i]["Films"][j];
                p.addEventListener("click", function() {
                    p.classList.toggle("selected");
                });
                p.id = cleanString(p.textContent);
                div.appendChild(p);
            }
            let movies = document.getElementById("movies");
            movies.appendChild(div);
        }
    }

    function cleanString(text) {
        return text.toLowerCase().replace(/ /g, "-");
    }

    function compareFilms() {
        return function(a, b) {
            if (a["Date"] > b["Date"]) {
                return 1;
            } else if (a["Date"] < b["Date"]) {
                return -1;
            }
            return 0;
        }
    }
})();