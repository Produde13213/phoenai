# PhoenAI — Office Demo Checklist

## Before the demonstration

1. Use an office-approved laptop/network. This is a browser prototype, not a live telephone service.
2. Pull the latest `main` branch.
3. Confirm Python 3.11+ is installed.
4. Double-click `start_demo.bat`. Keep the black terminal window open.
5. Open `http://127.0.0.1:8000` if the browser does not open automatically.
6. Check the header and audio-readiness message.
7. Play the welcome recording once and set a comfortable speaker volume.
8. Test menu options 1, 2, 3, and 4; test sub-options; press 0 to return to the main menu.
9. Press 9 to demonstrate invalid input.
10. Click Simulate idle timeout once to play the first reminder. Click it a second time to play goodbye and return to the main menu.
11. Test AI chat only if the NVIDIA API key is already configured on the demo computer.

## What works without a phone number

- Browser-based IVR menu simulation with a numeric keypad.
- Complaint, school-information, scholarship, and representative menu flows.
- Prerecorded WAV playback for the uploaded recordings.
- Main-menu return, invalid-input, idle, and goodbye audio previews.
- Audio-file readiness check.
- NVIDIA-powered text chat, if configured.
- Editable AI instructions in `sysprompt.txt`.

## Known limitations to explain honestly

- No incoming or outgoing calls.
- No BSNL, SIP, PBX, or EPABX connection.
- Option 4 does not transfer to a human representative.
- Option 1 has no dedicated voice recording yet.
- No complaint is filed or tracked.
- No school or scholarship database/portal is connected.
- AI responses are a prototype and must not be treated as official government advice.
- Do not enter Aadhaar numbers, OTPs, passwords, bank details, or sensitive personal information.

## If something goes wrong

- If the page does not load, confirm the terminal says the server is running and visit `http://127.0.0.1:8000`.
- If audio does not start automatically, press Play in the audio player; browser audio policies can block automatic playback.
- If the AI key is missing, the menu and prerecorded audio should still work. AI chat will show an unavailable message.
- To stop the server, return to the terminal and press Ctrl+C.

## Suggested presentation order

1. Welcome recording.
2. Press 1 and show complaint guidance.
3. Press Main menu, then 2 and demonstrate school sub-options.
4. Return and demonstrate scholarship options under 3.
5. Demonstrate 4 and explain that live transfer is future telephony work.
6. Press 0 to return to the main menu.
7. Press 9 to show invalid-input handling.
8. Ask a simple, non-sensitive question in AI chat if the NVIDIA key is configured.
