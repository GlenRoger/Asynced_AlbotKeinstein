from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Property, QSize, QTimer, QObject, QAbstractAnimation
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QTransform, QFont
from PySide6.QtCore import QSequentialAnimationGroup, QParallelAnimationGroup, QPauseAnimation

class AnimatedLabel(QLabel):
    """A QLabel that supports various animations"""
    
    # Anchor point constants - important for the pulse message animation
    CENTER = 0
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._pos = QPoint(0, 0)
        self._opacity = 1.0
        self._scale = 1.0
        self._rotation = 0.0
        self._anchor_type = self.CENTER  # Default anchor type is center
        self._transform = QTransform() 

        self._anchor_point = QPoint(0, 0)  # Will be calculated based on anchor type
        self._base_font_size = 24  # Store the base font size
        self._base_font = QFont("Arial", self._base_font_size, QFont.Bold)
        self.setFont(self._base_font)        
        
        # Animation objects
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.rotation_animation = QPropertyAnimation(self, b"rotation")
        
        # Set animation defaults
        self.reset_animations()
    
    def reset_animations(self):
        """Reset animations to default state"""
        # Position animation
        self.pos_animation.setDuration(1000)
        self.pos_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Opacity animation
        self.opacity_animation.setDuration(1000)
        self.opacity_animation.setEasingCurve(QEasingCurve.Linear)
        
        # Scale animation
        self.scale_animation.setDuration(1000)
        self.scale_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Rotation animation
        self.rotation_animation.setDuration(1000)
        self.rotation_animation.setEasingCurve(QEasingCurve.OutQuad)

    def update_anchor_point(self):
        """Update the anchor point based on current size and anchor type"""
        if self._anchor_type == self.CENTER:
            self._anchor_point = QPoint(self.width() // 2, self.height() // 2)
        elif self._anchor_type == self.TOP_LEFT:
            self._anchor_point = QPoint(0, 0)
        elif self._anchor_type == self.TOP_RIGHT:
            self._anchor_point = QPoint(self.width(), 0)
        elif self._anchor_type == self.BOTTOM_LEFT:
            self._anchor_point = QPoint(0, self.height())
        elif self._anchor_type == self.BOTTOM_RIGHT:
            self._anchor_point = QPoint(self.width(), self.height())
    
    def resizeEvent(self, event):
        """Override resize event to update anchor point when size changes"""
        super().resizeEvent(event)
        self.update_anchor_point()
    
    def set_anchor_type(self, anchor_type):
        """Set the anchor type for transformations"""
        self._anchor_type = anchor_type
        self.update_anchor_point()
    
    def get_anchor_type(self):
        return self._anchor_type
    

    # Custom properties for animations
    def get_pos(self):
        return self._pos
    
    def set_pos(self, pos):
        self._pos = pos
        self.move(pos)
    
    pos = Property(QPoint, get_pos, set_pos)
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, opacity):
        self._opacity = opacity

        # Clamp opacity between 0 and 1
        if opacity > 1.0:
            opacity = 1.0
        elif opacity < 0.0:
            opacity = 0.0
        
        # Opacity in Qt stylesheets works differently than you might expect
        # For proper visibility, we'll apply both opacity and background-color alpha
        
        # Calculate the background color alpha based on opacity (0-255)
        bg_alpha = int(120 * opacity)
        
        # Apply opacity directly and also to background color alpha
        self.setStyleSheet(f"""
            color: rgba(255, 255, 255, {int(255 * opacity)});
            background-color: rgba(0, 0, 0, {bg_alpha});
            padding: 20px;
            border-radius: 10px;
        """)
        
        # For very low opacity, hide the widget entirely
        if opacity < 0.05:
            self.hide()
        else:
            self.show()

    
    opacity = Property(float, get_opacity, set_opacity)
    
    def get_scale(self):
        return self._scale

    def set_scale(self, scale):
        # Store current position to restore after scaling
        current_pos = self.get_pos()
        
        # Update the scale value
        self._scale = scale
        
        # Scale the font
        new_font = QFont(self._base_font)
        new_font.setPointSizeF(self._base_font_size * scale)
        self.setFont(new_font)
        
        # Update padding and other properties based on scale
        padding = int(20 * scale)
        border_radius = int(10 * scale)
        self.setStyleSheet(f"color: white; background-color: rgba(0, 0, 0, 120); padding: {padding}px; border-radius: {border_radius}px;")
        
        # Adjust size to fit the new content (important!)
        self.adjustSize()
        
        # Calculate position adjustment to maintain anchor point
        if self._anchor_type == self.CENTER:
            # Center the widget after scaling
            parent_width = self.parent().width() if self.parent() else 800
            parent_height = self.parent().height() if self.parent() else 600
            
            new_pos_x = (parent_width - self.width()) // 2
            new_pos_y = (parent_height - self.height()) // 2
            
            self.move(new_pos_x, new_pos_y)
        else:
            # For other anchor points, use the original position
            self.move(current_pos)

    # def set_scale(self, scale):
    #     self._scale = scale
    #     self.resize(int(self.sizeHint().width() * scale), int(self.sizeHint().height() * scale))
    
    scale = Property(float, get_scale, set_scale)
    
    def get_rotation(self):
        return self._rotation

    
    def set_rotation(self, rotation):
        self._rotation = rotation
        # For rotation, we use color changes to indicate rotation visually
        intensity = int(120 + 80 * (rotation % 360) / 360.0)
        self.setStyleSheet(f"color: white; background-color: rgba(0, 0, 0, {intensity}); padding: 20px; border-radius: 10px;")
    
    # def set_rotation(self, rotation):
    #     self._rotation = rotation
    #     # Use a QTransform to rotate the label since QLabel doesn't have setRotation
    #     transform = QTransform()
    #     transform.rotate(rotation)
    #     # Apply the transformation
    #     self.setTransform(transform)

    # def set_rotation(self, rotation):
    #     self._rotation = rotation
    #     self.setRotation(rotation)  # Only works in QGraphicsItem
    
    rotation = Property(float, get_rotation, set_rotation)


