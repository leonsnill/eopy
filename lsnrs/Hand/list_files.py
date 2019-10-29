import os
import glob

def list_files(dir, ext, path=True, recursive=False):
    """
    Lists files in directory.
    :param dir: (str) Input directory.
    :param ext: (str) File extension, e.g. '.txt'.
    :param path: (bool) Return full path (default True).
    :param recursive: (bool) Apply recursive file matching (default False).
    :return: List of strings..
    """
    if path:
        if recursive:
            return glob.glob(dir + '/**/*' + ext, recursive=True)
        else:
            return glob.glob(dir + '/*' + ext)
    else:
        if recursive:
            return [os.path.basename(x) for x in glob.glob(dir + '/**/*' + ext, recursive=True)]
        else:
            return [os.path.basename(x) for x in glob.glob(dir + '/*' + ext)]
