# Voice-to-Code

Control AI Agent CLI with your voice using speech recognition.

## Overview

Speak commands naturally and watch them appear in AI Agent CLI in real-time. The tool uses whisper-mic for local, free speech-to-text transcription with support for accented English.

**Features:**
- ✅ Free, unlimited usage (runs locally)
- ✅ Auto-pause detection (2s silence triggers transcription)
- ✅ Context maintained across commands (persistent AI Agent session)
- ✅ Visual feedback (watch text appear in tmux window)
- ✅ Notifications and TTS announcements (mac: OS notification and `say` / linux: `notify-send` and `espeak-ng`)
- ✅ Live status bar (LISTENING/SENDING/READY)
- ✅ Detailed logging for debugging

## Prerequisites

- macOS and Homebrew, or Linux
- Python 3.x
- AI Agent with CLI installed and configured

The rest of this document assumes Debian for Linux instructions.

## Installation

### 1. Install system dependencies

```bash
brew install tmux portaudio ffmpeg
```

or

```bash
sudo apt-get install tmux libportaudio2 portaudio19-dev ffmpeg
```

### 2. Install Python dependencies

```bash
cd voice-to-code
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 3. Configure microphone gain

**System Settings → Sound → Input:**
- Select your microphone
- Adjust **Input volume** to 60-70%
- Test: speak normally, meter should reach 60-70%

Higher mic gain improves transcription accuracy and prevents cutoffs.

## Usage

### 1. Start AI Agent in tmux session

Open terminal window and create a tmux session:

```bash
tmux new-session -s ai-voice-input "amp"
```

**To resume existing Amp thread:**
```bash
tmux new-session -s ai-voice-input "amp threads continue T-your-thread-id"
```

The default session name is `ai-voice-input`, but you can use any name and select it from the dropdown in the GUI.

### 2. Launch GUI

```bash
source venv/bin/activate
python main.py
```

If you see the following Tk error:

```
import _tkinter # If this fails your Python may not be configured for Tk
ModuleNotFoundError: No module named '_tkinter'
```

You will need to rebuild python with Tk configuration:

```bash
# mac
brew install python-tk
# linux
sudo apt-get install python3-tk
```

If using pyenv, you may need to reinstall Python:

```bash
pyenv install <your-python-version>
```

### 3. Use voice input

1. **Click Start** → Initializes transcriber (5-10s, GUI freezes during model load)
2. **Speak your command** → Auto-transcribes after 2s pause
3. **View in log window** → See transcribed text
4. **AI Agent responds** in tmux window
5. **Continue conversation** → Speak, pause, repeat
6. **Click Stop** → Stops listening (exits within 2s)

## Configuration

Edit via **Settings → Preferences** in GUI, or directly in `config.py`:

```python
CONFIG = {
    'transcriber_type': 'whisper_mic',  # Speech-to-text implementation
    'processor_type': 'tmux',           # Where to send transcribed text
    'model': 'large',                   # Whisper model (tiny/base/small/medium/large)
    'pause_threshold': 2.0,             # Seconds of silence before ending phrase
    'listen_timeout': 2.0,              # Max seconds to wait for speech to start
    'energy_threshold': 100,            # Minimum audio energy to detect speech
    'dynamic_energy': True,             # Auto-adjust for ambient noise
    'vocalize_response': False,         # Whether AI Agent should say a summary of the response out loud (macOS: say / Linux: espeak-ng)
    'log_handler_type': 'ui',           # Log output: 'ui' or 'file'
    'debug': False,                     # Verbose logging + capture WhisperMic logs
}
```

**Debug Mode:**
- `False` - Logs only: start/stop, transcribed text, errors
- `True` - Logs all operational details + WhisperMic internal logs

**Whisper models (trade-off speed vs accuracy):**
- `tiny` - Fastest, poor accuracy
- `base` - Fast, decent accuracy (~1-2s transcription)
- `small` - Better accuracy (~3-4s transcription)
- `medium` - High accuracy (~5-7s transcription)
- `large` - **Best for accented English** (~7-10s transcription) - **Recommended**

*Note: Transcription speed depends on your CPU. For Mac, Apple Silicon (M1/M2/M3) is much faster.*

## Troubleshooting

### Stop button doesn't respond immediately
- WhisperMic retries when detecting "too quiet" background noise
- **Quick fix:** Mute your microphone, then click Stop
- **Permanent fix:** Increase `energy_threshold` via Settings (200-400) to ignore background noise

### Voice cuts off mid-sentence
- Increase `pause_threshold` to 2.5 or 3.0 seconds via Settings

### Not detecting speech
- Lower `energy_threshold` (try 200 or 100) via Settings
- Enable `dynamic_energy` for automatic adjustment

### Poor transcription accuracy
- Change model to `large` via Settings
- Speak slower and more deliberately

### No audio captured
- **macOS:** Check mic permissions: **System Settings → Privacy & Security → Microphone → Python** (enable)
- **Linux:** Ensure microphone on ALSA/PulseAudio is configured properly
  - For PulseAudio, `pavucontrol` → Input Devices tab → Click checkmark ("set as fallback") to set a microphone as the default

### Session not found error
- Start tmux session first: `tmux new-session -s ai-voice-input "amp"`
- Select the correct session from the dropdown in the GUI
- Use the **+** button to add custom session names if needed
- Use the **-** button to remove a custom session name when done

### View logs

Logs and configuration stored in `~/.voice-to-code/`

```bash
tail -f ~/.voice-to-code/voice_input.log
```

### Enable debug logging
Edit `config.py`:
```python
'debug': True,
```
Logs will include detailed operation info

## How It Works

1. Click Start in GUI
2. Initializes WhisperMic model (5-10s, GUI freezes)
3. WhisperMic listens for speech with timeout-based polling
4. Detects pause (2s silence) → auto-transcribes
5. Text sent to tmux session via TmuxProcessor
6. Loop continues until Stop clicked
7. Threading.Event signals stop → exits within 2s

**Technical Details:**
- **GUI:** Tkinter with modular views/models architecture
- **Transcription:** Fully local via whisper-mic, zero cost
- **Threading:** Init on main thread, streaming in background
- **Factories:** Pluggable transcribers, processors, log handlers
- **Logging:** File or UI output with stdlib bridge in debug mode

## License

MIT License

https://opensource.org/licenses/MIT
