"""
General utilities
-----------------
"""

import collections.abc as cabc


def merge_patch(target: cabc.MutableMapping, patch):
    """Apply JSON merge patch to target

    This function is implementation of the JSON Merget Patch algorithm
    described in RFC 7396. ``target`` is patched in place.

    Parameters:
        target: The target object
        patch: The patch to apply

    Return:
        The result of applying the patch. The returned object may or
        may not be the ``target`` parameter.
    """
    if isinstance(patch, cabc.Mapping):
        if not isinstance(target, cabc.Mapping):
            target = {}
        for key in list(patch.keys()):
            if (value := patch[key]) is None:
                target.pop(key, None)
            else:
                target[key] = merge_patch(target.get(key, {}), value)
        return target
    return patch
