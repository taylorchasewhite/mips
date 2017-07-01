function loadTabStyleSheets() {
	jQuery('head').append('<link rel="stylesheet" href="/css/buttons.css" type="text/css" />');
	jQuery('head').append('<link rel="stylesheet" href="/css/tabs.css" type="text/css" />');
	jQuery('head').append('<link rel="stylesheet" href="/css/normalize.css" type="text/css" />');
	jQuery('head').append('<link rel="stylesheet" href="/css/tabs2.css" type="text/css" />');
	jQuery('head').append('<link rel="stylesheet" href="/css/tabstyles.css" type="text/css" />');
    (function() {
     [].slice.call( document.querySelectorAll( '.tabs' ) ).forEach( function( el ) {
  	new CBPFWTabs( el );
     });
    })();
}

function initializeCompiler() {
    ace.config.set('basePath', '/scripts/ace/src-min-noconflict');	     
    var editor1 = ace.edit("editor1");
    editor1.setTheme("ace/theme/textmate");
    editor1.getSession().setMode("ace/mode/mips_assembler");
    editor1.getSession().setUseWrapMode(false);
	editor1.$blockScrolling=Infinity;
	var editor = ace.edit("editor0");
	editor.setTheme("ace/theme/textmate");
	editor.getSession().setMode("ace/mode/javascript");
	editor.getSession().setUseWrapMode(true);
	editor.$blockScrolling=Infinity;
	jQuery('#btnCompile').click(function(){
		jQuery.ajax({
			type:'post',
			url:"/compiler/part6/compile.php",
			//cache:false,
			data:{ 'data': editor.getSession().getValue() },
			//async:asynchronous,
			//dataType:json, //if you want json
			success: function(data, textStatus, jqXHR) {
				//alert(data);
				if (data.indexOf("Parse error")+data.indexOf("Lexical error") + data.indexOf("Error")===-3) {
					editor1.getSession().setValue(data);
					jQuery("#parseErrorDiv").text("Good job!");
					jQuery("#parseErrorDiv").addClass("parseSuccess").removeClass("hidden parseError");
				}
				else {
					jQuery("#parseErrorDiv").text(data);
					jQuery("#parseErrorDiv").removeClass("hidden parseSuccess").addClass("parseError");
				}
			},
			error: function(data,textStatus,errorThrown) {
				alert(textStatus + ": " + errorThrown);
			}
		});
	});	
}
