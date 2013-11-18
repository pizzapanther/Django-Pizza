var img_picker_editor = null;
var IMAGE_URL = location.href + '../../../kitchen_sink/image/';

CKEDITOR.plugins.add('pizzaimage', {
  init: function( editor ) {
    var url = IMAGE_URL + '?t=id';
    var html = '<div style="display: none;">'
    html += '<input id="hidden_ckeditor_img" type="hidden" onchange="insert_pizza_image()">';
    html += '<a href="' + url + '" id="lookup_hidden_ckeditor_img" onclick="return showRelatedObjectLookupPopup(this);"></a>';
    html += '</div>';
    
    django.jQuery('body').append(html);
    
    editor.addCommand('insertPizzaImage', {
      exec : function( editor ) {
        django.jQuery('#lookup_hidden_ckeditor_img').click();
        img_picker_editor = editor;
      }
		});
		
		editor.ui.addButton('PizzaImage', {
      label: 'Insert Pizza Image',
      command: 'insertPizzaImage',
      icon: this.path + 'images/picture.png'
    });
	}
});

function insert_pizza_image () {
  var iid = django.jQuery("#hidden_ckeditor_img").val();
  django.jQuery.ajax({
    url: IMAGE_URL + iid + '/get_url/',
    success: function (data) {
      img_picker_editor.insertHtml('<img src="' + data.url + '" alt="">');
    },
  });
}

function dismissRelatedLookupPopup(win, chosenId) {
  var name = windowname_to_id(win.name);
  var elem = document.getElementById(name);
  if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
      elem.value += ',' + chosenId;
  } else {
      document.getElementById(name).value = chosenId;
  }
  // GRAPPELLI CUSTOM: element focus
  elem.focus();
  win.close();
  django.jQuery(elem).trigger('change');
}
