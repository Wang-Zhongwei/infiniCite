// @ts-nocheck
// get the data

const nodes = JSON.parse(document.getElementById('nodes').textContent);
const links = JSON.parse(document.getElementById('edges').textContent);

nodes.forEach(function(d) {
    d.x = Math.random() * width;
    d.y = Math.random() * height;
  });
  
  
  // get the range of years
  const years = nodes.map((node) => node.year);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  
  const yearScale = d3.scaleLinear().domain([minYear, maxYear]).range([0, 1]);
  
  // Use the year scale to choose between the blue and red color scales
  const colorScale = function (year) {
    var scaledYear = yearScale(year);
    return d3.scaleLinear().domain([1.2, -0.2]).range(["blue", "white"])(
      scaledYear
    );
  };
  
  const maxCitationCount = Math.max(...nodes.map((node) => node.citationCount));
  const logScale = d3
    .scaleLog()
    .domain([1, maxCitationCount + 1])
    .range([10, 30]);
  const radiusScale = function (citationCount) {
    return logScale(citationCount + 1);
  };
  
  // create a svg
  var svg = d3.select("#graph"),
    width = svg.attr("width"),
    height = svg.attr("height");
  
  // create a force simulation
  var simulation = d3
    .forceSimulation(nodes)
    .force(
      "link",
      d3.forceLink(links).id((d) => d.id)
    )
    .velocityDecay(.9)
    .force("charge", d3.forceManyBody().strength(-100))
    .force("collide", d3.forceCollide(60))
  
    .force("center", d3.forceCenter(width / 2, height / 2));
  
  const linkTypes = ["empty", "background", "methodology", "result"];
  const flatLinks = [];
  links.forEach((link) => {
    const flatLink = {
      source: link.source,
      target: link.target,
    };
    if (link.type.length === 0) {
      flatLink.type = "empty";
      flatLinks.push({ ...flatLink });
    } else {
      link.type.forEach((type) => {
        flatLink.type = type;
        flatLinks.push({ ...flatLink });
      });
    }
  });
  
  const linkTypeScale = d3
    .scaleOrdinal()
    .domain(linkTypes)
    .range(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]);
  
  svg
    .append("defs")
    .selectAll("marker")
    .data(linkTypes) // Different link/path types can be defined here
    .enter()
    .append("marker") // This section adds in the arrows
    .attr("id", (d) => d)
    .attr("viewBox", "0 0 8 8")
    .attr("refX", 8) // Controls the shift of the arrowhead along the path
    .attr("refY", 4)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("orient", "auto")
    .attr("fill", "#888")
    .append("svg:path")
    .attr("d", "M 0 0 L 8 4 L 0 8 z");
  
  // Add the links as path elements with arrowhead markers
  var link = svg
    .append("g")
    .selectAll("line")
    .data(flatLinks)
    .join("line")
    .attr("stroke-width", 3)
    .attr("marker-end", function (d) {
      return "url(#" + d.type + ")";
    })
    .attr("stroke", (d) => linkTypeScale(d.type));
  
  // Create a tooltip div that is hidden by default:
  var tooltip = d3
    .select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("background", "#fff")
    .style("border", "solid")
    .style("border-width", "1px")
    .style("border-radius", "5px")
    .style("padding", "10px");
  
  // create nodes
  // define the glow filter in your SVG definition section
  var defs = svg.append("defs");
  var filter = defs.append("filter").attr("id", "glow");
  filter
    .append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");
  var feMerge = filter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");
  
  // within your node definition
  var node = svg
    .append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", (d) => radiusScale(d.citationCount))
    .attr("fill", (d) => colorScale(d.year))
    .call(drag(simulation))
    .on("mouseover", function (d) {
      // When the mouse goes over a node
      tooltip.text(d.title).style("font-size", "20px"); // Increase the font size
      d3.select(this)
        .style("filter", "url(#glow)") // Apply the glow effect
        .attr("stroke-width", "2px") // Optional: increase stroke width to make the node more highlighted
        .attr("stroke", "green"); // Optional: add stroke color to highlight the node
  
      // highlight connected edges
      d3.selectAll("line").style("stroke", (l) =>
        l.source === d || l.target === d ? "rgb(145, 196, 104)" : "#999"
      );
  
      return tooltip.style("visibility", "visible");
    })
    .on("mousemove", function () {
      return tooltip
        .style("top", d3.event.pageY - 10 + "px")
        .style("left", d3.event.pageX + 10 + "px");
    })
    .on("mouseout", function (d) {
      d3.select(this)
        .style("filter", null) // Remove the glow effect
        .attr("stroke-width", "0px"); // Optional: set stroke width back to 0
      d3.selectAll("line").style("stroke", (l) => linkTypeScale(l.type));
      return tooltip.style("visibility", "hidden");
    });
  
  const labels = svg
    .append("g")
    .selectAll("text")
    .data(nodes)
    .enter()
    .append("text")
    .text(function (d) {
      return d.year + "\n" + d.authors[0].name;
    })
    .style("text-anchor", "middle")
    .style("fill", "#000")
    .style("font-family", "Arial")
    .style("font-size", 12);
  
  // add titles to nodes
  node.append("title").text((d) => d.id);
  
  // add tick function
  simulation.on("tick", () => {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr(
        "x2",
        (d) =>
          d.target.x -
          radiusScale(d.target.citationCount) *
            Math.cos(Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x))
      )
      .attr(
        "y2",
        (d) =>
          d.target.y -
          radiusScale(d.target.citationCount) *
            Math.sin(Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x))
      );
  
    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    labels.attr("x", (d) => d.x).attr("y", (d) => d.y);
  });
  
  // add drag functions
  function drag(simulation) {
    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
  
    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }
  
    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  
    return d3
      .drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }
  
  
  