// get the data
var nodes = [
    {id: "Node 1", group: 1},
    {id: "Node 2", group: 2},
    {id: "Node 3", group: 2},
    {id: "Node 4", group: 3}
  ];
  
  var links = [
    {source: "Node 1", target: "Node 2", value: 1},
    {source: "Node 2", target: "Node 3", value: 2},
    {source: "Node 3", target: "Node 4", value: 3}
  ];
  
  // create a svg
  var svg = d3.select("svg"),
      width = +svg.attr("width"),
      height = +svg.attr("height");
  
  // create a color scale
  var color = d3.scaleOrdinal(d3.schemeCategory10);
  
  // create a force simulation
  var simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(width / 2, height / 2));
  
  // create links
  var link = svg.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-width", d => Math.sqrt(d.value));
  
  // create nodes
  var node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .text(d => d.id)
      .attr("r", 10)
      .attr("fill", d => color(d.group))
      .call(drag(simulation));
  
  // add titles to nodes
  node.append("title")
      .text(d => d.id);
  
  // add tick function
  simulation.on("tick", () => {
      link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
  
      node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);
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
      
      return d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended);
  }
  
  