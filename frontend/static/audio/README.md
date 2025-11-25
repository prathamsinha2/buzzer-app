# Ringtone Audio

This directory should contain the ringtone MP3 file used when the device rings.

## File Required:
- **ringtone.mp3** - The audio file that plays when the device is rung

## Audio Requirements:
- Format: MP3 (for maximum browser compatibility)
- Duration: 10-30 seconds recommended (will loop if needed)
- Sample Rate: 44.1kHz or 48kHz
- Bit Rate: 128kbps or higher

## Getting a Ringtone:
1. **Use a royalty-free ringtone**: Search for "royalty free ringtone mp3"
2. **Use system sounds**: Record your device's notification sound
3. **Create your own**: Use Audacity or similar tool
4. **Online tools**: Use https://www.zediva.com/ or similar to convert

## Testing on iOS:
- The audio MUST be triggered by user interaction (click/touch)
- The app must remain open for the audio to play on the lock screen
- Test on an actual iOS device (simulator may not play audio correctly)

## Important:
Make sure the ringtone.mp3 file is present before deploying to production.
