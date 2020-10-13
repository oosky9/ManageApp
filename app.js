
const express = require('express');
const sqlite3 = require('sqlite3');

const port = 3000;

const app = express();

const db_parameter = new sqlite3.Database('D:\\Research\\Database\\parameter.db');

app.use(express.static('public'));

app.get('/', (req, res) => {

  db_parameter.serialize(()=>{
    db_parameter.all("select name from sqlite_master where type='table';", (err, results)=>{
      res.render('top.ejs', {items: results});
    });

  });
});

app.post('/table/:name', (req, res) => {

  var tb_name = req.params.name;

  db_parameter.serialize(()=>{
    db_parameter.all(`select * from ${tb_name} ;`, (err, results)=>{
      res.render('table.ejs', {tb_title: tb_name, params: results})
    });
  });

});

app.listen(port);