'use strict';

function parseDepth(frame) {
	return parseInt(frame.dataset.depth);
}

// Returns next frame element or null
function getNextFrame(frame) {
	frame = frame.nextElementSibling;
	while (frame && !frame.classList.contains('frame')) {
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
	const expanded = this.classList.contains('expanded');
	const framesToSet = [this].concat(getAllChildFrames(this));
	for (const frame of framesToSet) {
		if (expanded)
			frame.classList.remove('expanded');
		else
			frame.classList.add('expanded');
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
	expandAllButton.addEventListener('click', function expandAll(event) {
		for (const frame of frames)
			frame.classList.add('expanded');
	});
	collapseAllButton.addEventListener('click', function collapseAll(event) {
		for (const frame of frames)
			frame.classList.remove('expanded');
	});
}

window.onload = initEventListeners;