class AnimationManager:
    """Manages different animations for overlay elements"""
    
    def __init__(self, logger):
        self.logger = logger
        self.logger_prefix = "utils/AnimationManager=>"
        self.logger.info(f"{self.logger_prefix}Initializing animation manager")
        
        # Animation types
        self.animations = {
            "bounce": self.bounce_animation,
            "spin": self.spin_animation,
            "fade": self.fade_animation,               # Combined fade-in/display/fade-out
            "fadein": lambda widget, duration=2000: self.fading_animation(widget, duration, 0.0, 1.0),
            "fadeout": lambda widget, duration=2000: self.fading_animation(widget, duration, 1.0, 0.0),
            "slide_in": self.slide_in_animation,
            "pulse": self.pulse_animation,
            "roll": self.roll_animation,
            "shake": self.shake_animation,
            "wave": self.wave_animation,
        }
    
    def apply_animation(self, widget, animation_type, duration=2000, **kwargs):
        """Apply an animation to a widget"""
        self.logger.info(f"{self.logger_prefix}Applying {animation_type} animation to widget")

        widget.set_anchor_type(widget.CENTER)
        
        # For specific animations, different anchors might be better
        if animation_type == "slide_in" and "direction" in kwargs:
            direction = kwargs.get("direction", "right")
            if direction == "left":
                widget.set_anchor_type(widget.TOP_RIGHT)
            elif direction == "right":
                widget.set_anchor_type(widget.TOP_LEFT)
            elif direction == "top":
                widget.set_anchor_type(widget.BOTTOM_LEFT)
            elif direction == "bottom":
                widget.set_anchor_type(widget.TOP_LEFT)
    

        if animation_type.lower() in self.animations:
            return self.animations[animation_type](widget, duration, **kwargs)
        else:
            self.logger.warning(f"{self.logger_prefix}Unknown animation type: {animation_type}")
            return None
    
    def bounce_animation(self, widget, duration=2000, height=50, bounce_count=3):
        """Creates a bouncing animation"""

        try:
            # Get current position, this should now be the actual position property
            start_pos = widget.pos if hasattr(widget, 'pos') and not callable(widget.pos) else widget.pos()
            
            # Stop any existing animations
            widget.pos_animation.stop()
            
            # Configure animation with smoother easing curve
            widget.pos_animation.setDuration(duration)
            widget.pos_animation.setEasingCurve(QEasingCurve.OutElastic)  # More natural bounce
            
            # Calculate bounce positions
            widget.pos_animation.setStartValue(start_pos)
            widget.pos_animation.setEndValue(start_pos)
            
            # Use more natural keyframes for bouncing
            # First bounce (highest)
            widget.pos_animation.setKeyValueAt(0.2, QPoint(start_pos.x(), start_pos.y() - height))
            
            # Second bounce (about 60% of height)
            if bounce_count >= 2:
                widget.pos_animation.setKeyValueAt(0.5, QPoint(start_pos.x(), start_pos.y() - int(height * 0.6)))
            
            # Third bounce (about 30% of height)
            if bounce_count >= 3:
                widget.pos_animation.setKeyValueAt(0.8, QPoint(start_pos.x(), start_pos.y() - int(height * 0.3)))
            
            # Start the animation
            widget.pos_animation.start()
            return widget.pos_animation
        except Exception as e:
            self.logger.error(f"Error in bounce_animation: {e}")
            return None


        # start_pos = widget.pos if hasattr(widget, 'pos') else widget.pos()

        # #Dobbel bruk av pos, som atributt og funksjon, må skille på disse.
        # if hasattr(widget, 'get_pos'):
        #     start_pos = widget.get_pos()
        # else:
        #     start_pos = widget.pos()

        # try:
        #     # Stop any existing animations
        #     widget.pos_animation.stop()
            
        #     # Configure animation
        #     widget.pos_animation.setDuration(duration)
        #     widget.pos_animation.setEasingCurve(QEasingCurve.OutBounce)
            
        #     # Calculate bounce positions
        #     widget.pos_animation.setStartValue(start_pos)
        #     top_pos = QPoint(start_pos.x(), start_pos.y() - height)
        #     widget.pos_animation.setEndValue(start_pos)
            
        #     # Add intermediate keyframes for multiple bounces
        #     for i in range(1, bounce_count + 1):
        #         time_percent = (i / (bounce_count + 1)) * 100
        #         bounce_height = height * (bounce_count + 1 - i) / (bounce_count + 1)
        #         widget.pos_animation.setKeyValueAt(time_percent/100, 
        #                                         QPoint(start_pos.x(), start_pos.y() - bounce_height))
            
        #     widget.pos_animation.start()
        #     return widget.pos_animation
        # except Exception as e:
        #     self.logger.error(f"Error in bounce_animation: {e}")
        #     return None


        # # Stop any existing animations
        # widget.pos_animation.stop()
        
        # # Configure animation
        # widget.pos_animation.setDuration(duration)
        # widget.pos_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        # # Calculate bounce positions
        # widget.pos_animation.setStartValue(start_pos)
        # top_pos = QPoint(start_pos.x(), start_pos.y() - height)
        # widget.pos_animation.setEndValue(start_pos)
        
        # # Add intermediate keyframes for multiple bounces
        # for i in range(1, bounce_count + 1):
        #     time_percent = (i / (bounce_count + 1)) * 100
        #     bounce_height = height * (bounce_count + 1 - i) / (bounce_count + 1)
        #     widget.pos_animation.setKeyValueAt(time_percent/100, 
        #                                     QPoint(start_pos.x(), start_pos.y() - bounce_height))
        
        # widget.pos_animation.start()
        # return widget.pos_animation
    
    def spin_animation(self, widget, duration=2000, degrees=360, loops=1):
        """Creates a spinning animation"""

        #FUNKER IKKE LIKEVEL
        try:
            # Stop any existing animations
            widget.rotation_animation.stop()
            
            # Configure animation
            widget.rotation_animation.setDuration(duration)
            widget.rotation_animation.setStartValue(0.0)
            widget.rotation_animation.setEndValue(degrees)
            widget.rotation_animation.setLoopCount(loops)
            
            widget.rotation_animation.start()
            return widget.rotation_animation
        except Exception as e:
            self.logger.error(f"Error in spin_animation: {e}")
            # Fallback to a simpler animation if rotation isn't supported
            return self.bounce_animation(widget, duration)
            
            widget.rotation_animation.start()
            return widget.rotation_animation
    

    def fade_animation(self, widget, duration=3000, display_time=2000):
        """
        Creates a combined fade-in, display, fade-out animation sequence.
        
        Args:
            widget: The widget to animate
            duration: Total duration for the fade-in and fade-out portions (split evenly)
            display_time: How long to display the text at full opacity between fades
        """

        loops = 1

        try:


            
            opacity_anim_1 = self.fading_animation(1.0, 0.0)
            opacity_anim_2 = self.fading_animation(0.0, 1.0)

            widget.sequential_group.addAnimation(opacity_anim_1)
            
            # widget.sequential_group.addAnimation(opacity_anim_2)

            return widget.sequential_group

            # Stop any existing animations
            # widget.opacity_animation.stop()
            
            # # Configure animation to change background color as a visual cue
            # widget.opacity_animation.setDuration(duration)
            # widget.opacity_animation.setStartValue(0.0)
            # widget.opacity_animation.setEndValue(1.0)
            # widget.opacity_animation.setLoopCount(loops)  # Double the loops for full cycle
            

            # i = 0.0

            # # Add keyframes for color cycling
            # while i <= .5:
            #     widget.opacity_animation.setKeyValueAt(1.0 - i, i)
            #     widget.opacity_animation.setKeyValueAt(1.0 - i, 1.0 - i)

            #     i += 0.05

            #     # widget.opacity_animation.setKeyValueAt(0.25, 0.9)
            #     # widget.opacity_animation.setKeyValueAt(0.5, 0.3)
            #     # widget.opacity_animation.setKeyValueAt(0.75, 0.9)
            
            # widget.opacity_animation.start()
            # return widget.opacity_animation
        except Exception as e:
            self.logger.error(f"Error in fade_animation: {e}")
            # Fallback to a simpler animation
            # return self.pulse_animation(widget, duration)





        # try:
        #     # Make sure widget is visible but transparent to start
        #     if hasattr(widget, 'set_opacity'):
        #         widget.set_opacity(0.0)
            
        #     # Set the anchor type to center (if available)
        #     if hasattr(widget, 'set_anchor_type'):
        #         widget.set_anchor_type(widget.CENTER)
            
        #     # Stop any existing animations
        #     if hasattr(widget, 'opacity_animation'):
        #         widget.opacity_animation.stop()
            
        #     # Create a sequence animation group
        #     sequence = QSequentialAnimationGroup()
            
        #     # Get the fade-in and fade-out duration (half of the total fade duration)
        #     fade_duration = duration // 2
            
        #     # Create the fade-in animation using our reusable function
        #     fade_in = self.fading_animation(widget, fade_duration, 0.0, 1.0)
        #     # Don't start the animation yet, just add it to the sequence
        #     sequence.addAnimation(fade_in)
            
        #     # Create a pause animation to hold at full opacity
        #     pause = QPauseAnimation(display_time)
        #     sequence.addAnimation(pause)
            
        #     # Create the fade-out animation using our reusable function
        #     fade_out = self.fading_animation(widget, fade_duration, 1.0, 0.0)
        #     # Don't start the animation yet, just add it to the sequence
        #     sequence.addAnimation(fade_out)
            
        #     # Start the sequence
        #     sequence.start(QAbstractAnimation.DeleteWhenStopped)
            
        #     return sequence
        # except Exception as e:
        #     self.logger.error(f"Error in fade_animation: {e}")
        #     return None


    def fading_animation(self, widget, duration=2000, start_opacity=0.0, end_opacity=1.0):
        """
        Creates a fading animation with customizable start and end opacity.
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            start_opacity: Starting opacity value (0.0 = transparent, 1.0 = opaque)
            end_opacity: Ending opacity value (0.0 = transparent, 1.0 = opaque)
        """
        try:
            # Make sure the widget is visible but at the starting opacity
            if hasattr(widget, 'set_opacity'):
                widget.set_opacity(start_opacity)
            
            # Create and start opacity animation
            opacity_anim = QPropertyAnimation(widget, b"opacity")
            opacity_anim.setDuration(duration)
            opacity_anim.setStartValue(start_opacity)
            opacity_anim.setEndValue(end_opacity)
            opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
            
            return opacity_anim
        except Exception as e:
            self.logger.error(f"Error in fading_animation: {e}")
            return None

    # Keep these for compatibility
    # def fade_in_animation(self, widget, duration=2000):
    #     """Fades in a widget from transparent to opaque"""
    #     try:
    #         # Make sure widget is visible but transparent to start
    #         if hasattr(widget, 'set_opacity'):
    #             widget.set_opacity(0.0)
            
    #         # Create and start opacity animation
    #         opacity_anim = QPropertyAnimation(widget, b"opacity")
    #         opacity_anim.setDuration(duration)
    #         opacity_anim.setStartValue(0.0)
    #         opacity_anim.setEndValue(1.0)
    #         opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
    #         opacity_anim.start(QAbstractAnimation.DeleteWhenStopped)
            
    #         return opacity_anim
    #     except Exception as e:
    #         self.logger.error(f"Error in fade_in_animation: {e}")
    #         return None
    
    # def fade_out_animation(self, widget, duration=2000):
    #     """Fades out a widget from opaque to transparent"""
    #     try:
    #         # Create and start opacity animation
    #         opacity_anim = QPropertyAnimation(widget, b"opacity")
    #         opacity_anim.setDuration(duration)
    #         opacity_anim.setStartValue(1.0)
    #         opacity_anim.setEndValue(0.0)
    #         opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
    #         opacity_anim.start(QAbstractAnimation.DeleteWhenStopped)
            
    #         return opacity_anim
    #     except Exception as e:
    #         self.logger.error(f"Error in fade_out_animation: {e}")
    #         return None
    
    def slide_in_animation(self, widget, duration=2000, direction="right"):
        """Creates a slide-in animation from the specified direction"""

        try:
            # Get parent dimensions
            parent_width = widget.parent().width() if widget.parent() else 800
            parent_height = widget.parent().height() if widget.parent() else 600
            
            widget_width = widget.width()
            widget_height = widget.height()
            
            # Determine start and end positions
            # Use widget.pos (property) or widget.pos() (method) depending on what's available
            end_pos = widget.pos if hasattr(widget, 'pos') and not callable(widget.pos) else widget.pos()
            start_pos = QPoint(end_pos.x(), end_pos.y())
            
            if direction == "left":
                start_pos.setX(-widget_width)
            elif direction == "right":
                start_pos.setX(parent_width)
            elif direction == "top":
                start_pos.setY(-widget_height)
            elif direction == "bottom":
                start_pos.setY(parent_height)
            
            # Stop any existing animations
            widget.pos_animation.stop()
            
            # Configure animation
            widget.pos_animation.setDuration(duration)
            widget.pos_animation.setStartValue(start_pos)
            widget.pos_animation.setEndValue(end_pos)
            
            widget.pos_animation.start()
            return widget.pos_animation
        except Exception as e:
            self.logger.error(f"Error in slide_in_animation: {e}")
            return None
    

        # parent_width = widget.parent().width() if widget.parent() else 800
        # parent_height = widget.parent().height() if widget.parent() else 600
        
        # widget_width = widget.width()
        # widget_height = widget.height()
        
        # # Determine start and end positions
        # end_pos = widget.pos()
        # start_pos = QPoint(end_pos.x(), end_pos.y())
        
        # if direction == "left":
        #     start_pos.setX(-widget_width)
        # elif direction == "right":
        #     start_pos.setX(parent_width)
        # elif direction == "top":
        #     start_pos.setY(-widget_height)
        # elif direction == "bottom":
        #     start_pos.setY(parent_height)
        
        # # Stop any existing animations
        # widget.pos_animation.stop()
        
        # # Configure animation
        # widget.pos_animation.setDuration(duration)
        # widget.pos_animation.setStartValue(start_pos)
        # widget.pos_animation.setEndValue(end_pos)
        
        # widget.pos_animation.start()
        # return widget.pos_animation
    
    def pulse_animation(self, widget, duration=2000, min_scale=0.8, max_scale=1.2, pulse_count=2):
        """Creates a pulsing animation that changes widget size"""
        # Stop any existing animations
        try:
            # Set the anchor type to center to ensure scaling happens from the middle
            if hasattr(widget, 'set_anchor_type'):
                widget.set_anchor_type(widget.CENTER)
            
            # Stop any existing animations
            widget.scale_animation.stop()
            
            # Configure animation
            widget.scale_animation.setDuration(duration)
            widget.scale_animation.setStartValue(1.0)  # Start at normal size
            widget.scale_animation.setEndValue(1.0)    # End at normal size
            widget.scale_animation.setLoopCount(pulse_count)
            
            # Add keyframes for pulsing - more dynamic range for better effect
            widget.scale_animation.setKeyValueAt(0.15, max_scale)  # Grow quickly
            widget.scale_animation.setKeyValueAt(0.5, min_scale)   # Shrink to smaller than original
            widget.scale_animation.setKeyValueAt(0.85, max_scale)  # Grow again
            
            # Start the animation
            widget.scale_animation.start()
            return widget.scale_animation
        
        except Exception as e:
            self.logger.error(f"Error in pulse_animation: {e}")
            return None


        #Went out of bounds...
        # widget.scale_animation.stop()
        
        # # Configure animation
        # widget.scale_animation.setDuration(duration)
        # widget.scale_animation.setStartValue(1.0)
        # widget.scale_animation.setEndValue(1.0)
        # widget.scale_animation.setLoopCount(pulse_count)
        
        # # Add keyframes for pulsing
        # widget.scale_animation.setKeyValueAt(0.25, max_scale)
        # widget.scale_animation.setKeyValueAt(0.75, min_scale)
        
        # widget.scale_animation.start()
        # return widget.scale_animation
    
    def roll_animation(self, widget, duration=2000, distance=200, direction="right"):
        """Creates a rolling animation that moves across the screen"""
        try:
            # Get current position
            start_pos = widget.pos if hasattr(widget, 'pos') and not callable(widget.pos) else widget.pos()
            
            # Calculate end position based on direction
            if direction == "right":
                end_pos = QPoint(start_pos.x() + distance, start_pos.y())
            elif direction == "left":
                end_pos = QPoint(start_pos.x() - distance, start_pos.y())
            else:
                end_pos = start_pos
            
            # Stop any existing animations
            widget.pos_animation.stop()
            
            # Configure position animation
            widget.pos_animation.setDuration(duration)
            widget.pos_animation.setStartValue(start_pos)
            widget.pos_animation.setEndValue(end_pos)
            
            # Start animation
            widget.pos_animation.start()
            
            return widget.pos_animation
        except Exception as e:
            self.logger.error(f"Error in roll_animation: {e}")
            return None



        #DIdn't work anyway
        # """Creates a rolling animation that moves and rotates simultaneously"""
        # start_pos = widget.pos()
        
        # # Calculate end position based on direction
        # if direction == "right":
        #     end_pos = QPoint(start_pos.x() + distance, start_pos.y())
        # elif direction == "left":
        #     end_pos = QPoint(start_pos.x() - distance, start_pos.y())
        # else:
        #     end_pos = start_pos
        
        # # Stop any existing animations
        # widget.pos_animation.stop()
        # widget.rotation_animation.stop()
        
        # # Configure position animation
        # widget.pos_animation.setDuration(duration)
        # widget.pos_animation.setStartValue(start_pos)
        # widget.pos_animation.setEndValue(end_pos)
        
        # # Configure rotation animation
        # widget.rotation_animation.setDuration(duration)
        # widget.rotation_animation.setStartValue(0.0)
        
        # # Calculate rotations based on distance (approx 1 rotation per 100px)
        # rotations = distance / 100
        # widget.rotation_animation.setEndValue(360 * rotations * (1 if direction == "right" else -1))
        
        # # Start both animations
        # widget.pos_animation.start()
        # widget.rotation_animation.start()
        
        # return [widget.pos_animation, widget.rotation_animation]
    
    def shake_animation(self, widget, duration=1000, intensity=10, shake_count=5):
        """Creates a shaking animation"""

        try:
            # Get current position
            start_pos = widget.pos if hasattr(widget, 'pos') and not callable(widget.pos) else widget.pos()
            
            # Stop any existing animations
            widget.pos_animation.stop()
            
            # Configure animation
            widget.pos_animation.setDuration(duration)
            widget.pos_animation.setStartValue(start_pos)
            widget.pos_animation.setEndValue(start_pos)
            
            # Add keyframes for shaking
            for i in range(1, shake_count * 2):
                time_percent = (i / (shake_count * 2)) * 100
                direction = 1 if i % 2 == 0 else -1
                offset = intensity * direction
                widget.pos_animation.setKeyValueAt(time_percent/100, 
                                                QPoint(start_pos.x() + offset, start_pos.y()))
            
            widget.pos_animation.start()
            return widget.pos_animation
        except Exception as e:
            self.logger.error(f"Error in shake_animation: {e}")
            return None


        # start_pos = widget.pos()
        
        # # Stop any existing animations
        # widget.pos_animation.stop()
        
        # # Configure animation
        # widget.pos_animation.setDuration(duration)
        # widget.pos_animation.setStartValue(start_pos)
        # widget.pos_animation.setEndValue(start_pos)
        
        # # Add keyframes for shaking
        # for i in range(1, shake_count * 2):
        #     time_percent = (i / (shake_count * 2)) * 100
        #     direction = 1 if i % 2 == 0 else -1
        #     offset = intensity * direction
        #     widget.pos_animation.setKeyValueAt(time_percent/100, 
        #                                     QPoint(start_pos.x() + offset, start_pos.y()))
        
        # widget.pos_animation.start()
        # return widget.pos_animation
    
    def wave_animation(self, widget, duration=2000, amplitude=20, wave_count=2):
        """Creates a wave-like animation moving up and down"""

        try:
            # Get current position
            start_pos = widget.pos if hasattr(widget, 'pos') and not callable(widget.pos) else widget.pos()
            
            # Stop any existing animations
            widget.pos_animation.stop()
            
            # Configure animation
            widget.pos_animation.setDuration(duration)
            widget.pos_animation.setEasingCurve(QEasingCurve.InOutSine)
            widget.pos_animation.setStartValue(start_pos)
            widget.pos_animation.setEndValue(start_pos)
            
            # Add keyframes for wave motion
            keyframe_count = wave_count * 2
            for i in range(1, keyframe_count):
                time_percent = (i / keyframe_count) * 100
                sin_value = amplitude * (-1 if i % 2 == 0 else 1)
                widget.pos_animation.setKeyValueAt(time_percent/100, 
                                               QPoint(start_pos.x(), start_pos.y() + sin_value))
            
            widget.pos_animation.start()
            return widget.pos_animation
        except Exception as e:
            self.logger.error(f"Error in wave_animation: {e}")
            return None


        # start_pos = widget.pos()
        
        # # Stop any existing animations
        # widget.pos_animation.stop()
        
        # # Configure animation
        # widget.pos_animation.setDuration(duration)
        # widget.pos_animation.setEasingCurve(QEasingCurve.InOutSine)
        # widget.pos_animation.setStartValue(start_pos)
        # widget.pos_animation.setEndValue(start_pos)
        
        # # Add keyframes for wave motion
        # keyframe_count = wave_count * 2
        # for i in range(1, keyframe_count):
        #     time_percent = (i / keyframe_count) * 100
        #     sin_value = amplitude * (-1 if i % 2 == 0 else 1)
        #     widget.pos_animation.setKeyValueAt(time_percent/100, 
        #                                    QPoint(start_pos.x(), start_pos.y() + sin_value))
        
        # widget.pos_animation.start()
        # return widget.pos_animation