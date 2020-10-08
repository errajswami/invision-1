const microphone = $("#microphone");

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
  } else {
    alert("Speech recognition not supported")
  }