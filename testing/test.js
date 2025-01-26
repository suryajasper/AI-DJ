// Function to speak the text
function speakText() {
  const textInput = document.getElementById('textInput').value;
  if (!textInput) {
    alert('Please enter some text!');
    return;
  }

  // Create a SpeechSynthesisUtterance instance
  const msg = new SpeechSynthesisUtterance();
  msg.text = textInput;

  // Adjust optional settings
  msg.rate = 1; // Speed (0.1 to 2)
  msg.pitch = 1; // Pitch (0 to 2)
  msg.volume = 1; // Volume (0 to 1)

  // Speak the text
  window.speechSynthesis.speak(msg);
}

// Function to stop speaking
function stopSpeaking() {
  window.speechSynthesis.cancel();
}

// Attach event listeners to buttons
document.getElementById('speakButton').addEventListener('click', speakText);
document.getElementById('stopButton').addEventListener('click', stopSpeaking);
