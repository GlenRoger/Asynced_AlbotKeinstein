from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, Property, QSize, QTimer, QObject
from PySide6.QtWidgets import QLabel

class AnimatedLabel(QLabel):
    """A QLabel that supports various animations"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._pos = QPoint(0, 0)
        self._opacity = 1.0
        self._scale = 1.0
        self._rotation = 0.0
        
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
        self.setStyleSheet(f"color: white; background-color: rgba(0, 0, 0, 120); padding: 20px; border-radius: 10px; opacity: {opacity};")
    
    opacity = Property(float, get_opacity, set_opacity)
    
    def get_scale(self):
        return self._scale
    
    def set_scale(self, scale):
        self._scale = scale
        self.resize(int(self.sizeHint().width() * scale), int(self.sizeHint().height() * scale))
    
    scale = Property(float, get_scale, set_scale)
    
    def get_rotation(self):
        return self._rotation
    
    def set_rotation(self, rotation):
        self._rotation = rotation
        self.setRotation(rotation)  # Only works in QGraphicsItem
    
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
            "fade": self.fade_animation,
            "slide_in": self.slide_in_animation,
            "pulse": self.pulse_animation,
            "roll": self.roll_animation,
            "shake": self.shake_animation,
            "wave": self.wave_animation,
        }
    
    def apply_animation(self, widget, animation_type, duration=2000, **kwargs):
        """Apply an animation to a widget"""
        self.logger.info(f"{self.logger_prefix}Applying {animation_type} animation to widget")
        
        if animation_type in self.animations:
            return self.animations[animation_type](widget, duration, **kwargs)
        else:
            self.logger.warning(f"{self.logger_prefix}Unknown animation type: {animation_type}")
            return None
    
    def bounce_animation(self, widget, duration=2000, height=50, bounce_count=3):
        """Creates a bouncing animation"""
        start_pos = widget.pos()
        
        # Stop any existing animations
        widget.pos_animation.stop()
        
        # Configure animation
        widget.pos_animation.setDuration(duration)
        widget.pos_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        # Calculate bounce positions
        widget.pos_animation.setStartValue(start_pos)
        top_pos = QPoint(start_pos.x(), start_pos.y() - height)
        widget.pos_animation.setEndValue(start_pos)
        
        # Add intermediate keyframes for multiple bounces
        for i in range(1, bounce_count + 1):
            time_percent = (i / (bounce_count + 1)) * 100
            bounce_height = height * (bounce_count + 1 - i) / (bounce_count + 1)
            widget.pos_animation.setKeyValueAt(time_percent/100, 
                                            QPoint(start_pos.x(), start_pos.y() - bounce_height))
        
        widget.pos_animation.start()
        return widget.pos_animation
    
    def spin_animation(self, widget, duration=2000, degrees=360, loops=1):
        """Creates a spinning animation"""
        # Stop any existing animations
        widget.rotation_animation.stop()
        
        # Configure animation
        widget.rotation_animation.setDuration(duration)
        widget.rotation_animation.setStartValue(0.0)
        widget.rotation_animation.setEndValue(degrees)
        widget.rotation_animation.setLoopCount(loops)
        
        # For actual rotation effect, we need to use QGraphicsEffect
        # Since QLabel doesn't directly support rotation, we're using a workaround
        # This will be applied in the OverlayWindow class
        
        widget.rotation_animation.start()
        return widget.rotation_animation
    
    def fade_animation(self, widget, duration=2000, start_opacity=0.0, end_opacity=1.0):
        """Creates a fade in/out animation"""
        # Stop any existing animations
        widget.opacity_animation.stop()
        
        # Configure animation
        widget.opacity_animation.setDuration(duration)
        widget.opacity_animation.setStartValue(start_opacity)
        widget.opacity_animation.setEndValue(end_opacity)
        
        widget.opacity_animation.start()
        return widget.opacity_animation
    
    def slide_in_animation(self, widget, duration=2000, direction="right"):
        """Creates a slide-in animation from the specified direction"""
        parent_width = widget.parent().width() if widget.parent() else 800
        parent_height = widget.parent().height() if widget.parent() else 600
        
        widget_width = widget.width()
        widget_height = widget.height()
        
        # Determine start and end positions
        end_pos = widget.pos()
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
    
    def pulse_animation(self, widget, duration=2000, min_scale=0.8, max_scale=1.2, pulse_count=2):
        """Creates a pulsing animation that changes widget size"""
        # Stop any existing animations
        widget.scale_animation.stop()
        
        # Configure animation
        widget.scale_animation.setDuration(duration)
        widget.scale_animation.setStartValue(1.0)
        widget.scale_animation.setEndValue(1.0)
        widget.scale_animation.setLoopCount(pulse_count)
        
        # Add keyframes for pulsing
        widget.scale_animation.setKeyValueAt(0.25, max_scale)
        widget.scale_animation.setKeyValueAt(0.75, min_scale)
        
        widget.scale_animation.start()
        return widget.scale_animation
    
    def roll_animation(self, widget, duration=2000, distance=200, direction="right"):
        """Creates a rolling animation that moves and rotates simultaneously"""
        start_pos = widget.pos()
        
        # Calculate end position based on direction
        if direction == "right":
            end_pos = QPoint(start_pos.x() + distance, start_pos.y())
        elif direction == "left":
            end_pos = QPoint(start_pos.x() - distance, start_pos.y())
        else:
            end_pos = start_pos
        
        # Stop any existing animations
        widget.pos_animation.stop()
        widget.rotation_animation.stop()
        
        # Configure position animation
        widget.pos_animation.setDuration(duration)
        widget.pos_animation.setStartValue(start_pos)
        widget.pos_animation.setEndValue(end_pos)
        
        # Configure rotation animation
        widget.rotation_animation.setDuration(duration)
        widget.rotation_animation.setStartValue(0.0)
        
        # Calculate rotations based on distance (approx 1 rotation per 100px)
        rotations = distance / 100
        widget.rotation_animation.setEndValue(360 * rotations * (1 if direction == "right" else -1))
        
        # Start both animations
        widget.pos_animation.start()
        widget.rotation_animation.start()
        
        return [widget.pos_animation, widget.rotation_animation]
    
    def shake_animation(self, widget, duration=1000, intensity=10, shake_count=5):
        """Creates a shaking animation"""
        start_pos = widget.pos()
        
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
    
    def wave_animation(self, widget, duration=2000, amplitude=20, wave_count=2):
        """Creates a wave-like animation moving up and down"""
        start_pos = widget.pos()
        
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