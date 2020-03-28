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
		setResult("ERROR: " + e)
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
	setResult(errors);
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

function setResult(message) {
	const resultContents = document.querySelector('#resultContents');

	if(typeof(message) == "string") {
		resultContents.innerHTML = message;
	} else {
		resultContents.innerHTML = ""; // FIXME iterate over children and remove

		document.querySelector('#resultContents').append(message);
	}
}

window.initOrgviz = function() {
	document.querySelector('button#sendFile').onclick = sendOrgContentRequest
	document.querySelector('textarea').onkeydown = codeEditKeyDown

	window.serverUrl = "http://localhost:8081/"

	setResult('Nothing to see here yet!');
}
