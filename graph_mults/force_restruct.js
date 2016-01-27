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
    fillScale = d3.scale.category10().domain(countries)
    .range(["#5DA5DA","#FAA43A","#60BD68","#F17CB0","#B2912F","#B276B2","#DECF3F","#F15854","#4D4D4D",'#3182bd','#6baed6','#9ecae1','#c6dbef','#e6550d','#fd8d3c','#fdae6b','#fdd0a2','#31a354','#74c476','#a1d99b','#c7e9c0','#756bb1','#9e9ac8','#bcbddc','#dadaeb','#636363','#969696','#bdbdbd','#d9d9d9' ]);;
    console.log(fillScale.domain());
    console.log(fillScale.range());
    // d3.json("http://localhost:5000/industries?top=10", function(json){
    //         top_industries = json.industries;
    //         buildGraphs(top_industries,2);
    // })
    buildGraphs();
}

function buildGraphs(){
    // for( i = 0; i < top_industries.length; i++){
    //     console.log(top_industries[i]);
    //     new Graph(top_industries[i],subgraphs);
    // }
   var graph7 = new Graph("E-Commerce Platforms",12);
   var graph2 = new Graph("Games",12);
   var graph3 = new Graph("SaaS",12);
   var graph4 = new Graph("News",12);
   var graph5 = new Graph("Education Tech",12);
   var graph6 = new Graph("Software",12);
   var graph7 = new Graph("Fashion",12);
   var graph7 = new Graph("Digital Media",12);
   var graph7 = new Graph("Restaurants and food",12);
   var graph7 = new Graph("Web Design",12);
   var graph7 = new Graph("Financial Services",12);
   var graph7 = new Graph("Enterprise Software",12);
   var graph7 = new Graph("Social Media",12);
   var graph7 = new Graph("Transportation",12);
   var graph7 = new Graph("Social Networking",12);
   var graph7 = new Graph("Human Resource",12);
   var graph7 = new Graph("Shopping",12);
   var graph7 = new Graph("Services",12);
   var graph7 = new Graph("Health Care",12);


}

var Graph = function(industry, subgraphs) {

var w = 400,
    h = 400


var vis = d3.select("body")
  .append("div")
  .style("float","left")
  .attr("id", industry.replace(/ /g,"_"))
  .append("svg:svg")
  .attr("width", w)
  .attr("height", h);

var file = "http://localhost:5000/industryGraph/" + industry + "?subgraphs=" + subgraphs

d3.json(file, function(json) {

  console.log("JSON: ", json);


  var node_scale = d3.scale.linear()
                    .domain([0, d3.max(json.nodes, function(d) { return d["degree"]; })])
                    .range([3,10]);

    console.log(node_scale.domain())
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
      .style("stroke-width", function(d){return d.value;})
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
      .attr("r", function(d){ return d.group == 2 ? 2 : node_scale(d.degree)}) //function(d) {return node_scale(d.cent_deg)})
      .attr("country", function(d){return d.location;})
      .style("fill", function(d) { return fillScale(d.location); })
      .style("stroke", function(d){return d.group == 2 ? "black" : undefined })
      .call(force.drag);

  node.append("svg:title")
      .text(function(d) { return d.coname + ": " + d.location; });

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);


    d3.select("#"+industry.replace(/ /g,"_"))
    .append("div")
    .text(industry + "(" + Math.round(json.frac*100,3) + "%)")
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
