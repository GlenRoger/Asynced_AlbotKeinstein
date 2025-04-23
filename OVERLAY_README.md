# Twitch Bot Overlay System

This document explains how to use the overlay system for the Twitch bot.

## Overview

The overlay system consists of three main components:

1. **OverlayWindow (overlay.py)**: The PySide6 window that displays messages, GIFs, and plays sounds.
2. **OverlayBridge (overlay_bridge.py)**: A communication bridge that connects the bot to the overlay window.
3. **Integration in AlbotBrain.py**: Coordinates the overlay with the rest of the bot system.

## How It Works

The bot and the overlay communicate using Qt's signal/slot mechanism through the OverlayBridge class. The flow is:

1. Bot detects an event (e.g., streamer joins chat)
2. Bot calls a method on the overlay bridge (e.g., `show_streamer_greeting`)
3. Bridge emits a signal
4. Overlay window receives the signal and updates the display

## Available Commands in Chat

You can test the overlay with these commands in Twitch chat:

- `%overlay message Hello World!` - Shows a message on the overlay
- `%overlay greeting StreamerName` - Shows a greeting for a streamer
- `%overlay hide` - Hides the overlay

These commands are restricted to the streamer and moderators.

## Automatic Features

- **Streamer Greetings**: When a streamer from your auto-shoutout list joins chat, they'll automatically get a greeting on the overlay.

## For Developers

### How to Add a New Overlay Feature

1. **Add a signal in OverlayBridge**:
   ```python
   new_feature_signal = Signal(parameters_you_need)
   ```

2. **Add a method in OverlayBridge**:
   ```python
   def trigger_new_feature(self, parameters):
       self.new_feature_signal.emit(parameters)
   ```

3. **Add a slot in OverlayWindow**:
   ```python
   def handle_new_feature(self, parameters):
       # Implementation
   ```

4. **Connect them in OverlayWindow.connect_bridge**:
   ```python
   self.bridge.new_feature_signal.connect(self.handle_new_feature)
   ```

### Testing in OBS

1. Add a "Window Capture" source in OBS
2. Select the window titled "OverlayWindow" (or however it appears in your window list)
3. Configure transparency settings if necessary
4. Position and size as needed in your scene

## Future Enhancements

- GIF caching system
- Custom animations for different user roles
- Dynamic positioning based on stream layout
- Theme customization options

## Dependencies

- PySide6 must be installed: `pip install PySide6`