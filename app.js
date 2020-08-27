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
        if (parseInt(JSON.parse(req.body.options).count) < 1) {
            res.status(400).json({"error": "Cannot select a negative number of films"})
        } else {
            const python = spawn('python', [path.join(__dirname, 'LaunchScript.py'), req.body.options]);
            let dataToSend = '["no data"]\n';
            python.stdout.on('data', (data) => {
                console.log('Pipe data from python script ...');
                dataToSend = data.toString();
            });
            python.stderr.on('data', (data) => {
                console.log(`error:${data}`);
            });
            python.on('close', (code) => {
                console.log(`child process close all stdio with code ${code}`);
                // send data to frontend
                res.text;
                res.send(dataToSend.substring(0, dataToSend.length - 1));
            });
        }

    } catch(err) {
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

app.get('*', function(req, res){
  res.status(404).send('<strong>404 error</strong>.<br> Page not found. <a href="/index.html">Back to Main Page</a>');
});

const PORT = process.env.PORT || 8000;
app.listen(PORT);