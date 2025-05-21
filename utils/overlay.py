import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QMovie
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
import os
from utils.overlay_animations import AnimatedLabel, AnimationManager

class OverlayWindow(QWidget):

    def __init__(self, logger, bridge=None):
        super().__init__()
        self.logger = logger
        self.logger_prefix = "utils/OverlayWindow=>"
        self.logger.info(f"{self.logger_prefix}Initializing overlay window")
        
        # Store bridge reference if provided
        self.bridge = bridge
        
        # Set window properties for transparency and always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set up the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Set up animation manager first
        self.animation_manager = AnimationManager(logger)

        # Create greeting label
        # self.greeting_label = QLabel("Hi there!")
        self.greeting_label = AnimatedLabel("Hi there!")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 120); padding: 20px; border-radius: 10px;")
        self.greeting_label.setFont(QFont("Arial", 24, QFont.Bold))
        
        # Add to layout
        layout.addWidget(self.greeting_label)

        # Set a default center anchor point for animations
        self.greeting_label.set_anchor_type(AnimatedLabel.CENTER)

        #Set up animation manager
        self.animation_manager = AnimationManager(logger)

        # Create a label for GIFs
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.hide()
        layout.addWidget(self.gif_label)
        
        # Set up sound effect player
        self.sound_player = QSoundEffect()
        
        # Set up timer for auto-hiding elements
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_current_display)

        # Set initial window size and position
        self.resize(400, 200)
        self.move(100, 100)  # You can adjust this to position on screen
        
        # Create cache directory if it doesn't exist
        self.cache_dir = os.path.join(os.getcwd(), "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.current_display = None  # Tracks what's currently showing
        
        self.logger.info(f"{self.logger_prefix}Overlay window initialized")


        self.gif_dict = {}

        
    def connect_bridge(self, bridge):
        """Connect to signals from the bridge"""
        self.bridge = bridge
        
        # Connect signals to slots
        self.bridge.show_message_signal.connect(self.show_message)
        self.bridge.show_streamer_greeting_signal.connect(self.show_streamer_greeting)
        self.bridge.play_sound_signal.connect(self.play_sound)
        self.bridge.show_gif_signal.connect(self.show_gif)
        self.bridge.show_full_greeting_signal.connect(self.show_full_greeting)
        self.bridge.hide_overlay_signal.connect(self.hide)
        self.bridge.animate_message_signal.connect(self.animate_message)
        
        
        self.logger.info(f"{self.logger_prefix}Bridge connected")


    def show_message(self, message, run_alone = True,  animation_type=None, duration = 5000):
        """Update the greeting label with a new message"""
        self.logger.info(f"{self.logger_prefix}Showing message: {message}")


        if run_alone:
            self.hide_current_display()        

        # Ensure the anchor point is set to center for proper display
        if hasattr(self.greeting_label, 'set_anchor_type'):
            self.greeting_label.set_anchor_type(AnimatedLabel.CENTER)

        # Reset scale to 1.0 to ensure we start from the base size
        if hasattr(self.greeting_label, 'set_scale'):
            self.greeting_label.set_scale(1.0)

        # Set the message text
        self.greeting_label.setText(message)
        
        # Adjust the label size to fit the content
        self.greeting_label.adjustSize()
        
        # Center the label in the window
        center_x = (self.width() - self.greeting_label.width()) // 2
        center_y = (self.height() - self.greeting_label.height()) // 2
        self.greeting_label.move(center_x, center_y)
        
        # Show the label
        self.greeting_label.show()
        self.current_display = "message"
        self.show()
        
        # Apply animation if specified
        if animation_type:
            self.animate_message(animation_type)
            #applying bounce... isn't here..
        
        # Auto-hide after specified duration
        self.hide_timer.start(duration)

        # self.greeting_label.setText(message)
        # self.greeting_label.show()
        # self.current_display = "message"
        # self.show()
        
        # # Apply animation if specified
        # if animation_type:
        #     self.animate_message(animation_type)
        
        # # Auto-hide after 5 seconds
        # self.hide_timer.start(duration)




    # def show_message(self, message, duration=5000, run_alone = True):
    #     """Update the greeting label with a new message"""
    #     self.logger.info(f"{self.logger_prefix}Showing message: {message} for {duration}ms")
        
    #     if run_alone:
    #         self.hide_current_display()
        
    #     self.greeting_label.setText(message)
    #     self.greeting_label.show()
    #     self.current_display = "message"
    #     self.show()
        
    #     # Auto-hide after 5 seconds
    #     self.hide_timer.start(duration)
        
    # def show_streamer_greeting(self, streamer_name):
    #     """Show a greeting for a streamer"""
    #     self.logger.info(f"{self.logger_prefix}Showing greeting for: {streamer_name}")
    #     # For now, just show a simple greeting
    #     self.show_message(f"Welcome to the stream, {streamer_name}!")
    #     # In the future, this could show custom graphics/animations

    
    def animate_message(self, animation_type, **kwargs):
        """Apply an animation to the current message"""

        if kwargs is None:
            kwargs = {}

        self.logger.info(f"{self.logger_prefix}Animating message with: {animation_type}, kwargs: {kwargs}")

        if self.current_display == "message":
            # Reset position to ensure animations start from a known state
            if hasattr(self.greeting_label, 'set_pos'):
                # Calculate center position in the parent window
                center_x = (self.width() - self.greeting_label.width()) // 2
                center_y = (self.height() - self.greeting_label.height()) // 2
                self.greeting_label.set_pos(QPoint(center_x, center_y))
                
            self.animation_manager.apply_animation(self.greeting_label, animation_type, **kwargs)
    
    
    def show_streamer_greeting(self, streamer_name, animation_type="bounce"):
        """Show a greeting for a streamer with animation"""
        self.logger.info(f"{self.logger_prefix}Showing greeting for: {streamer_name}")
        # For now, just show a simple greeting with animation
        self.show_message(f"Welcome to the stream, {streamer_name}!")
        self.animate_message(animation_type)


    def play_sound(self, sound_file):
        """Play a sound file"""
        self.logger.info(f"{self.logger_prefix}Playing sound: {sound_file}")
        
        # Make sure we have an absolute path
        if not os.path.isabs(sound_file):
            sound_file = os.path.join(os.getcwd(), sound_file)
            
        self.sound_player.setSource(QUrl.fromLocalFile(sound_file))
        self.sound_player.play()

    #Look locally in gif_dict first,   gif_dict[URL] = file_path
    #if gif is there use gif-viewer to show that local file
    #else download file, update gif_dict and give path to new file
    def get_gif(self, gif_url):
        pass
        
    def show_gif(self, gif_url, duration=5000, run_alone = True):
        """Show a GIF for the specified duration"""
        self.logger.info(f"{self.logger_prefix}Showing GIF: {gif_url} for {duration}ms")

        if run_alone:
            self.hide_current_display()
        
        # For this basic example, assuming gif_url is a local file path
        movie = QMovie(gif_url)
        self.gif_label.setMovie(movie)
        movie.start()
        
        self.gif_label.show()
        self.current_display = "gif"
        self.show()
        
        # Auto-hide after the specified duration
        self.hide_timer.start(duration)
        
    def hide_current_display(self):
        """Hide whatever is currently displayed"""
        if self.current_display == "message" or self.current_display == "full_greeting":
            self.greeting_label.hide()
        if self.current_display == "gif" or self.current_display == "full_greeting":
            if self.gif_label.movie():
                self.gif_label.movie().stop()
            self.gif_label.hide()

        self.current_display = None


    def show_full_greeting(self, streamer_name, greeting_text=None, gif_path=None, sound_path=None, show_duration=8000, animation_type="bounce"):
        """
        Show a complete greeting with text, GIF, and sound simultaneously.
        
        Args:
            streamer_name: Name of the streamer to greet
            greeting_text: Custom text to display (if None, a default is generated)
            gif_path: Path to the GIF file (if None, a default is used)
            sound_path: Path to the sound file (if None, a default is used)
            duration: How long to show the greeting in milliseconds
        """
        self.logger.info(f"{self.logger_prefix}Showing full greeting for: {streamer_name}")
        self.hide_current_display()
        
        # Set up default values if not provided
        if greeting_text is None:
            greeting_text = f"Welcome to the stream, {streamer_name}!"
        else:
            greeting_text = f"{greeting_text}!"
        
        if gif_path is None:
            gif_path = os.path.join(os.getcwd(), "overlay_media", "gifs", "temp_gif.gif")
        
        if sound_path is None:
            sound_path = os.path.join(os.getcwd(), "overlay_media", "sounds", "Alarm01.wav")
        
        # Use existing methods to show message, GIF, and play sound

        do_run_alone = False

  
        self.show_message(greeting_text, do_run_alone, None, show_duration)
        # Apply animation after showing the message
        if animation_type:
            self.logger.info(f"{self.logger_prefix}We got an animation type, what is it?{animation_type}")
            self.animate_message(animation_type)


        self.show_gif(gif_path, show_duration, run_alone=do_run_alone)

        self.play_sound(sound_path)
        
        # Update the current display state
        self.current_display = "full_greeting"
        



        #Old version, working nice, why change?
        # # Show the greeting text
        # self.greeting_label.setText(greeting_text)
        # self.greeting_label.show()
        

        # self.show_gif(gif_path, show_duration, run_alone = do_run_alone)
        # # self.show_message(greeting_text, do_run_alone, None, show_duration)
        # self.animation_manager.apply_animation(self.greeting_label, animation_type)


        # self.play_sound(sound_path)
        

        # # Update the current display state
        # self.current_display = "full_greeting"
        
        # # We don't need to call self.show() since show_message and show_gif already do that
        # # The hide timer is already started by show_gif with the specified duration

    def hide_message(self):
        """Hide the overlay window"""
        self.logger.info(f"{self.logger_prefix}Hiding overlay window")
        self.hide_current_display()
        self.hide()