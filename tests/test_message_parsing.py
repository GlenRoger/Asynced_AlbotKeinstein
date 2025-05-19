# test_message_parsing.py
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.send_message import Message_sending_central
from utils.logger import LogThis

def test_find_msg_and_sender_with_command():
    """Test parsing a command message"""
    # Setup
    logger = LogThis().get_logger()
    msg_central = Message_sending_central(logger)
    
    # Test data - a real Twitch message with a command
    twitch_message = ":coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :%hei"
    
    # Run the function
    result = msg_central.find_msg_and_sender(twitch_message)
    
    # Check results
    username, command = result
    assert username == "coolingenwastaken"
    assert command == "hei"

def test_find_msg_and_sender_without_command():
    """Test parsing a regular message (not a command)"""
    # Setup
    logger = LogThis().get_logger()
    msg_central = Message_sending_central(logger)
    
    # Test data - a regular chat message (no % prefix)
    twitch_message = ":coolingenwastaken!coolingenwastaken@coolingenwastaken.tmi.twitch.tv PRIVMSG #coolingenwastaken :hello everyone"
    
    # Run the function
    result = msg_central.find_msg_and_sender(twitch_message)
    
    # Check results
    username, command = result
    assert username == "coolingenwastaken"
    assert command == ""  # Should be empty since it's not a command