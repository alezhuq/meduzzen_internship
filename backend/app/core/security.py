from hashlib import blake2b
from .config import SECRET_HASH_KEY
from hmac import compare_digest

AUTH_SIZE = 16

SECRET_KEY = str.encode(str(SECRET_HASH_KEY))


def hash_string(cookie):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(cookie)
    return h.hexdigest().encode('utf-8')


def compare_hash(cookie, sig):
    """
    compares input (not hashed) string (cookie) with hashed value - sig
    :param cookie: unhashed byte string
    :param sig: hashed default string
    :return: True if values match, else false
    """
    good_sig = hash_string(cookie)
    return compare_digest(good_sig, sig)



