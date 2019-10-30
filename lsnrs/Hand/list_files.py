import os
import glob

def list_files(dir, ext=None, path=True, recursive=False):
    """
    Lists files in directory.
    :param dir: (str) Input directory in which to search files.
    :param ext: (str) Optional. Only return files with certain extension (e.g. '.txt').
    :param path: (bool) Return full path (default True).
    :param recursive: (bool) Apply recursive file matching (default False).
    :return: List of strings..
    """
    if ext is not None:
        ext_str = ext
    else:
        ext_str = ''

    if path:
        if recursive:
            return glob.glob(dir + '/**/*' + ext_str, recursive=True)
        else:
            return glob.glob(dir + '/*' + ext_str)
    else:
        if recursive:
            return [os.path.basename(x) for x in glob.glob(dir + '/**/*' + ext_str, recursive=True)]
        else:
            return [os.path.basename(x) for x in glob.glob(dir + '/*' + ext_str)]
