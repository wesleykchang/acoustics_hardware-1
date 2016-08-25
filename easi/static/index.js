//Make Header (just edit to change structure of table, nothing else needs to be changed in this file)
var fields ="Start Date, Test ID, LastWaveform, Serial Number, Mode (tr/pe), Channel, Channel 2,	Gain (dB),	Delay (us),	Time (us),Freq (MHz), Notes, Filter Mode, Run (y/n)"
//Collect Elements to Play with Later
var $TABLE = $('#table');
var $BTN = $('#export-btn');
var $EXPORT = $('#export');

//Add code here to make table
fields = fields.split(",")
for (f in fields) fields[f] = fields[f].replace(/\s+/g,"")
fields.push("")
fields.push("")
fields.push("")
header = ""
for (f in fields) header += "<th>"+fields[f]+"</th>"
$("#header").html(header)

//Make Clone Basis
//This is a hack but so far it doesn't break.  The idea is that we create an empty hidden row that's read to go when we hit "add".  This has been modified to scale appropriately to the size of the header and autofill the table on load

//glyph's, icons from jquery-ui -> may want to change at some point
upbut =  '<span class="table-up glyphicon glyphicon-arrow-up">'
updownbut = '<span class="table-up glyphicon glyphicon-arrow-up"></span> <span class="table-down glyphicon glyphicon-arrow-down"></span>'
removebut =   "<span class='table-remove glyphicon glyphicon-remove'></span>"
playbut = "<span class='test-start glyphicon glyphicon-play'></span>"
playstopbut = "<span class='test-start glyphicon glyphicon-play'></span><span class = 'test-singleshot glyphicon glyphicon-chevron-right'></span><span class = 'test-stop glyphicon glyphicon-stop'></span>"

//make the clone structure the size of the fields
clone_arr = [] 
for (var i=3; i < fields.length-1; i++ ) clone_arr.push("")
clone_arr[clone_arr.length-3] = playstopbut //add play button
clone_arr[clone_arr.length-2] = removebut //add remove button
clone_arr[clone_arr.length-1] = updownbut // add updown button

//Turn the array into HTML
cloner = "<td contenteditable=false></td><td contenteditable=false></td><td kind=LastWaveform contenteditable=false></td>"
for (c in clone_arr) 
{
    var ce = "false"
    if (clone_arr[c] == "") ce = "true" 
    cloner += "<td contenteditable='"+ce+"'>"+clone_arr[c]+"</td>"
}
$("#cloner").html(cloner)

//Load the data
last_tid = 000000 //initialize the last testID to something
loadsettings()

//Ye Olde code (from https://codepen.io/anon/pen/PzEgLN)
$('.table-add').click(function () {
  var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line');
  $TABLE.find('table').append($clone);
});

$('.table-remove').click(function () {
    console.log(this)
  $(this).parents('tr').detach();
  sendsettings(last_tid)
});

$('.table-up').click(function () {
  var $row = $(this).parents('tr');
  if ($row.index() === 1) return; // Don't go above the header
  $row.prev().before($row.get(0));
  sendsettings(last_tid)
});

$('.table-down').click(function () {
  var $row = $(this).parents('tr');
  $row.next().after($row.get(0));
  sendsettings(last_tid)
});

$('.test-start').click(function () {
  var d = new Date().toString(); //return current y,m,d
  var $row = $(this).parents('tr');

  // alert('Please stop test before starting a new one')
  // alert($row[0].getAttribute('run'))
  if ($row[0].getAttribute('run') == 'y'){
    alert('Please stop current test before starting a new one')
    return;
  }

  $tds = $row.find("td:nth-child(1)"); //find startdate
  $tid = $row.find("td:nth-child(2)"); //find testid

  $.each($tds, function() {
      $(this).html(d.slice(4,24));
  });

  current_tid = last_tid + 1;

  $.each($tid, function() {
      $(this).html((current_tid).toString());
  });

  last_tid = current_tid;

  //for exporting whether or not to run
  $row[0].setAttribute('run','y')
  $row[0].setAttribute('rowid',current_tid.toString())
  $row[0].setAttribute('active','false')

  //to 'lock' the row while a test is running
  $row.each(function () {
    var $td = $(this).find('td');
    $td.each(function(){
      $(this).attr('contenteditable','false')
    });
  }); 
  sendsettings(last_tid) 
});

$('.test-stop').click(function () {
  var $row = $(this).parents('tr');
  stopRow($row)
});

function stopRow(row){
  row[0].setAttribute('run','n');

  //to 'unlock' a row when a test is finished.
  row.each(function () {
    var $td = row.find('td').slice(3,13);
    $td.each(function(){
      $(this).attr('contenteditable','true')
    });
  });
  sendsettings(last_tid)
  }


