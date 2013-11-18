$(document).ready(function () {
  var patt = /_popup=1/;
  
  if (patt.test(document.location.search)) {}
  
  else {
    patt = /^(Add|Change)/;
    var title = $('title').html();
    if (!patt.test(title)) {
      $('ul.object-tools').append('<li><a href="./multi/">Multi Image Upload</a></li>');
      $('ul.grp-object-tools').append('<li><a class="grp-state-focus" href="./multi/">Multi Image Upload</a></li>');
    }
  }
});
