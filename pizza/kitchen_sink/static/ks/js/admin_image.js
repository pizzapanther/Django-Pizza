$(document).ready(function () {
  var patt = /_popup=1/;
  
  if (patt.test(document.location.search)) {}
  
  else {
    if ($('ul.object-tools').length > 0) {
      $('ul.object-tools').append('<li><a href="./multi/">Multi Image Upload</a></li>');
    }
    
    if ($('ul.grp-object-tools').length > 0) {
      $('ul.grp-object-tools').append('<li><a class="grp-state-focus" href="./multi/">Multi Image Upload</a></li>');
    }
  }
});
