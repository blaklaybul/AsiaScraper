var Graph = function(industry) {

var w = 300,
    h = 300,
    fill = d3.scale.category20();

var vis = d3.select("body")
  .append("div")
  .style("float","left")
  .attr("id", industry)
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h);

var file = "force_" + industry + ".json"

d3.json(file, function(json) {

  var node_scale = d3.scale.linear()
                    .domain([1, d3.max(json.nodes, function(d) { return d["degree"]; })])
                    .range([2,10]);

  var force = d3.layout.force()
      .charge(-10)
      .linkDistance(20)
      .nodes(json.nodes)
      .links(json.links)
      .size([w, h])
      .start();

  var link = vis.selectAll("line.link")
      .data(json.links)
    .enter().append("svg:line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); })
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  var node = vis.selectAll("circle.node")
      .data(json.nodes)
    .enter().append("svg:circle")
      .attr("class", "node")
      .attr("class", function(d){ return d.group})
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", function(d) {return node_scale(d.degree)})
      .attr("country", function(d){return d.location;})
      .style("fill", function(d) { return fill(d.location); })
      .call(force.drag);

  node.append("svg:title")
      .text(function(d) { return d.location; });

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);

    d3.select("#"+industry)
    .append("div")
    .text(industry)
    .style("text-align", "center");


  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  });
});

};

var graph1 = new Graph("Shopping")
var graph2 = new Graph("Games")
var graph3 = new Graph("SaaS")
var graph4 = new Graph("News")
