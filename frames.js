'use strict';

function getFrameState(frame) {
	const code = frame.querySelector('code')
	return code.style.display === 'block' ? 'expand' : 'collapse';
}

// `state` is 'collapse' or 'expand'
function setFrameState(frame, state) {
	const display = state === 'expand' ? 'block' : 'none';
	const code = frame.querySelector('code');
	const table = frame.querySelector('table');
	code.style.display = display;
	table.style.display = display;
}

function setAllFrameStates(state) {
	const frames = document.getElementsByClassName('frame');
	for (let frame of frames) {
		setFrameState(frame, state);
	}
}

function parseDepth(frame) {
	return parseInt(frame.dataset.depth);
}

// Returns next frame element or null
function getNextFrame(frame) {
	frame = frame.nextSibling;
	while (frame && frame.className !== 'frame') {
		frame = frame.nextSibling;
	}
	return frame;
}

function getAllChildFrames(frame) {
	const rootDepth = parseDepth(frame);
	const childFrames = [];
	frame = getNextFrame(frame);
	while (frame && parseDepth(frame) > rootDepth) {
		childFrames.push(frame);
		frame = getNextFrame(frame);
	}
	return childFrames;
}

// Toggles a frame and applies same action to all its child frames
// `this` refers to frame DOM element
function toggleFrame(event) {
	const state = getFrameState(this) === 'collapse' ? 'expand' : 'collapse';
	const framesToSet = [this].concat(getAllChildFrames(this))
	for (const frame of framesToSet) {
		setFrameState(frame, state);
	}
}

function initEventListeners() {
	// Frame toggles
	const frames = document.getElementsByClassName('frame');
	for (const frame of frames) {
		frame.addEventListener('click', toggleFrame);
	}

	// expand-all/collapse-all buttons
	const expandAllButton = document.getElementById('expand-all');
	const collapseAllButton = document.getElementById('collapse-all');
	expandAllButton.addEventListener('click', function(event) {
		setAllFrameStates('expand');
	});
	collapseAllButton.addEventListener('click', function(event) {
		setAllFrameStates('collapse');
	});
}

window.onload = function() {
	initEventListeners();
}

