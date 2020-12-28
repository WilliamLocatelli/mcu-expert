/**
 * Copyright 2020 William Locatelli.
 * This code handles all of the interactive functionality of the Marvel Movie Picker Wizard interface.
 */
'use strict';

(function() {
    let seenBefore = null;
    let wantToSee = null;
    let numToSearch = 0;
    let rule = null;
    const NUM_FILMS = 23;

    window.addEventListener("load", LoadData);

    /*
     * Adds event listeners to buttons.
     */
    function LoadData() {
        document.getElementById("next").addEventListener("click", screen2);
        // If somebody clicks "whatever it takes", disable changing the count.
        let count = document.getElementById("count");
        let count_slider = document.getElementById("count-slider");
        count.addEventListener("change", function() {
            count.value = Math.min(count.value, NUM_FILMS - 1);
            count.value = Math.max(count.value, 1);
            count_slider.value = count.value;
        });
        count_slider.addEventListener("input", function() {
            count_slider.value = Math.min(count_slider.value, NUM_FILMS - 1);
            count_slider.value = Math.max(count_slider.value, 1);
            count.value = count_slider.value;
        });

        document.getElementById("whatever").addEventListener("click", function() {
            document.getElementById("count").disabled = true;
            document.getElementById("count-slider").disabled = true;
        });

        // If somebody clicks the radio button next to the count, enable changing the count.
        document.getElementById("select_num").addEventListener("click", function() {
            document.getElementById("count").disabled = false;
            document.getElementById("count-slider").disabled = false;
        });
        // Retrieve info from database (currently not being used)
        /*
        fetch('/main')
            .then(checkStatus)
            .then(res => res.json())
            .then(populateScreen)
            .catch(console.error);*/
        // make movies selectable
        let movies = document.querySelectorAll("#movies p");
        for (let i = 0; i < movies.length; i++) {
            movies[i].addEventListener("click", selectElement);
        }
    }

    /*
     * Populates the screen with films returned from the database. (This function is not currently being used.)
     */
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

    function selectElement() {
        this.classList.toggle("selected");
        // Figure out what page we're on
        let header = document.querySelector("#instructions h2").textContent;
        if (header === "Step 1: Select the movies you've already seen") {
            this.classList.toggle("seen");
        } else {
            this.classList.toggle("wantToSee");
        }
    }

    //-----------------------------------------Next Button Functions-----------------------------------------\\
    /*
     * Transitions from screen 1 to screen 2 by updating previous/next buttons, coloring/disabling movies, and changing
     * instructions.
     */
    function screen2() {
        // Update prev/next buttons & instructions
        updatePrevNext(screen2, screen3, reset, backto1);
        document.getElementById("previous").textContent = "Previous";
        document.querySelector("#instructions h2").textContent = "Step 2. Select the movies you're interested in seeing";
        document.querySelector("#instructions .subheading").textContent = "You'll be recommended movies to watch before you watch these.";
        // Mark movies already seen
        seenBefore = document.querySelectorAll(".selected");
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.remove("selected");
            seenBefore[i].classList.add("disabled");
            //seenBefore[i].classList.add("seen");
        }
        // Make movies previously marked as "want to see" selectable
        if (wantToSee) {
            for (let i = 0; i < wantToSee.length; i++) {
                wantToSee[i].classList.remove("disabled");
                //wantToSee[i].classList.remove("wantToSee");
                wantToSee[i].classList.add("selected");
            }
        }
        // Enable previous button
        document.getElementById('previous').disabled = false;
    }

    /*
     * Transitions from screen 2 to screen 3 by updating previous/next buttons, coloring/disabling movies,
     * and changing instructions.
     */
    function screen3() {
        // Make sure at least one movie is selected
        wantToSee = document.querySelectorAll(".selected");
        if (wantToSee.length === 0) {
            document.querySelector("#instructions .subheading").textContent = "Must select at least one movie you want to see.";
            return;
        }
        document.querySelector("#instructions .subheading").classList.add("hidden");
        // Update prev/next buttons & instructions
        updatePrevNext(screen3, submit, backto1, backto2);
        document.getElementById("next").textContent = "Submit";
        document.querySelector("#instructions h2").textContent = "Step 3. Options";
        document.getElementById("options").classList.remove("hidden");
        // Mark selected movies as want to see
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.remove("selected");
            //wantToSee[i].classList.add("wantToSee");
        }
        // Mark seen movies as seen...i dont remember why this is necessary
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.add("seen");
        }
        // disable clicking on movies
        let allMovies = document.querySelectorAll("#movies p");
        for (let i = 0; i < allMovies.length; i++) {
            allMovies[i].classList.add("disabled");
        }
    }

    /*
     * Formats data from page and sends it to backend for processing.
     */
    function submit() {
        document.querySelector("#instructions h2").textContent = "Processing...";
        document.getElementById("next").disabled = true;
        document.getElementById("previous").disabled = true;
        document.getElementById("rel").disabled = true;
        document.getElementById("rec").disabled = true;
        document.getElementById("inter").disabled = true;
        document.getElementById("count").disabled = true;
        document.getElementById("count-slider").disabled = true;
        let body = new FormData;
        let options = {};
        options['parents'] = JSON.parse(stringifyMovieList(seenBefore));
        options['children'] = JSON.parse(stringifyMovieList(wantToSee));
        // get input rule
        rule = document.querySelector('input[name=heuristic]:checked');
        options['rule'] = rule.value;
        // get number of films
        numToSearch = document.getElementById("count").value;
        options['count'] = numToSearch;
        // get count rule
        let count_rule = document.querySelector('input[name=count_rule]:checked');
        options['count_rule'] = count_rule.value;
        body.append("options", JSON.stringify(options));
        fetch('/results', {method: 'POST', body: body})
            .then(checkStatus)
            .then(res => res.text())
            .then(outputResult)
            .catch(displayError);
    }

    /*
     * Processes data returned from backend and displays it on the page.
     */
    function outputResult(response) {
        let lastRecs = document.querySelectorAll(".recommended");
        for (let i = 0; i < lastRecs.length; i++) {
            lastRecs[i].classList.remove("recommended");
        }
        // must replace ' with " or else JSON won't parse
        let data = JSON.parse(response.replace(/'/g, '"'));
        let films = data['films'];
        if (films.length === 0) {
            document.getElementById("error").textContent = data['msg'];
            document.getElementById("error").classList.remove("hidden");
        }
        let recommendedFilms = [];
        let requestedFilms = [];
        let recs = document.getElementById("recs");
        let order = document.getElementById("watch-order");
        order.innerHTML = "";
        for (let i = 0; i < films.length; i++) {
            let movie = films[i];
            let movieObj = document.getElementById(cleanString(movie));
            let result = document.createElement("p");
            result.textContent = movie;
            let requested = false;
            for (let i = 0; i < wantToSee.length; i++) {
                if (wantToSee[i].textContent === movie) {
                    requested = true;
                }
            }
            if (requested) {
                requestedFilms.push(movie);
                //result.textContent += " (Your selection)";
                result.classList.add("requested");
            } else {
                recommendedFilms.push(movie);
                movieObj.classList.add("recommended");
                //result.textContent += " (Our recommended film)";
            }
            let li = document.createElement("li");
            li.appendChild(result);
            order.appendChild(li);
        }
        // generate text output

        recs.textContent = generateSentence(recommendedFilms, requestedFilms);

        // update instructions box
        document.querySelector("#instructions h2").textContent = "Done! Scroll down for results.";
        document.getElementById("options").classList.add("hidden");
        document.getElementById("results").classList.remove("hidden");
        document.getElementById("previous").disabled = false;
        document.getElementById("previous").removeEventListener("click", backto2);
        document.getElementById("previous").addEventListener("click", backto3);
    }

    /*
     * Generates a sentence telling the user what their recommended films are.
     */
    function generateSentence(recommendedFilms, requestedFilms) {
        let text1;
        let rule = document.querySelector('input[name=heuristic]:checked');
        let count = parseInt(document.getElementById("count").value);
        if (recommendedFilms.length < count) {
            if (count === 1) {
                text1 = "You requested 1 film, but there "
            } else {
                text1 = "You requested " + count + " films, but there";
            }
            if (recommendedFilms.length === 0) {
                text1 += " are no films to watch before";
            } else if (recommendedFilms.length === 1) {
                text1 += " is only 1 film to watch before";
            } else {
                text1 += " are only " + recommendedFilms.length + " films to watch before";
            }
            if (requestedFilms.length === 1) {
                text1 += " watching ";
            } else {
                text1 += "/between watching ";
            }
            text1 += listFilms(requestedFilms);
            if (recommendedFilms.length === 1) {
                text1 += ". That film is " + listFilms(recommendedFilms);
            } else if (recommendedFilms.length > 1) {
                text1 += ". Those films are " + listFilms(recommendedFilms);
            }
        } else {
            // Case where there are no recommended films
            if (recommendedFilms.length === 0) {
                text1 = "There are no other films you should watch ";
                if (requestedFilms.length === 1) {
                    text1 += " before watching " + listFilms(requestedFilms);
                } else {
                    text1 += " before/between watching " + listFilms(requestedFilms);
                }
            } else if (rule.value === "Interconnected") {
                text1 = "In order to have the most interconnected viewing experience possible while only watching " + recommendedFilms.length;
                if (recommendedFilms.length === 1) {
                    text1 += " additional film";
                } else {
                    text1 += " additional films";
                }
                text1 += ", you should watch " + listFilms(recommendedFilms);
                if (requestedFilms.length === 1) {
                    text1 += " before watching " + listFilms(requestedFilms);
                } else {
                    text1 += " before/between watching " + listFilms(requestedFilms);
                }
            } else if (rule.value === "Relevant") {
                if (recommendedFilms.length === 1) {
                    text1 = "The most relevant film to " + listFilms(requestedFilms) + " is " + listFilms(recommendedFilms);
                } else {
                    text1 = "The " + recommendedFilms.length + " most relevant films to " + listFilms(requestedFilms) + " are " + listFilms(recommendedFilms);
                }
            } else if (rule.value === "Recent") {
                text1 = "When " + listFilms(requestedFilms) + " came out, the ";
                if (recommendedFilms.length === 1) {
                    text1 += "most recent film featuring characters/plotlines in ";
                } else {
                    text1 += recommendedFilms.length + " most recent films featuring characters/plotlines in ";
                }
                if (requestedFilms.length === 1) {
                    text1 += "this movie ";
                } else {
                    text1 += "these movies ";
                }
                if (recommendedFilms.length === 1) {
                    text1 += " was " + listFilms(recommendedFilms);
                } else {
                    text1 += " were " + listFilms(recommendedFilms);
                }
            }
        }
        text1 += ".";
        return text1;
    }


    //-----------------------------------------Back Button Functions-----------------------------------------\\
    /*
     * Transitions from screen 2 to screen 1 by updating previous/next buttons, coloring/disabling movies,
     * and changing instructions.
     */
    function backto1() {
        document.querySelector("#instructions h2").textContent = "Step 1: Select the movies you've already seen";
        document.querySelector("#instructions .subheading").textContent = "If you don't remember the " +
            "movie and wouldn't mind watching it again, don't select it.";
        wantToSee = document.querySelectorAll(".selected");
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.remove("selected");
            wantToSee[i].classList.add("disabled");
            //wantToSee[i].classList.add("wantToSee");
        }
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.remove("disabled");
            seenBefore[i].classList.add("selected");
            //seenBefore[i].classList.remove("seen");
        }
        document.getElementById('previous').textContent = "Reset";
        updatePrevNext(screen3, screen2, backto1, reset)
    }

    /*
     * Transitions from screen 3 to screen 2 by updating previous/next buttons, coloring/disabling movies,
     * and changing instructions.
     */
    function backto2() {
        updatePrevNext(submit, screen3, backto2, backto1)
        document.getElementById("next").textContent = "Next";
        let allMovies = document.querySelectorAll("#movies p");
        for (let i = 0; i < allMovies.length; i++) {
            allMovies[i].classList.remove("disabled");
            //allMovies[i].classList.remove("wantToSee");
            allMovies[i].classList.remove("recommended");
        }
        for (let i = 0; i < wantToSee.length; i++) {
            wantToSee[i].classList.add("selected");
        }
        for (let i = 0; i < seenBefore.length; i++) {
            seenBefore[i].classList.add("disabled");
        }

        document.querySelector("#instructions h2").textContent = "Step 2. Select the movies you're interested in seeing";
        document.querySelector("#instructions .subheading").textContent = "You'll be recommended movies to watch before you watch these.";
        document.querySelector("#instructions .subheading").classList.remove("hidden");
        document.getElementById("options").classList.add("hidden");
        document.getElementById('results').classList.add("hidden");
    }

    /*
     * Transitions from final watchlist screen to screen 3 by updating previous/next buttons, coloring/disabling movies,
     * and changing instructions.
     */
    function backto3() {
        document.getElementById("error").classList.add("hidden");
        document.getElementById("options").classList.remove("hidden");
        document.querySelector("#instructions h2").textContent = "Step 3. Options";

        document.getElementById("next").disabled = false;
        document.getElementById("rel").disabled = false;
        document.getElementById("rec").disabled = false;
        document.getElementById("inter").disabled = false;
        document.getElementById("count").disabled = false;
        document.getElementById("count-slider").disabled = false;
        document.getElementById("previous").removeEventListener("click", backto3);
        document.getElementById("previous").addEventListener("click", backto2);

    }

    /*
     * Resets the page by clearing all global variables and making all movies deselected and selectable.
     */
    function reset() {
        seenBefore = null;
        wantToSee = null;
        numToSearch = 0;
        rule = null;
        let allMovies = document.querySelectorAll("#movies p");

        for (let i = 0; i < allMovies.length; i++) {
            allMovies[i].classList.remove("selected");
            allMovies[i].classList.remove("disabled");
            allMovies[i].classList.remove("wantToSee");
            allMovies[i].classList.remove("seen");
            allMovies[i].classList.remove("recommended");
        }
        document.getElementById('previous').disabled = true;
        document.getElementById('results').classList.add("hidden");
    }

    //------------------------------------------Helper Functions--------------------------------------------\\


    /*
     * Checks response from fetch request, and throws error if an error occurred.
     */
    function checkStatus(response) {
        if (response.ok) {
            return response;
        } else {
            throw Error("Error in request: " + response.statusText);
        }
    }

    /*
     * Converts string to lowercase and replaces all spaces with dashes.
     */
    function cleanString(text) {
        return text.toLowerCase().replace(/ /g, "-");
    }

    /*
     * Used for arrays.sort() to compare films by release date.
     */
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

    /*
     * Displays an error on the screen. res format: {"error": "Error title"}
     */
    function displayError(res) {
        document.getElementById("error").textContent = "Error occurred, please refresh. \n" + res;
        document.getElementById("error").classList.remove("hidden");
    }

    /*
     * Returns a string which lists the films in list.
     * list - array containing the titles of all films to list
     * returns: a string of the format "<film name>" for single-item lists, "<film name> and <film name>" for 2-item
     *          lists, and "<film name>, <film name>, and <film name>" for lists containing 3+ items.
     */
    function listFilms(list) {
        if (list.length === 1) {
            return list[0];
        } else if (list.length === 2) {
            return list[0] + " and " + list[1];
        } else {
            let result = "";
            for (let i = 0; i < list.length - 1; i++) {
                result += list[i] + ", ";
            }
            result += "and " + list[list.length - 1];
            return result;
        }
    }

    /*
     * Converts a list of paragraphs containing movie titles into a JSON-formatted string, like '["Movie 1", "Movie 2"]'
     */
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

    /*
     * Updates previous and next buttons by removing the oldNext and oldPrev listeners and adding
     * the newPrev and newNext listeners.
     */
    function updatePrevNext(oldNext, newNext, oldPrev, newPrev) {
        let next = document.getElementById("next");
        let prev = document.getElementById("previous");
        next.removeEventListener("click", oldNext);
        if (newNext !== null) {
            next.addEventListener("click", newNext);
        }
        prev.removeEventListener("click", oldPrev);
        if (newPrev !== null) {
            prev.addEventListener("click", newPrev);
        }
    }
})();