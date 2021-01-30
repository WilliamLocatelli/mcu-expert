/**
 * Copyright 2020 William Locatelli.
 * Backend for Marvel Movie Wizard.
 */
'use strict';

const path = require('path');  // For accessing python file
const {spawn} = require('child_process');  // For running python script
const express = require('express');  // For node app
const app = express();
const sqlite3 = require('sqlite3');  // For database
const sqlite = require('sqlite');  // For database
const multer = require('multer');  // For post requests

// For main page redirect:
const redir = "<!DOCTYPE html>\n" +
    "<html lang=\"en\">\n" +
    "   <head>\n" +
    "      <title>Which Marvel Movies Should I Watch?</title>\n" +
    "      <meta http-equiv = \"refresh\" content = \"0; url = /index.html\" />\n" +
    "   </head>\n" +
    "   <body>\n" +
    "   </body>\n" +
    "</html>";

app.use(express.urlencoded({extended: true}));
app.use(express.json());
app.use(multer().none());


app.use(express.static("public"));
/*
 * Redirects requests to root to main page
 */
app.get('/', async function(req, res) {
    res.send(redir);
});

/*
 * Retrieves all movie titles from database, organizing them by series and release date.
 * Response format: {"All Series:" [ { "Series": "Series 1 name", "Films": ["Film 1", "Film 2", ...]}, {"Series": ...}]}
 * Possible errors: 500 server error
 */
app.get('/main/', async function(req, res) {
    try {
        let db = await getDBConnection();
        let titles = await db.all("SELECT Title, Series, ReleaseDate FROM Films ORDER BY Series");
        await db.close();
        let result = {"All Series": []};
        let series = 0;
        for (let i = 0; i < titles.length; i++) {
            if (result["All Series"].length === 0) {
                result["All Series"].push({"Series": titles[i]['Series'], "Films": [], "Date": titles[i]['ReleaseDate']});
                result['All Series'][series]["Films"].push(titles[i]['Title']);
            } else if (result['All Series'][series]["Series"] !== titles[i]['Series']) {
                result["All Series"].push({"Series": titles[i]['Series'], "Films": [], "Date": titles[i]['ReleaseDate']});
                series++;
                result['All Series'][series]["Films"].push(titles[i]['Title']);
            } else {
                result['All Series'][series]["Films"].push(titles[i]['Title']);
            }
        }
        res.status(200).json(result);
    } catch(err) {
        res.status(500).json({'error': 'Internal server error'});
    }
});

/*
 * Runs python script on input data and outputs results.
 * Input format example: {"parents": ["watched_film_1", "watched_film_2", ...], "children": ["film_1", "film_2", ...],
 *                        "count": "3", "rule": "Recent", "count_rule": "Whatever It Takes"}
 * Output format: {"msg": "", "films": ["film_x", "film_1", "film_2", ...]
 * Possible errors: 400 if negative count passed, 500 server error
 */
