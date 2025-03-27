import logging


logger = logging.getLogger("command_handler")



#Important to implement:
# cooldown on user writing too much to bot
# cooldown on bot sending too much


def is_safe_message(message, user_id):
    # Length check
    if len(message) > 500:
        logger.warning(f"Message from {user_id} rejected: too long ({len(message)} chars)")
        return False
        
    # Check for command rate limiting (implementation depends on how you track users)
    # if is_user_rate_limited(user_id):
    #     logger.warning(f"Message from {user_id} rejected: rate limited")
    #     return False
    
    # Add other checks as needed
    
    return True


#If a command is safe and can be considered as a command
def command_handler(msg):
    print(f"In command handler, recieved:{msg}")





def is_safe_command(command_text):
    # Define explicitly what characters are allowed
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+- øæåÆØÅ')
    
    # Check each character in the command
    disallowed_found = []
    for char in command_text:
        if char not in allowed_chars:
            disallowed_found.append(char)
    
    # If we found any disallowed characters
    if disallowed_found:
        disallowed_str = ', '.join([f"'{c}'" for c in set(disallowed_found)])
        logger.info(f"Command rejected. Disallowed characters found: {disallowed_str} in: {command_text}")
        return False
    
    return True  