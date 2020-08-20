'use strict';

const express = require('express');
const {spawn} = require('child_process');
const app = express();
const sqlite3 = require('sqlite3');
const sqlite = require('sqlite');
const multer = require('multer');

app.use(express.urlencoded({extended: true}));
app.use(express.json());
app.use(multer().none());

app.get('/main/', async function(req, res) {
    try {
        let db = await getDBConnection();
        let titles = await db.all("SELECT Title, Series, ReleaseDate FROM Films ORDER BY Series");
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

app.get('/results', async function (req, res) {

});

async function getDBConnection() {
  const db = await sqlite.open({
    filename: 'FilmData.db',
    driver: sqlite3.Database
  });
  return db;
}


app.use(express.static("public"));
const PORT = process.env.PORT || 8000;
app.listen(PORT);