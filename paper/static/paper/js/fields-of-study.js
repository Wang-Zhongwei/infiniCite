// @ts-nocheck

window.onload = function () {
  var colorMap = {
    a: "#990000",
    b: "#3770d2",
    c: "#009999",
    d: "#000025",
    e: "#998200",
    f: "#0e390e",
    g: "#4d4d4d",
    h: "#ff0381",
    i: "#10001c",
    j: "#e4d232",
    k: "#5fb2ce",
    l: "#009900",
    m: "#c358a3",
    n: "#00001a",
    o: "#1a1a00",
    p: "#c537d2",
    q: "#ff5a76",
    r: "#990000",
    s: "#8d8d8d",
    t: "#001a1a",
    u: "#1a001a",
    v: "#e228e2",
    w: "#e9b759",
    x: "#000000",
    y: "#999900",
    z: "#8affff",
  };

  var fields = document.getElementsByClassName("field-of-study");
  for (var i = 0; i < fields.length; i++) {
    var firstLetter = fields[i].innerText.charAt(0).toLowerCase();
    fields[i].style.backgroundColor = colorMap[firstLetter]
      ? colorMap[firstLetter]
      : "#808080";
  }
};