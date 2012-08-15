function get_versions (id) {
  $('#view_versions_' + id).load('./' + id + '/versions/');
}


function close_versions (id) {
  $('#view_versions_' + id).html('<a href="javascript: void(0);" onclick="get_versions(' + id + ')">View Versions</a>');
}
