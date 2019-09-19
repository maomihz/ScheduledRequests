# https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
def merge(source, destination=dict(), allowed_keys=set(), blocked_keys=set()):
    result = dict()
    keys = source.keys() | destination.keys()
    if allowed_keys: # Whitelist mode
        keys &= allowed_keys
    if blocked_keys: # Blacklist mode
        keys -= blocked_keys
    for key in keys:
        if key not in destination:
            result[key] = source[key]
        elif key not in source:
            result[key] = destination[key]
        elif isinstance(source[key], dict) and isinstance(destination[key], dict):
            result[key] = merge(source[key], destination[key])
        else: # Fallback, take the source
            result[key] = source[key]
    return result

request_params = {
    "url", "method", "params", "data", "json", "headers", "cookies", "files",
    "auth", "timeout",
#     "allow_redirects", "proxies", "verify", "stream", "cert"
}
