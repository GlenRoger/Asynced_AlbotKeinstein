from PySide6.QtCore import QObject, Signal
import config

class OverlayBridge(QObject):
    """
    Bridge class that facilitates communication between the bot and the overlay window
    using Qt's signal/slot mechanism.
    """
    # Define signals for different overlay actions
    show_message_signal = Signal(str)
    show_streamer_greeting_signal = Signal(str)
    play_sound_signal = Signal(str)
    show_gif_signal = Signal(str, int)  # URL, duration
    show_full_greeting_signal = Signal(str, object, object, object, int)
    hide_overlay_signal = Signal()
    animate_message_signal = Signal(str, object)  # animation_type, kwargs
    length_of_show_timer_signal = Signal(int)

    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.logger_prefix = "utils/OverlayBridge=>"
        self.logger.info(f"{self.logger_prefix}Initializing overlay bridge")

        self.overlay_ready_for_new_action = False

        
    def set_overlay_ready_flag(self, bool_value):
        self.overlay_ready_for_new_action = bool_value


    def overlay_ready_for_new_action(self):
        return self.overlay_ready_for_new_action
    
    def play_message(self, text_to_show = "", gif_to_show = "", sound_to_play = "", duration=5000):
        current_prefix = self.logger_prefix + "play_message"
        self.logger.info(f"{current_prefix}Going to play: text:{text_to_show}, gif:{gif_to_show}, sound:{sound_to_play}")

        self.length_of_show_timer_signal.emit(duration)

        if text_to_show != "":
            self.logger.info(f"{current_prefix}Text sent!")
            self.show_message_signal.emit(text_to_show)
        if gif_to_show:
            gif_path = gif_to_show
            self.logger.info(f"{current_prefix} Gif sent:{gif_path}")
            self.show_gif_signal.emit(gif_path, duration)
        if sound_to_play:
            sound_path = f"{config.MEDIA_FOLDER_SOUNDS}{sound_to_play}"
            self.logger.info(f"{current_prefix} Sound sent: {sound_path}")
            self.play_sound_signal.emit(sound_path)

        


    def show_message(self, message, animation_type=None, run_alone = True):
        """Send a message to be displayed on the overlay, optionally with animation"""
        self.logger.info(f"{self.logger_prefix}Emitting show_message_signal: {message}")
        self.show_message_signal.emit(message)
        
        if animation_type:
            self.animate_message(animation_type)
    
    def show_streamer_greeting(self, streamer_name, animation_type="bounce"):
        """Send a signal to show a greeting for a streamer with animation"""
        self.logger.info(f"{self.logger_prefix}Emitting show_streamer_greeting_signal: {streamer_name}")
        self.show_streamer_greeting_signal.emit(streamer_name)
        
        # Apply default animation for streamer greetings
        self.animate_message(animation_type)


#     OLD
#     def show_message(self, message):
#         """Send a message to be displayed on the overlay"""
#         self.logger.info(f"{self.logger_prefix}Emitting show_message_signal: {message}")

#         self.overlay_ready_for_new_action = False
#         self.show_message_signal.emit(message)
    
#     def show_streamer_greeting(self, streamer_name):
#         """Send a signal to show a greeting for a streamer"""
#         self.logger.info(f"{self.logger_prefix}Emitting show_streamer_greeting_signal: {streamer_name}")

#         self.overlay_ready_for_new_action = False
#         self.show_streamer_greeting_signal.emit(streamer_name)

# 

    def play_sound(self, sound_file):
        """Send a signal to play a sound"""
        self.logger.info(f"{self.logger_prefix}Emitting play_sound_signal: {sound_file}")

        self.overlay_ready_for_new_action = False
        self.play_sound_signal.emit(sound_file)
    
    def show_gif(self, gif_url, duration=5000, run_alone = True):
        """Send a signal to show a GIF for the specified duration (ms)"""
        self.logger.info(f"{self.logger_prefix}Emitting show_gif_signal: {gif_url}, duration: {duration}ms")

        self.overlay_ready_for_new_action = False
        self.show_gif_signal.emit(gif_url, duration)

    def show_full_greeting(self, streamer_name, greeting_text=None, gif_path=None, sound_path=None, duration=10000, animation_type="bounce"):
        """Send a signal to show a full greeting, may contain GIF, text, sound and duration for the specified duration (ms)"""
        self.logger.info(f"{self.logger_prefix}Emitting show_full_greeting_signal: {streamer_name}, {greeting_text}, {gif_path}, {sound_path}, duration: {duration}ms")

        self.overlay_ready_for_new_action = False
        self.show_full_greeting_signal.emit(streamer_name, greeting_text, gif_path, sound_path, duration)

    def animate_message(self, animation_type, **kwargs):
        """Send a signal to animate the current message"""
        self.logger.info(f"{self.logger_prefix}Emitting animate_message_signal: {animation_type}")
        self.animate_message_signal.emit(animation_type, kwargs)

    def hide_overlay(self):
        """Send a signal to hide the overlay"""
        self.logger.info(f"{self.logger_prefix}Emitting hide_overlay_signal")

        self.overlay_ready_for_new_action = False
        self.hide_overlay_signal.emit()