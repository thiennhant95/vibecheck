// Demo: AI-generated Node.js endpoint with classic mistakes
const express = require("express");
const app = express();

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  next();
});

app.get("/run", (req, res) => {
  // FIXME: sanitize input later
  const result = eval(req.query.code);
  console.log("result", result);
  res.send(String(result));
});

app.post("/login", (req, res) => {
  const password = "admin12345678";
  res.send("ok " + password);
});

module.exports = app;
