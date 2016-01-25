// load data first separately

// make call to countries API to get full list of countries. this allows to set
// color scale before we create the graphs

// var color = function() {
//
//     var data;
//
//     return d3.json("http://localhost:5000/countries", GetFill);
//
//     function GetFill(jsonData){
//
//         // this.fill = d3.scale.category20()
//         //     .domain(jsonData.countries);
//
//         data = jsonData.countries;
//         return data;
//     }
//
// };

    // function(json){
    //     fill = d3.scale.category20()
    //             .domain(json.countries);
    //     setFill();
    //         })
    //
    // function setFill(){
    //     var obj = {
    //         fill: fill
    //     };
    //     return obj;
    //     }
    // return setFill();
    // };
    //
    // return getit()

var Graph = function(industry, subgraphs) {

var w = 300,
    h = 300,
    fill = d3.scale.category10();

var vis = d3.select("body")
  .append("div")
  .style("float","left")
  .attr("id", industry.replace(" ","_"))
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h);

var file = "http://localhost:5000/industryGraph/" + industry + "?subgraphs=" + subgraphs

d3.json(file, function(json) {

  var node_scale = d3.scale.linear()
                    .domain([1, d3.max(json.nodes, function(d) { return d["degree"]; })])
                    .range([2,9]);

  var force = d3.layout.force()
      .charge(-10)
      .linkDistance(15)
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


    d3.select("#"+industry.replace(" ","_"))
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
var graph1 = new Graph("Shopping",1);
var graph2 = new Graph("Games",1);
var graph3 = new Graph("SaaS",1);
var graph4 = new Graph("News",1);
var graph5 = new Graph("Education Tech",1);
var graph6 = new Graph("Software",1);
var graph7 = new Graph("Fashion",1);
var graph7 = new Graph("Services",1);
