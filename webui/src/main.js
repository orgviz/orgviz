function sendOrgContentRequest() {
	console.log("Sending orgContent")

	setUpdateButtonEnabled(false)

	orgvizInput = document.querySelector("textarea").value

	fetch(window.serverUrl + "createImageFromOrgViz", {
		method: "POST",
		mode: "cors",
		body: orgvizInput
	}).then(res => {
		return res.json();
	}).then(json => {
		recvOrgContentResult(json) 
	}).catch(e => {
		console.log("Fetch error", e)
		setResultError("ERROR: " + e)
	});
}

function sendWebservice() {
	console.log("Sending webservice")

	var btn = document.querySelector('button#sendWebservice')
	var wait = document.querySelector('#waitMessage')
	setResult("Please wait...")

	btn.disabled = true;
	wait.hidden = false;

	fetch(window.serverUrl + "createImageFromWebservice", {
		method: "POST",
		mode: "cors", 
		cache: "no-cache",
		body: document.querySelector('#webserviceKey').value,
	}).then(res => {
		btn.disabled = false;
		wait.hidden = true;

		return res.json()
	}).then(json => {
		recvOrgContentResult(json)
	}).catch(e => {
		console.log("Fetch error", e)
		setResultError("ERROR: " + e)
	});
}

function recvOrgContentResult(json) {
	if (json.errors.length == 0) {
		showRenderedFilename(json.filename);
	} else {
		showServerErrors(json.errors);
	}
}

function showRenderedFilename(filename) {
	var img = document.createElement("img")
	img.setAttribute("src", filename + "?date=" + (new Date().getTime())); // Append the date here, to cache-bust

	setResult(img)
}

function showServerErrors(errors) {
	setResultError(errors);
}

function setUpdateButtonEnabled(enabled) {
	document.querySelector('button#sendFile').disabled = !enabled
}


function codeEditKeyDown(e) {
	const KEY_TAB = 9;

	setUpdateButtonEnabled(true)

	if (e.keyCode == KEY_TAB) {
		this.value += "\t"

		if (e.preventDefault) {
			e.preventDefault()
		}

		return false
	}
}

function setResultError(message) {
	setResult(message, "error")
}

function setResult(message, style) {
	const resultContents = document.querySelector('#resultContents');
	resultContents.classList.remove('error')
	resultContents.classList.add(style)

	if(typeof(message) == "string") {
		resultContents.innerHTML = message;
	} else {
		resultContents.innerHTML = ""; // FIXME iterate over children and remove

		document.querySelector('#resultContents').append(message);
	}
}

function changeView(config) {
	console.log("Changing view", config)

	switch (config.serverMode) {
		case 'webservice':
			document.querySelector("div#inputView").remove()

			document.querySelector("#webserviceTitle").innerHTML = config.webserviceName
			document.querySelector("#webserviceKeyName").innerHTML = config.webserviceKeyName + ': '

			document.querySelector("main").style.flexDirection = "column"
			document.querySelector("#webserviceView").style.flexGrow = 0
			document.querySelector("#imageView").style.flexGrow = 1
			break;
		default:
			document.querySelector('div#webserviceView').remove()
			break;
	}
}

function recvServerConfig(config) {
	console.log("server config: ", config) 

	changeView(config)
}

function getServerConfig() {
	fetch(window.serverUrl + "clientConfig", {
		method: "POST",
		mode: "cors",
	}).then(res => {
		return res.json();
	}).then(json => {
		recvServerConfig(json) 
	}).catch(e => {
		console.log("Fetch error", e)
		setResult("ERROR: " + e)
	});
}

window.initOrgviz = function() {
	document.querySelector('button#sendFile').onclick = sendOrgContentRequest
	document.querySelector('textarea').onkeydown = codeEditKeyDown

	document.querySelector('button#sendWebservice').onclick = sendWebservice

	window.serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/" 

	getServerConfig();

	setResult('Nothing to see here yet!');
}