$('.test-singleshot').click(function () {
  var d = new Date().toString(); //return current y,m,d
  var $row = $(this).parents('tr');

  // alert('Please stop test before starting a new one')
  // alert($row[0].getAttribute('run'))
  if ($row[0].getAttribute('run') == 'y'){
    alert('Please stop current test before starting a new one')
    return;
  }

  $tds = $row.find("td:nth-child(1)"); //find startdate
  $tid = $row.find("td:nth-child(2)"); //find testid

  $.each($tds, function() {
      $(this).html(d.slice(4,24));
  });

  current_tid = last_tid + 1;

  $.each($tid, function() {
      $(this).html((current_tid).toString());
  });

  last_tid = current_tid;

  //for exporting whether or not to run
  $row[0].setAttribute('run','y')
  $row[0].setAttribute('rowid',current_tid.toString())
  $row[0].setAttribute('active','false')
  $row[0].setAttribute('singleshot','true')

  //to 'lock' the row while a test is running
  $row.each(function () {
    var $td = $(this).find('td');
    $td.each(function(){
      $(this).attr('contenteditable','false')
    });
  }); 
  sendsettings(last_tid) 
});

// A few jQuery helpers for exporting only
jQuery.fn.pop = [].pop;
jQuery.fn.shift = [].shift;

//export button
$BTN.click(function () {
sendsettings(last_tid) //DS Addition
});

//function to add data from rows to ports, make a JSON object, send off
function sendsettings(last_tid)
{

  var $rows = $TABLE.find('tr:not(:hidden)');
  var headers = [];
  var data = [];
  
  // Get the headers (add special header logic here)
  $($rows.shift()).find('th:not(:empty)').each(function () {
    headers.push($(this).text().toLowerCase());
  });
  
  // Turn all existing rows into a loopable array
  $rows.each(function () {
    var $td = $(this).find('td');
    var h = {};
    // Use the headers from earlier to name our hash keys
    headers.forEach(function (header, i) {
      h[header] = $td.eq(i).text();
    });
    h["run(y/n)"] = $(this).attr('run')

    //yes we need this.
    if (this.hasAttribute('singleshot')){
      h["singleshot"] = $(this).attr('singleshot')
    }

    data.push(h);
  });
  
  out = {} //define the output JSON

  //Gets all ids matching "port" and fills JSON accordling
  ports = $('input[id$="_port"]')
  for (p = 0; p < ports.length; p++){
    out[ports[p].id] = $('#'+ports[p].id).val()
  }
  out['last_tid'] = last_tid
  out['data'] = data
  // Output the result

  json_str = JSON.stringify(out)

  $.post("/table_save",json_str,
        function(data)
        {
         data = JSON.parse(data)
         $EXPORT.text(data['status'])
         $EXPORT.fadeTo(200, 1).fadeTo(800, 0);
        })

}


//ye new code to make it rain

//Basic data read library
function loadsettings()
{
$.get("/table_load",
    function(data)
    {
        out = JSON.parse(data)

        last_tid = (parseInt(out['last_tid']))
        
        //Attempt to fill ports based on JSON data
        ports = $('input[id$="_port"]')
        for (p = 0; p < ports.length; p++)
        {
            $('#'+ports[p].id).val(out[ports[p].id])        
        }

        data = out['data']
        for (d in data)
        {
            makerow(data[d])
        }
    })
}


function makerow(p) {

    //get the structure of the row

    var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line');

    //fill in the row with values

    for (var i = 0; i < fields.length - 4; i++) $clone[0].cells[i].innerHTML = p[fields[i].toLowerCase()]

        //append the row to the table

    $clone[0].setAttribute('rowid',p['testid'])
    $clone[0].setAttribute('run',p['run(y/n)'])
    $clone[0].setAttribute('active','false')
    // if (p['singleshot'] != undefined){
    //   $clone[0].setAttribute('singleshot',p['singleshot'])
    // }

    if (p['run(y/n)'] == 'y'){
      for (var i = 0; i < fields.length - 4; i++) $clone[0].cells[i].setAttribute('contenteditable','false')
    }

    $TABLE.find('table').append($clone);

}


last_rowid = 0;


var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('active',function(data){
    current_rowid = data['rowid']        
    $('tr').attr('active','false'); //turn off previous active row
    $('[rowid="' + current_rowid + '"]').attr('active','true');
});


socket.on('update',function(data){
    current_rowid = data['rowid']
    var current_row = $('[rowid="' + current_rowid + '"]')
    console.log(current_rowid)
      var attr = current_row.attr('singleshot');
      console.log(attr);

      if (typeof attr !== typeof undefined && attr !== false) {
         console.log('hi')
          stopRow(current_row);
          current_row.removeAttr('singleshot')
      }

    var ymin = Math.min.apply(Math, data['amp'])
    var ymax = Math.max.apply(Math, data['amp'])

    ins = "<div style='text-align:right; vertical-align:middle;'><span class='inlinespark'></span></div>"
    $("tr[rowid='" + current_rowid + "'] td[kind='LastWaveform']").html(ins)
    $("tr[rowid='" + current_rowid + "'] td[kind='LastWaveform']").sparkline(data['amp'], {
            type: 'line',
            width: '100',
            height: '50',
            fillColor: false,
            lineColor: "black",
            lineWidth: 1.5,
            spotRadius: 2,
            chartRangeMin: ymin,
            chartRangeMax: ymax
        });

    last_rowid = current_rowid
});