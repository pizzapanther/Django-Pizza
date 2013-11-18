CKEDITOR.editorConfig = function( config ) {
  config.toolbar = 'Full';
  config.scayt_autoStartup = true;
  config.allowedContent = true;
  
  config.extraPlugins = 'pizzaimage,pizzafile',
  config.toolbar_Full =
  [
    { name: 'document', items : [ 'Source' ] },
    { name: 'clipboard', items : [ 'Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
  	{ name: 'editing', items : [ 'Find','Replace','-','SelectAll','-', 'Scayt' ] },
  	//'/',
  	{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
  	{ name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','CreateDiv',
  	'-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock','-','BidiLtr','BidiRtl' ] },
  	{ name: 'links', items : [ 'Link','Unlink','Anchor' ] },
  	{ name: 'insert', items : [ 'Image','Flash','Table','HorizontalRule','SpecialChar','Iframe' ] },
  	{ name: 'pizza', items : [ 'PizzaImage', 'PizzaFile' ] },
  	'/',
  	{ name: 'styles', items : [ 'Styles','Format', 'Font', 'FontSize' ] },
  	{ name: 'colors', items : [ 'TextColor','BGColor' ] },
  	{ name: 'tools', items : [ 'Maximize', 'ShowBlocks','-','About' ] }
  ];
}
