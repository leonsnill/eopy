import os
import re

def finder(directory, suffix="", pattern="", full_path=False, incl_dir=False, recursive=False):
    """
    List files and directories in directory. Allows for specifying file endings and patterns in strings. Recursive
    option available.

    Args:
        directory: Input directory.
        suffix: (optional) Returns only files with provided suffix.
        pattern: (optional) Return only files and directories that match a given string at any position.
        full_path: Return full absolute path (default = False).
        incl_dir: Include directories in search (default = False).
        recursive: List files and directories in subfolders (default = False).

    Returns: List of files/directories.

    """
    # initialise output
    finder_list = []

    # iterate through elements in input directory
    for e in os.scandir(directory):

        # files
        if e.is_file() and e.path.endswith(suffix) and re.search(pattern, e.name):
            if full_path:
                finder_list.append(e.path)
            else:
                finder_list.append(e.name)

        # directories
        if e.is_dir() and (incl_dir | recursive):
            if re.search(pattern, e.name):
                if full_path:
                    finder_list.append(e.path)
                else:
                    finder_list.append(e.name)

            # reapply function if recursive
            if recursive:
                finder_list2 = finder(e.path, suffix, pattern, full_path, recursive)
                finder_list = finder_list + finder_list2

    return finder_list
