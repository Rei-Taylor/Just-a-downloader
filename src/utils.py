

def sanitize_filename(filename):
        invalid_chars = {
            '\\': '', '/': '', ':': '', '*': '', '?': '', '"': '', 
            '<': '', '>': '', '|': '', "'": '', '™': '', '®': '', '©': '',
            '\u00a9': '', '\u00ae': '', '\u2122': '', '\u2019': '', '\u2018': '',
            '\u201c': '', '\u201d': '', '\u2026': '', '\u2122': '', '\ufe0f': ''
        }
        
        for char, replacement in invalid_chars.items():
            filename = filename.replace(char, replacement)
        
        filename = ''.join(c for c in filename if ord(c) < 128)
        
        filename = filename.strip().strip('.')
        
        max_length = 200 
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename