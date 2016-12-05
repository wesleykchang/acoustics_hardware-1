// URL = window.location.href 
// var myVar = fields;
// alert(fields)

var query = window.location.search.substring(1);
var parameters = {};
var keyValues = query.split('&');
var lenfigs = 0

for (var keyValue in keyValues) {
    var keyValuePairs = keyValues.toString().split('=');
    var key = keyValuePairs[0];
    var value = keyValuePairs[1];
    parameters[key] = value;
}

var testID = "TestID_" + parameters['testid'];
loadfig("0")

function mod(n, m) {
  return ((n % m) + m) % m;
}

$('#left-btn').click(function () {
  current = $("#figindex").val().split("/")
  updated = mod(parseInt(current[0])-1, (parseInt(current[1])+1))
  $("#figindex").val(updated.toString() + "/" + current[1]);
  loadfig(updated.toString())
});

$('#right-btn').click(function () {
  current = $("#figindex").val().split("/")
  updated = mod(parseInt(current[0])+1, (parseInt(current[1])+1))
  $("#figindex").val(updated.toString() + "/" + current[1]);
  loadfig(updated.toString())
});

$("#figindex").keyup(function (e) {
    if (e.keyCode == 13) {
        value = $("#figindex").val().split("/")
        loadfig(value[0])
    }
});



function loadfig(index) {  
  $.get(testID + "/makefigs", {'index': index},
      function(data)
      {
         console.log(data);
         out = JSON.parse(data)
         d3.select("#fig01").selectAll("*").remove();
         mpld3.draw_figure("fig01",out['fig1']);
         $("#figindex").val(out['lenfigs'][0] + "/" + out['lenfigs'][1]);
         lenfigs = (out['lenfigs'][1])
         if (lenfigs >= 1500){
          $('#fig02').text("Loading waterfall")
          loadwaterfall()
        }
        else{
          $('#fig02').text("Insufficient waves for waterfall")
        }

      })
}

function loadwaterfall() {
  $.get(testID + "/makewaterfall",
      function(data)
      {
        out = JSON.parse(data)
        mpld3.draw_figure("fig02",out['fig02']);
      })
}


