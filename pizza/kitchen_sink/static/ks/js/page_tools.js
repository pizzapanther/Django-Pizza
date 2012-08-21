var edit_tb = '<div draggable="true" id="edit_tb">\
  {{=select}}&nbsp; -&nbsp; <button>Save</button>\
</div>';
edit_tb = new t(edit_tb);

var edit_select = '<select id="region_select" onchange="edit_region()">\
<option>Select a Region to Edit</option>\
{{@regions}}<option value="{{=_key}}">{{=_val.dname}}</option>{{/@regions}}\
</select>';
edit_select = new t(edit_select);

function load_edit_tools () {
  if (jQuery.cookie('PIZZA_EDIT') == 'ON') {
    var select = edit_select.render({regions: pizzaContext});
    jQuery('body').append(edit_tb.render({select: select}));
    
    var dm = document.getElementById('edit_tb'); 
    dm.addEventListener('dragstart',drag_start,false);
    document.body.addEventListener('dragover',drag_over,false); 
    document.body.addEventListener('drop',drop,false); 
  }
}

function edit_region () {
  var key = jQuery("#region_select").val();
  if (key != "") {
    if (pizzaContext[key].etype == 'rich') {
      jQuery('#id_' + key).redactor({ focus: true });
    }
  }
}

function drag_start(event) {
    var style = window.getComputedStyle(event.target, null);
    event.dataTransfer.setData("text/plain",
    (parseInt(style.getPropertyValue("left"),10) - event.clientX) + ',' + (parseInt(style.getPropertyValue("top"),10) - event.clientY));
}

function drag_over(event) { 
    event.preventDefault(); 
    return false; 
}

function drop(event) { 
    var offset = event.dataTransfer.getData("text/plain").split(',');
    var dm = document.getElementById('edit_tb');
    dm.style.left = (event.clientX + parseInt(offset[0],10)) + 'px';
    dm.style.top = (event.clientY + parseInt(offset[1],10)) + 'px';
    event.preventDefault();
    return false;
}
