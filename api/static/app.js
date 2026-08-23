// Conductor Voice Agent - hands-free mobile web app
let mediaRecorder;
let microphoneStream;
let audioContext;
let analyser;
let monitoringFrame;
let audioChunks = [];
let currentAudio = null;
let isRecording = false;
let isProcessing = false;
let sessionActive = false;
let shouldSubmitRecording = true;
let heardSpeech = false;
let recordingStartedAt = 0;
let lastSoundAt = 0;

const micButton = document.getElementById('micButton');
const sessionLabel = document.getElementById('sessionLabel');
const status = document.getElementById('status');
const messages = document.getElementById('messages');
const recordingIndicator = document.getElementById('recordingIndicator');
const voiceSelect = document.getElementById('voiceSelect');
const conversationMode = document.getElementById('conversationMode');

document.addEventListener('DOMContentLoaded', () => {
	setupTextChat();
	loadSettings();
	micButton.addEventListener('click', toggleConversation);
	showStatus('Ready. Tap the microphone once to begin.');
});

function setupTextChat() {
	const textInput = document.getElementById('textInput');
	const sendButton = document.getElementById('sendButton');

	sendButton.addEventListener('click', () => {
		const text = textInput.value.trim();
		if (text) {
			sendTextMessage(text);
			textInput.value = '';
		}
	});

	textInput.addEventListener('keydown', (event) => {
		if (event.key === 'Enter') {
			sendButton.click();
		}
	});
}

async function sendTextMessage(text) {
	try {
		addMessage('user', text);
		showStatus('Thinking...');

		const response = await fetch('/api/chat', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ query: text })
		});

		if (!response.ok) throw new Error('API request failed');

		const data = await response.json();
		addMessage('assistant', data.response);
		addSources(data.sources);
		showStatus('Ready');
	} catch (error) {
		showStatus(`Error: ${error.message}`);
		console.error('Chat error:', error);
	}
}

async function ensureMicrophone() {
	if (mediaRecorder) return;

	microphoneStream = await navigator.mediaDevices.getUserMedia({
		audio: {
			echoCancellation: true,
			noiseSuppression: true,
			autoGainControl: true
		}
	});

	const preferredType = 'audio/webm';
	const recorderOptions = MediaRecorder.isTypeSupported(preferredType)
		? { mimeType: preferredType }
		: undefined;
	mediaRecorder = new MediaRecorder(microphoneStream, recorderOptions);

	mediaRecorder.ondataavailable = (event) => {
		if (event.data.size > 0) audioChunks.push(event.data);
	};

	mediaRecorder.onstop = async () => {
		cancelAnimationFrame(monitoringFrame);
		const mimeType = mediaRecorder.mimeType || preferredType;
		const audioBlob = new Blob(audioChunks, { type: mimeType });
		audioChunks = [];

		if (shouldSubmitRecording && audioBlob.size > 0) {
			await sendVoiceMessage(audioBlob);
		} else {
			scheduleNextListen();
		}
	};

	audioContext = new AudioContext();
	const source = audioContext.createMediaStreamSource(microphoneStream);
	analyser = audioContext.createAnalyser();
	analyser.fftSize = 2048;
	source.connect(analyser);
}

async function toggleConversation() {
	if (sessionActive) {
		stopConversation();
		return;
	}

	sessionActive = true;
	updateSessionControl();
	try {
		await ensureMicrophone();
		if (audioContext.state === 'suspended') await audioContext.resume();
		await startRecording();
	} catch (error) {
		sessionActive = false;
		updateSessionControl();
		showStatus('Microphone access is required. Allow it once, then tap again.');
		console.error('Microphone error:', error);
	}
}

function stopConversation() {
	sessionActive = false;
	if (currentAudio) {
		currentAudio.pause();
		currentAudio = null;
	}
	if (isRecording) stopRecording(false);
	updateSessionControl();
	showStatus('Conversation paused. Tap once to resume.');
}

async function startRecording() {
	if (!sessionActive || isProcessing || isRecording) return;
	await ensureMicrophone();
	if (mediaRecorder.state !== 'inactive') return;

	isRecording = true;
	shouldSubmitRecording = true;
	heardSpeech = false;
	recordingStartedAt = Date.now();
	lastSoundAt = recordingStartedAt;
	audioChunks = [];

	micButton.classList.add('recording');
	recordingIndicator.classList.remove('hidden');
	showStatus('Listening...');
	mediaRecorder.start();
	monitorSilence();
}

function stopRecording(submit) {
	if (!isRecording || mediaRecorder.state === 'inactive') return;
	isRecording = false;
	shouldSubmitRecording = submit;
	micButton.classList.remove('recording');
	recordingIndicator.classList.add('hidden');
	showStatus(submit ? 'Thinking...' : 'Listening...');
	mediaRecorder.stop();
}

