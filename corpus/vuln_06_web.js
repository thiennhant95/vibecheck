// Planted flaws (JS): cors-wildcard, js-eval, debug-log
const express = require("express");
const app = express();

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  next();
});

app.get("/run", (req, res) => {
  const result = eval(req.query.code);
  console.log("result", result);
  res.send(String(result));
});

module.exports = app;
