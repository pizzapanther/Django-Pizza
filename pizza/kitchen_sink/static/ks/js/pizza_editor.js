function pizza_load_editors () {
  var patt = /__prefix__/;
  
  django.jQuery(".pizza_editor").each(function (i, element) {
    if (!django.jQuery(element).hasClass("pizza_editor_loaded")) {
      if (!patt.test(element.id)) {
        CKEDITOR.replace(element.id, {customConfig : CKEDITOR.basePath + '../js/ckconfig.js'});
        django.jQuery(element).addClass("pizza_editor_loaded");
      }
    }
  });
}

django.jQuery(document).ready(function () {
  pizza_load_editors();
  
  var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
  var observer = new MutationObserver(function(mutations, observer) {
    pizza_load_editors();
  });
  
  observer.observe(document, {subtree: true, childList: true});
});
