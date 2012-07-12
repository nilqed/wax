// ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
// (C) 1998-2012, SciOS Scientific Operating Systems GmbH
// editor.js
// Editor/Ajax functions
// Credits: CodeMirror, jQuery
// Author: kp/19052012
// Notes:
// jquery.ui.core.css -> .ui-helper-reset -> font-size set to 60%
// see also: static.scios.themes.base jquery.ui.theme.css
// ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


// accordion west (fully collapsible)
jQuery(function() {
  jQuery( "#accordion-west" ).accordion({
    collapsible: true
  });
});


function toggle(showHideDiv, switchTextDiv) {
	var element = document.getElementById(showHideDiv);
	var text = document.getElementById(switchTextDiv);
	if(element.style.display == "block") {
    		element.style.display = "none";
		text.innerHTML = "restore";
  	}
	else {
		element.style.display = "block";
		text.innerHTML = "collapse";
	}
}


