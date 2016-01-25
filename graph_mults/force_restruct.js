//globals
var fillScale = undefined;

function init(){
    //load countries data
    d3.json("http://localhost:5000/countries", function(json){
        countries = json.countries;
        buildFillScale(countries)
    })
    //build Graphs
}

function buildFillScale(countries){
    fillScale = d3.scale.category10().domain(countries);
    buildGraphs()
}

function buildGraphs(){
    var graph2 = new Graph("Games",1);
    var graph3 = new Graph("SaaS",1);
    var graph4 = new Graph("News",1);
    var graph5 = new Graph("Education Tech",1);
    var graph6 = new Graph("Software",1);
    var graph7 = new Graph("Fashion",1);
    var graph7 = new Graph("Digital Media",1);
    var graph7 = new Graph("Restaurants and food",1);
    var graph7 = new Graph("Web Design",1);
    var graph7 = new Graph("Financial Services",1);
    var graph7 = new Graph("Enterprise Software",1);
    var graph7 = new Graph("Social Media",1);
    var graph7 = new Graph("Transportation",1);
    var graph7 = new Graph("Social Networking",1);
    var graph7 = new Graph("Human Resource",1);
    var graph7 = new Graph("Shopping",1);
    var graph7 = new Graph("Services",1);
    var graph7 = new Graph("Health Care",1);
}

var Graph = function(industry, subgraphs) {

var w = 250,
    h = 250


var vis = d3.select("body")
  .append("div")
  .style("float","left")
  .attr("id", industry.replace(/ /g,"_"))
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h);

var file = "http://localhost:5000/industryGraph/" + industry + "?subgraphs=" + subgraphs

d3.json(file, function(json) {

  var node_scale = d3.scale.linear()
                    .domain([0, d3.max(json.nodes, function(d) { return d["cent_deg"]; })])
                    .range([3,10]);
    console.log(node_scale.domain())
  var force = d3.layout.force()
      .charge(-5)
      .linkDistance(15)
      .nodes(json.nodes)
      .links(json.links)
      .size([w, h])
      .start();

  var link = vis.selectAll("line.link")
      .data(json.links)
    .enter().append("svg:line")
      .attr("class", "link")
      .style("stroke-width", 3)
      .style("stroke", "black")
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
      .attr("r", function(d) {return node_scale(d.cent_deg)})
      .attr("country", function(d){return d.location;})
      .style("fill", function(d) { return fillScale(d.location); })
      .style("stroke", function(d){return d.group == 1 ? "black" : undefined })
      .call(force.drag);

  node.append("svg:title")
      .text(function(d) { return d.location; });

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);


    d3.select("#"+industry.replace(/ /g,"_"))
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

init()
