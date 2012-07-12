// ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
// (C) 2010 SciOS Scientific Operating Systems GmbH
// editor.js
// Editor/Ajax functions
// Credits: CodeMirror, jQuery
// Author: kp/10052010
// ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

var i = 0;
var activeEditor;
var mainLayout;


// Cell structure:
//
// <div id="id.cell:N" class="cls.cell">
//   <div id="id.cell.input:N" class="cls.cell.input"> ... </div>
//   <div id="id.cell.output:N" class="cls.cell.output"> ...<...>... </div>
// </div>
//

function createInputCell(n) {
  var div = document.createElement("div");
  var textarea = document.createElement("textarea");
  div.setAttribute("id", "id.cell.input:" + n);
  div.setAttribute("class", "cls.cell.input");
  div.setAttribute("style", "display:block");
  textarea.setAttribute("id", n);
  div.appendChild(textarea);
  return div;
}

function createOutputCell(n) {
  var div = document.createElement("div");
  var code = document.createElement("pre"); // code,pre or p if MJax
  div.setAttribute("id", "id.cell.output:" + n);
  div.setAttribute("class", "cls.cell.output");
  div.setAttribute("style", "display:block");
  code.setAttribute("id", "id.code:" + n);
  code.setAttribute("class", "cls.code" );
  code.setAttribute("style", "display:block");
  div.appendChild(code);
  return div;
}

function createCell(n) {
  var div = document.createElement("div");
  div.setAttribute("id", "id.cell:" + n);
  div.setAttribute("class", "cls.cell");
  div.setAttribute("style", "display:block");
  div.appendChild(createInputCell(n));
  div.appendChild(createOutputCell(n));
  return div;
}


// extract code data
function getCodeData(data) {
  return data.split("</code>")[0].split("<code>")[1];
}

// extract image data
function getImageData(data) {
  return data.split("</img>")[0].split("<img>")[1];
}



// Add an editor
function addEditor(n) {

  // add a cell to the body or other element with id = n
  ///document.body.appendChild(createCell(n));
  document.getElementById("main").appendChild(createCell(n));

  // replace textarea in input cell by editor
  var ed = CodeMirror.fromTextArea(document.getElementById(n), {
              lineNumbers: true,
              matchBrackets: false,
              autofocus: true,
              extraKeys: {"Ctrl-Space": "autocomplete",
                          "Ctrl-Enter": "dispatch"} });
  return ed;
}


// autocomplete command
CodeMirror.commands.autocomplete = function(cm) {
  CodeMirror.simpleHint(cm, CodeMirror.javascriptHint);
}



// dispatch command
CodeMirror.commands.dispatch = function(cm) {

  var textarea = cm.getTextArea(); // get the underlying text area
  var id = textarea.getAttribute("id"); // get the id of the editor/area
  var value = cm.getValue(); // get editor contents

  jQuery.ajax({
    type: "POST",
    data: value,
    dataType: "text",
    success: function(data) {
      var outcode = document.getElementById("id.code:"+id)
      var txt = document.createTextNode(getCodeData(data))

      if (outcode.hasChildNodes() == false )
        {outcode.appendChild(txt)}
      else
        {outcode.replaceChild(txt, outcode.firstChild)}; //img node?
        MathJax.Hub.Queue(["Typeset",MathJax.Hub,outcode]);
     },
  });



  //cm.setValue(id);

  // if we are in the last editor then create a new one.
  if (id == i) {
    i++;
    activeEditor = addEditor(i);
    activeEditor.focus();
    }

  //cm.save();
  //cm.toTextArea();
}



// Main
jQuery(document).ready(function () {
  mainLayout = jQuery('body').layout({applyDefaultStyles: true});
  mainLayout.toggle("east");
  activeEditor = addEditor(0);
  activeEditor.focus();
});

