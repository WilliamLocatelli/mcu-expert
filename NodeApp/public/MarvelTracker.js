'use strict';

(function() {
    let seenBefore = null;
    let wantToSee = null;
    let numToSearch = 0;

    window.addEventListener("load", LoadData);

    function LoadData() {
        document.getElementById("next").addEventListener("click", screen2);
        fetch('/main')
            .then(checkStatus)
            .then(res => res.json())
            .then(populateBoard)
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
        document.getElementById("next").removeEventListener("click", screen3);
        document.getElementById("next").addEventListener("click", submit);
        document.getElementById("next").textContent = "Submit";
        document.getElementById("previous").removeEventListener("click", backto1);
        document.getElementById("previous").addEventListener("click", backto2);
        wantToSee = document.querySelectorAll(".selected");
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

    function submit() {

    }

    function checkStatus(response) {
        if (response.ok) {
            return response;
        } else {
            throw Error("Error in request: " + response.statusText);
        }
    }

    function populateBoard(res) {
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
                div.appendChild(p);
            }
            let movies = document.getElementById("movies");
            movies.appendChild(div);
        }
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