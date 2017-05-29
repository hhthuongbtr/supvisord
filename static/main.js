//call
function check_unicode(str){
	for (var i = 0; i < str.length; i++) {
		if(str.charCodeAt(i) > 127) {
			return false;
		}
	}
	return true;
};

//call
function check_empty(str){
	if (str == "") {
		return false;
	}
	return true;
};

//call
function check_ip_fortmat(str){
	var matches = str.match(/\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):([0-9]{1,5})\b/);
	if (matches != null) {
		return false;
	}
	return true;
};

function check_name(){
	var name = document.getElementById( 'name' ).value.trim();
	return	{
		"result" : check_empty(name),
		"error" : "Tên không được trống!"
	};
}
function check_name_unicode(){
	var name = document.getElementById( 'name' ).value.trim();
	return	{
		"result" : check_unicode(name),
		"error" : "Tên không chứa kí tự đặc biệt, dấu tiếng Việt!"
	};
};

//supvisor/add/
function check_streamkey(){
	var streamkey = document.getElementById( 'streamkey' ).value.trim();
	return	{
		"result" : check_empty(streamkey),
		"error" : "Streamkey không được trống!"
	};
};

//supvisor/add/
function check_streamkey_unicode(){
	var streamkey = document.getElementById( 'streamkey' ).value.trim();
	return	{
		"result" : check_unicode(streamkey),
		"error" : "Streamkey không chứa kí tự đặc biệt, dấu tiếng Việt!"
	};
};

//supvisor/rtmp/add/
function check_encode(){
	var encode = document.getElementById( 'encode' ).value.trim();
	return	{
		"result" : check_empty(encode),
		"error" : "Encode không được trống!"
	};
}

//supvisor/rtmp/add/
function check_encode_unicode(){
	var encode = document.getElementById( 'encode' ).value.trim();
	return	{
		"result" : check_unicode(encode),
		"error" : "Encode không chứa kí tự đặc biệt, dấu tiếng Việt!"
	};
};

//supvisor/rtmp/add/
function check_domain(){
	var domain = document.getElementById( 'domain' ).value.trim();
	return	{
		"result" : check_empty(domain),
		"error" : "Domain không được trống!"
	};
}

//supvisor/rtmp/add/
function check_domain_unicode(){
	var domain = document.getElementById( 'domain' ).value.trim();
	return	{
		"result" : check_unicode(domain),
		"error" : "Domain không chứa kí tự đặc biệt, dấu tiếng Việt!"
	};
};		

function check_ip(){
	var ip = document.getElementById( 'ip' ).value.trim();
	return	{
		"result" : check_empty(ip),
		"error" : "IP không được trống!"
	};
};

//supvisor/rtmp/add/
function command(){
	var domain = document.form.domain.value.trim();
	var encode = document.form.encode.value.trim();
	var ip = document.form.ip.value.trim();
	document.getElementById("cmd").innerHTML = "Command: ffmpeg -re -i udp://" + ip + " " + encode + " rtmp://" + domain;
};

//supvisor/rtmp/add/
function name_change(){
	var name = document.getElementById( 'name' ).value.trim();
	document.getElementById("program").innerHTML = "Program: rtmp_" + name + ".ini";
};

//supvisor/add/
function event_onchange(){
	var event = document.getElementById( 'event' );
	if (event.options[event.selectedIndex].value == "RTMP"){
		window.location.href = "/supvisor/rtmp/add/";
	}
};

//supvisor/add/
function SubmitCheckTextField(){
	var arrs = [
		check_name,
		check_name_unicode,
		check_streamkey,
		check_streamkey_unicode,
		check_ip
	];

	var errors = "";

	arrs.forEach(function (fn) {
		var item = fn();
		if (item.result == false ) {
			errors += "\n" + item.error;
		}
	});

	if (errors.length > 1) {
		alert(errors);
		return false;
	}
	document.form.submit();
};

//supvisor/start/
function start_SubmitCheckTextField(){
	var arrs = [
		check_streamkey,
		check_streamkey_unicode,
		check_ip
	];

	var errors = "";

	arrs.forEach(function (fn) {
		var item = fn();
		if (item.result == false ) {
			errors += "\n" + item.error;
		}
	});

	if (errors.length > 1) {
		alert(errors);
		return false;
	}
	document.form.submit();
};

//supvisor/rtmp/add/		
function rtmp_SubmitCheckTextField(){
	var arrs = [
		check_name,
		check_name_unicode,
		check_encode,
		check_encode_unicode,
		check_domain,
		check_domain_unicode,
		check_ip
	];

	var errors = "";

	arrs.forEach(function (fn) {
		var item = fn();
		if (item.result == false ) {
			errors += "\n" + item.error;
		}
	});

	if (errors.length > 1) {
		alert(errors);
		return false;
	}
	document.form.submit();
};

//supvisor/rtmp/add/		
function rtmp_start_SubmitCheckTextField(){
	var arrs = [
		check_encode,
		check_encode_unicode,
		check_domain,
		check_domain_unicode,
		check_ip
	];

	var errors = "";

	arrs.forEach(function (fn) {
		var item = fn();
		if (item.result == false ) {
			errors += "\n" + item.error;
		}
	});

	if (errors.length > 1) {
		alert(errors);
		return false;
	}
	document.form.submit();
};