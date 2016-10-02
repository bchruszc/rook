queue()
    .defer(d3.json, "/donorschoose/projects")
    .defer(d3.json, "static/geojson/us-states.json")
    .await(makeGraphs);
    
function makeGraphs(error, projectsJson, statesJson) {
    
};