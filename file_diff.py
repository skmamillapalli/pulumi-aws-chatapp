def diff_git_directories(dir1: str, dir2: str) -> dict:
    """
    Compares the files and directories between two directories

    Args:
        dir1 (str): Directory name
        dir2 (str): Directory name

    Returns:
        dict
    """
    dirs_cmp = filecmp.dircmp(dir1, dir2)

    # Dict to hold current match status, initially set to True(files match equal)
    match_status= {
        'status': True,
        'diff_files': []
    }

    if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or \
        len(dirs_cmp.funny_files) > 0:
        return { 
            'status': False, 
            'diff_files': dirs_cmp.left_only or dirs_cmp.right_only or dirs_cmp.funny_files
        }

    (_, mismatch, errors) =  filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return { 
            'status': False, 
            'diff_files': mismatch or errors
        }

    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        git_dir_diff = diff_git_directories(new_dir1, new_dir2)
        if not git_dir_diff['status']:
            return diff_git_directories(new_dir1, new_dir2)

    return match_status
