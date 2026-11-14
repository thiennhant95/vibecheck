// Clean JS with bait strings. Expected: ZERO findings.
const HELP = "Avoid eval() and new Function() in production code";
const REGEX = /eval\(/g;

function sum(items) {
  return items.reduce((acc, it) => acc + it.price, 0);
}

function safeParse(text) {
  return JSON.parse(text);
}

module.exports = { sum, safeParse };
