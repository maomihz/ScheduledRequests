# https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
def merge(source, destination=None, allowed_keys=None, blocked_keys=None):
    result = dict()
    keys = source.keys()
    if destination:
        keys |= destination.keys()
    if allowed_keys: # Whitelist mode
        keys &= allowed_keys
    if blocked_keys: # Blacklist mode
        keys -= blocked_keys
    for key in keys:
        if not destination or key not in destination:
            result[key] = source[key]
        elif key not in source:
            result[key] = destination[key]
        elif isinstance(source[key], dict) and isinstance(destination[key], dict):
            result[key] = merge(source[key], destination[key])
        else: # Fallback, take the source
            result[key] = source[key]
    return result
