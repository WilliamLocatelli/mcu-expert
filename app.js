'use strict';

/*const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});*/
const path = require('path')
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
        //const client = await pool.connect();
        //const titles = await client.query("SELECT title, series, release_date FROM films ORDER BY series");
        //client.release();
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

app.post('/results/', async function (req, res) {
    try {
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
    } catch(err) {
        res.status(500).json({'error': 'Internal server error'});
    }
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