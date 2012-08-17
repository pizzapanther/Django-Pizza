$(document).ready(function () {
  var url = '?__clearqs=1';
  var patt = /pop=1/;
  
  if (patt.test(document.location.search)) {
    $.each(document.location.search.substr(1).split('&'), function (c, q) {
      var i = q.split('=');
      if (i[0] != 'q') {
        url = url + '&' + q;
      }
    });
  }
  
  if ($('ul.object-tools .addlink').length > 0) {
    $('ul.object-tools').append('<li><a href="' + url + '">Reset Search &amp; Filters</a></li>');
  }
  
  if ($('ul.grp-object-tools .grp-add-link').length > 0) {
    $('ul.grp-object-tools').append('<li><a class="grp-state-focus" href="' + url + '">Reset Search &amp; Filters</a></li>');
  }
});
