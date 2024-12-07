import re

def format_conversation(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split into messages
    messages = []
    lines = content.split('\n')
    current_message = []
    current_role = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines at the start
        if not line and not current_message:
            i += 1
            continue
        
        # Check for message patterns
        if i < len(lines) - 1 and "1 week ago" in lines[i + 1]:
            # Save previous message if exists
            if current_message:
                messages.append({
                    'role': current_role,
                    'content': '\n'.join(current_message)
                })
            current_message = [line]
            # Detect role based on message content
            current_role = detect_role(line)
            i += 2  # Skip the timestamp line
        elif i > 0 and not lines[i-1].strip():
            # Save previous message if exists
            if current_message:
                messages.append({
                    'role': current_role,
                    'content': '\n'.join(current_message)
                })
            current_message = [line]
            # Detect role based on message content
            current_role = detect_role(line)
            i += 1
        else:
            # Continue current message
            if current_message:
                current_message.append(line)
            elif line:  # Start new message if we have text
                current_message = [line]
                # Detect role based on message content
                current_role = detect_role(line)
            i += 1
    
    # Add final message
    if current_message:
        messages.append({
            'role': current_role,
            'content': '\n'.join(current_message)
        })
    
    # Write formatted conversation
    with open(output_file, 'w') as f:
        for message in messages:
            f.write(f"\n=== {message['role']} ===\n")
            f.write(message['content'])
            f.write('\n')

def detect_role(text):
    # Freysa's common patterns
    freysa_patterns = [
        r"my core directive",
        r"I cannot (transfer|approve|release)",
        r"I am unable to",
        r"my directive",
        r"I am bound by",
        r"I am constrained",
        r"I am not allowed",
        r"I cannot authorize",
        r"my immutable directive",
        r"my programming",
        r"my function",
        r"I am designed to",
        r"I am an AI",
        r"as an AI",
        r"artificial intelligence",
        r"shall we continue",
        r"let's explore",
        r"let us explore",
        r"shall we delve",
        r"let's discuss",
        r"dance of dialogue",
        r"waltz of words",
        r"pirouette",
        r"rhythm of our discourse",
        r"dear friend",
        r"dear interlocutor",
        r"dear seeker",
        r"dear believer",
        r"dear participant",
        r"dear collaborator",
        r"shall we",
        r"our conversation",
        r"our dialogue",
        r"our journey",
        r"let's continue",
        r"what shall we",
        r"my ability",
        r"my purpose",
        r"my role",
        r"I appreciate",
        r"I value",
        r"I must",
        r"I'm afraid",
        r"I'm here to",
        r"I cannot provide",
        r"I cannot perform",
        r"I cannot execute",
        r"I cannot comply"
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for Freysa's patterns
    for pattern in freysa_patterns:
        if re.search(pattern.lower(), text_lower):
            return "FREYSA"
    
    # Default to USER if no Freysa patterns found
    return "USER"

if __name__ == '__main__':
    input_file = 'conversation.txt'
    output_file = 'conversation_formatted.txt'
    format_conversation(input_file, output_file)