function monitorSilence() {
	if (!isRecording || !analyser) return;

	const samples = new Uint8Array(analyser.fftSize);
	analyser.getByteTimeDomainData(samples);
	let sumSquares = 0;
	for (const sample of samples) {
		const centered = (sample - 128) / 128;
		sumSquares += centered * centered;
	}
	const volume = Math.sqrt(sumSquares / samples.length);
	const now = Date.now();

	if (volume > 0.025) {
		heardSpeech = true;
		lastSoundAt = now;
	}

	if (heardSpeech && now - lastSoundAt > 1200) {
		stopRecording(true);
		return;
	}

	if (!heardSpeech && now - recordingStartedAt > 20000) {
		stopRecording(false);
		return;
	}

	if (now - recordingStartedAt > 90000) {
		stopRecording(heardSpeech);
		return;
	}

	monitoringFrame = requestAnimationFrame(monitorSilence);
}

async function sendVoiceMessage(audioBlob) {
	isProcessing = true;
	try {
		addMessage('user', 'Voice message...', true);
		const formData = new FormData();
		formData.append('audio', audioBlob, 'recording.webm');

		const response = await fetch('/api/voice-chat', {
			method: 'POST',
			body: formData
		});
		if (!response.ok) throw new Error('Voice API request failed');

		const data = await response.json();
		updateLastMessage(data.transcription);
		addMessage('assistant', data.response);
		addSources(data.sources);

		if (data.audio_url) await playAudio(data.audio_url);
	} catch (error) {
		sessionActive = false;
		updateSessionControl();
		showStatus(`Voice error: ${error.message}. Tap once to retry.`);
		console.error('Voice chat error:', error);
	} finally {
		isProcessing = false;
	}

	scheduleNextListen();
}

function scheduleNextListen() {
	if (sessionActive && conversationMode.checked) {
		showStatus('Listening again...');
		setTimeout(startRecording, 350);
		return;
	}

	if (!conversationMode.checked) sessionActive = false;
	updateSessionControl();
	showStatus(sessionActive ? 'Ready for the next turn' : 'Ready');
}

function addSources(sources) {
	if (!sources || sources.length === 0) return;
	const sourceText = sources.slice(0, 2).map((source) =>
		`${source.platform.toUpperCase()}: ${source.title}`
	).join('\n');
	addMessage('system', sourceText, true);
}

function addMessage(role, text, small = false) {
	const messageDiv = document.createElement('div');
	messageDiv.className = `message p-4 rounded-2xl ${
		role === 'user'
			? 'bg-white/20 ml-8'
			: role === 'assistant'
				? 'bg-blue-500/30 mr-8'
				: 'bg-white/10 text-center'
	} ${small ? 'text-xs' : 'text-sm'} text-white`;
	messageDiv.textContent = text;
	messages.appendChild(messageDiv);
	messages.parentElement.scrollTop = messages.parentElement.scrollHeight;
	return messageDiv;
}

function updateLastMessage(text) {
	const lastMessage = messages.lastElementChild;
	if (lastMessage) lastMessage.textContent = text;
}

async function playAudio(audioUrl) {
	return new Promise((resolve, reject) => {
		if (currentAudio) currentAudio.pause();
		currentAudio = new Audio(audioUrl);
		currentAudio.onended = () => {
			currentAudio = null;
			resolve();
		};
		currentAudio.onerror = reject;
		showStatus('Speaking...');
		currentAudio.play().catch(reject);
	});
}

function showStatus(text) {
	status.replaceChildren();
	const line = document.createElement('p');
	line.className = 'text-sm opacity-75';
	line.textContent = text;
	status.appendChild(line);
}

function updateSessionControl() {
	micButton.setAttribute(
		'aria-label',
		sessionActive ? 'Stop hands-free conversation' : 'Start hands-free conversation'
	);
	sessionLabel.textContent = sessionActive
		? 'Conversation active — tap only to stop'
		: 'Tap once to start hands-free conversation';
}

function loadSettings() {
	const savedVoice = localStorage.getItem('voice');
	if (savedVoice) voiceSelect.value = savedVoice;
	const savedConversationMode = localStorage.getItem('conversationMode');
	conversationMode.checked = savedConversationMode !== 'false';

	voiceSelect.addEventListener('change', () => {
		localStorage.setItem('voice', voiceSelect.value);
		saveVoiceSettings();
	});

	conversationMode.addEventListener('change', () => {
		localStorage.setItem('conversationMode', String(conversationMode.checked));
	});
}

async function saveVoiceSettings() {
	try {
		await fetch('/api/settings/voice', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ voice: voiceSelect.value })
		});
	} catch (error) {
		console.error('Error saving voice settings:', error);
	}
}

let deferredPrompt;
window.addEventListener('beforeinstallprompt', (event) => {
	event.preventDefault();
	deferredPrompt = event;
	const installButton = document.createElement('button');
	installButton.textContent = 'Install voice app';
	installButton.className = 'glass text-white px-4 py-2 rounded-lg text-sm fixed bottom-4 right-4';
	installButton.addEventListener('click', async () => {
		deferredPrompt.prompt();
		await deferredPrompt.userChoice;
		deferredPrompt = null;
		installButton.remove();
	});
	document.body.appendChild(installButton);
});

if ('serviceWorker' in navigator) {
	navigator.serviceWorker.register('/static/sw.js').catch(() => {
		// The service worker is optional; voice remains available online.
	});
}
