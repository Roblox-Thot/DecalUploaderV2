# TODO: Make and add exceptions

__all__ = (
    "DecalUploaderException",
    "Banned"
)

class DecalUploaderException(Exception): pass
class Banned(DecalUploaderException): pass