app.post('/results/', async function (req, res) {
    try {
        let count = parseFloat(JSON.parse(req.body.options).count);
        if (count < 1) {
            res.status(400).json({"error": "Cannot select a negative number of films"})
        } else if (isNaN(count) || !Number.isInteger(count)) {
            res.status(400).json({"error": "Number of films must be an integer number"})
        } else {
            const python = spawn('python', [path.join(__dirname, 'LaunchScript.py'), req.body.options]);
            let dataToSend = '["no data"]\n';
            python.stdout.on('data', (data) => {
                dataToSend = data.toString();
            });
            python.stderr.on('data', (data) => {
                console.log(`error:${data}`);
            });
            python.on('close', (code) => {
                console.log(`child process close all stdio with code ${code}`);
                // send data to frontend
                let data = JSON.parse(dataToSend.substring(0, dataToSend.length - 1).replace(/'/g, '"'));
                let message = generateSentence(req.body.options, data["films"]);
                let result = concatenateResult(data["films"], message);
                res.text;
                res.send(result);
            });
        }

    } catch(err) {
        console.error(err);
        res.status(500).json({'error': 'Internal server error'});
    }
});

/*
 * Returns connection to the sqlite database
 */
async function getDBConnection() {
  const db = await sqlite.open({
    filename: 'FilmData.db',
    driver: sqlite3.Database
  });
  return db;
}

/*
 * Puts films and message into a single stringified JSON object
 */
function concatenateResult(films, message) {
    let result = "{\"films\": [\"" + films[0] + "\"";
    for (let i = 1; i < films.length; i++) {
        result += ",\"" + films[i] + "\"";
    }
    result += "], \"msg\": \"";
    result += message;
    result += "\"}";
    return result;
}

/*
 * Generates a sentence telling the user what their recommended films are.
 */
function generateSentence(options, films) {
    options = JSON.parse(options);
    let rule = options['rule'];
    let requestedFilms = options["children"];
    let text;
    let unwatchedFilms = films.filter(x => !options["parents"].includes(x));
    let recommendedFilms = unwatchedFilms.filter(x => !options["children"].includes(x));
    let count = parseInt(options["count"]);
    if (recommendedFilms.length < count) {
        if (count === 1) {
            text = "You requested 1 film, but there "
        } else {
            text = "You requested " + count + " films, but there";
        }
        if (recommendedFilms.length === 0) {
            text += " are no films to watch before";
        } else if (recommendedFilms.length === 1) {
            text += " is only 1 film to watch before";
        } else {
            text += " are only " + recommendedFilms.length + " films to watch before";
        }
        if (requestedFilms.length === 1) {
            text += " watching ";
        } else {
            text += "/between watching ";
        }
        text += listFilms(requestedFilms);
        if (recommendedFilms.length === 1) {
            text += ". That film is " + listFilms(recommendedFilms);
        } else if (recommendedFilms.length > 1) {
            text += ". Those films are " + listFilms(recommendedFilms);
        }
    } else {
        // Case where there are no recommended films
        if (recommendedFilms.length === 0) {
            text = "There are no other films you should watch ";
            if (requestedFilms.length === 1) {
                text += " before watching " + listFilms(requestedFilms);
            } else {
                text += " before/between watching " + listFilms(requestedFilms);
            }
        } else if (rule === "Interconnected") {
            text = "In order to have the most interconnected viewing experience possible while only watching " + recommendedFilms.length;
            if (recommendedFilms.length === 1) {
                text += " additional film";
            } else {
                text += " additional films";
            }
            text += ", you should watch " + listFilms(recommendedFilms);
            if (requestedFilms.length === 1) {
                text += " before watching " + listFilms(requestedFilms);
            } else {
                text += " before/between watching " + listFilms(requestedFilms);
            }
        } else if (rule === "Relevant") {
            if (recommendedFilms.length === 1) {
                text = "The most relevant film to " + listFilms(requestedFilms) + " is " + listFilms(recommendedFilms);
            } else {
                text = "The " + recommendedFilms.length + " most relevant films to " + listFilms(requestedFilms) + " are " + listFilms(recommendedFilms);
            }
        } else if (rule === "Recent") {
            text = "When " + listFilms(requestedFilms) + " came out, the ";
            if (recommendedFilms.length === 1) {
                text += "most recent film featuring characters/plotlines in ";
            } else {
                text += recommendedFilms.length + " most recent films featuring characters/plotlines in ";
            }
            if (requestedFilms.length === 1) {
                text += "this movie ";
            } else {
                text += "these movies ";
            }
            if (recommendedFilms.length === 1) {
                text += " was " + listFilms(recommendedFilms);
            } else {
                text += " were " + listFilms(recommendedFilms);
            }
        }
    }
    text += ".";
    return text;
}

/*
 * Returns a string which lists the films in list.
 * list - array containing the titles of all films to list
 * returns: a string of the format "<film name>" for single-item lists, "<film name> and <film name>" for 2-item
 *          lists, and "<film name>, <film name>, and <film name>" for lists containing 3+ items.
 */
function listFilms(list) {
    if (list.length === 1) {
        return "<cite>" + list[0] + "</cite>";
    } else if (list.length === 2) {
        return "<cite>" + list[0] + "</cite> and <cite>" + list[1] + "</cite>";
    } else {
        let result = "";
        for (let i = 0; i < list.length - 1; i++) {
            result += "<cite>" + list[i] + "</cite>, ";
        }
        result += "and <cite>" + list[list.length - 1] + "</cite>";
        return result;
    }
}

app.get('*', function(req, res){
  res.status(404).send('<strong>404 error</strong>.<br> Page not found. <a href="/">Back to Main Page</a>');
});

const PORT = process.env.PORT || 8000;
app.listen(PORT);