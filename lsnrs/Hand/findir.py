import os
import glob

def findir(dir, pattern=None, path=True, recursive=False):
    """
    Lists files / directories in directory.

    :param dir: (str) Input directory in which to search files.
    :param ext: (str) Optional. Only return files with certain extension (e.g. '.txt').
    :param path: (bool) Return full path (default True).
    :param recursive: (bool) Apply recursive file matching (default False).
    :return: List of files / directories.
    """
    if pattern is not None:
        pattern_str = pattern
    else:
        pattern_str = ''

    if path:
        if recursive:
            return glob.glob(dir + '/**/*' + pattern_str, recursive=True)
        else:
            return glob.glob(dir + '/*' + pattern_str)
    else:
        if recursive:
            return [os.path.basename(x) for x in glob.glob(dir + '/**/*' + pattern_str, recursive=True)]
        else:
            return [os.path.basename(x) for x in glob.glob(dir + '/*' + pattern_str)]
