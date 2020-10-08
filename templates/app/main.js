$("#messageSend").click(function(e){
    e.preventDefault();
    var msg = new SpeechSynthesisUtterance('Testing one more option');
    window.speechSynthesis.speak(msg);
});