$(document).ready(function () {
  var url = '?__clearqs=1';
  var patt = /_popup=1/;
  
  if (patt.test(document.location.search)) {
    $.each(document.location.search.substr(1).split('&'), function (c, q) {
      var i = q.split('=');
      if (i[0] != 'q') {
        url = url + '&' + q;
      }
    });
  }
  
  patt = /^(Add|Change)/;
  var title = $('title').html();
  if (!patt.test(title)) {
    $('ul.object-tools').append('<li><a href="' + url + '">Reset Search &amp; Filters</a></li>');
    $('ul.grp-object-tools').append('<li><a class="grp-state-focus" href="' + url + '">Reset Search &amp; Filters</a></li>');
  }
});
