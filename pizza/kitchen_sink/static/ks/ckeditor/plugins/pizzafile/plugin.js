var file_picker_editor = null;
var FILE_URL = location.href + '../../../kitchen_sink/file/';

CKEDITOR.plugins.add('pizzafile', {
  init: function( editor ) {
    var url = FILE_URL + '?t=id';
    var html = '<div style="display: none;">'
    html += '<input id="hidden_ckeditor_file" type="hidden" onchange="insert_pizza_file()">';
    html += '<a href="' + url + '" id="lookup_hidden_ckeditor_file" onclick="return showRelatedObjectLookupPopup(this);"></a>';
    html += '</div>';
    
    django.jQuery('body').append(html);
    
    editor.addCommand('insertPizzaFile', {
      exec : function( editor ) {
        django.jQuery('#lookup_hidden_ckeditor_file').click();
        file_picker_editor = editor;
      }
		});
		
		editor.ui.addButton('PizzaFile', {
      label: 'Insert Pizza File',
      command: 'insertPizzaFile',
      icon: this.path + 'images/file.png'
    });
	}
});

function insert_pizza_file () {
  var iid = django.jQuery("#hidden_ckeditor_file").val();
  django.jQuery.ajax({
    url: FILE_URL + iid + '/get_url/',
    success: function (data) {
      file_picker_editor.insertHtml('<a href="' + data.url + '">' + data.title +'</a>');
    },
  });
}
