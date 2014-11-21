function activateMenu(str) {
	$("[id$=menu]").removeClass("active");
	$("[id="+str+"menu]").addClass("active");
}