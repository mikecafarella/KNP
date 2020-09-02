var svg = d3.select("svg");

var width = svg.attr("width");
var height = svg.attr("height");

svg = svg.call(d3.zoom().on("zoom", zoomed)).append("g");

svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

var color = d3.scaleOrdinal(d3.schemeCategory10);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(width / 2, height / 2));



d3.json("zoom_forced_modified_var_val.json", createGraph );

function createGraph(error, graph) {
    if (error) throw error;

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke", function (d) {
            return color(d.type);
        })
        .attr("marker-end", "url(#arrow)");


    var KGPLVar = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.var)
        .enter().append("circle")
        .attr("r", 10)
        .attr("fill", function (d) {
            if (d.root == "true") return color(d.root);
            return color(d.type);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));


    var KGPLVal = svg.append("g")
        .attr("class", "nodes")
        .selectAll("rect")
        .data(graph.val)
        .enter().append("rect")
        .attr("width", 20)
        .attr("height", 20)
        .attr("fill", function (d) {
            if (d.root == "true") return color(d.root);
            return color(d.type);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // var all_nodes = graph.var;
    // console.log(graph.var);
    const all_nodes = graph.var.concat(graph.val);
    // console.log("above is graph.var");

    // console.log(all_nodes);

    var text = svg.append("g").attr("class", "labels").selectAll("g")
        .data(all_nodes)
        .enter().append("g")
        .append("text")
        .attr("x", 14)
        .attr("y", ".31em")
        .style("font-family", "sans-serif")
        .style("font-size", "0.7em")
        .text(function (d) {
            var a = d.id;
            var b = d.creater;
            var c = "\n";
            var t = a.concat(c);
            return t.concat(b);
        });

    KGPLVal.on("click", function (d) {
        console.log("clicked", d.id);
    });


    KGPLVal.append("title")
        .text(function (d) {
            return d.id;
        });

    KGPLVar.append("title")
        .text(function (d) {
            return d.id;
        });
    simulation
        .nodes(all_nodes)
        .on("tick", ticked);
    console.log(graph.links);
    simulation.force("link")
        .links(graph.links);


    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        KGPLVar
            .attr("cx", function (d) {
                return d.x;
            })
            .attr("cy", function (d) {
                return d.y;
            });
        KGPLVal
            .attr("x", function (d) {
                return d.x-10;
            })
            .attr("y", function (d) {
                return d.y-10;
            });
        text
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })


    }
}


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

function zoomed() {
    svg.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ")" + " scale(" + d3.event.transform.k + ")");
}

/*
var data = {
    "val": [
        {
            "id": "val/0",
            "type": 1,
            "creater":"UserA"
        },
        {
            "id": "val/1",
            "type": 1,
            "creater":"UserA"
        }],
    "var": [{
        "id": "var/0",
        "type": 2,
        "creater":"UserB"
    }],
    "links": [
        {
            "source": "var/0",
            "target": "val/1",
            "type": 1
        }]
};*/

// createGraph(false, data);