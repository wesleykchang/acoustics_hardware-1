window.name='logfile'
//Make Header (just edit to change structure of table, nothing else needs to be changed in this file)
var fields ="Start Date, Test ID, Serial Number, Mode (tr/pe), Channel, Channel 2,	Gain (dB),	Delay (us),	Time (us),Freq (MHz), Notes"
//Collect Elements to Play with Later
var $TABLE = $('#table');
var $BTN = $('#export-btn');
var $EXPORT = $('#export');

//Add code here to make table
fields = fields.split(",")
for (f in fields) fields[f] = fields[f].replace(/\s+/g,"")
fields.push("")
header = ""
for (f in fields) header += "<th>"+fields[f]+"</th>"
$("#header").html(header)


//Make Clone Basis
//This is a hack but so far it doesn't break.  The idea is that we create an empty hidden row that's read to go when we hit "add".  This has been modified to scale appropriately to the size of the header and autofill the table on load

//glyphs, icons from jquery-ui 
trashbtn = "<span class='test-figs glyphicon glyphicon-picture'></span><span class='test-delete glyphicon glyphicon-trash'></span>"

//make the clone structure the size of the fields
clone_arr = [] 
for (var i=2; i < fields.length; i++ ) clone_arr.push("")
clone_arr[clone_arr.length-1] = trashbtn // add trash button


//Turn the array into HTML
cloner = "<td contenteditable=false></td><td contenteditable=false></td>"
for (c in clone_arr) 
{
    var ce = "false"
    if (clone_arr[c] == "") ce = "false" 
    cloner += "<td contenteditable='"+ce+"'>"+clone_arr[c]+"</td>"
}
$("#cloner").html(cloner)

//Load the data
loadsettings()


//Basic data read library
function loadsettings()
{
$.get("table_load",
    function(logfile)
    {
        out = JSON.parse(logfile)
        
        //Attempt to fill ports based on JSON data

        data = out['data']
        for (d in data)
        {
            makerow(data[d])
        }
    })
}



$('.test-delete').click(function () {
    var $row = $(this).parents('tr')
    var id = $row[0].getAttribute('rowid')

    $.post("del_test",JSON.stringify({'rowid' : id}),
        function()
        {
         $row.detach();
        })
    });


$('.test-figs').click(function () {
    // var input = '/'  + document.getElementById("datepicker").value;
    var $row = $(this).parents('tr')
    var id = $row[0].getAttribute('rowid')
    // var link = ('http://' + document.domain + ':' + location.port + '/viewfigs');
    var link = ('/viewfigs?testid=' + id);
    window.open(link, '_blank');
    });


function makerow(p) {

    //get the structure of the row

    var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line');

    //fill in the row with values

    for (var i = 0; i < fields.length-1; i++) $clone[0].cells[i].innerHTML = p[fields[i].toLowerCase()]

        //append the row to the table

    $clone[0].setAttribute('rowid',p['testid'])
    $clone[0].setAttribute('run',p['run(y/n)'])

    $TABLE.find('table').append($clone);

}
