import sys
import subprocess

def mount(path_to_smb, path_to_local_dir):
    retcode = subprocess.call(["/sbin/mount", "-t", "smbfs", path_to_smb, path_to_local_dir])

def unmount(path_to_local_dir):
    """Unmounts the local SMB directory"""
    retcode = subprocess.call(["/sbin/umount", path_to_local_dir])

def main():
    # smb location
    path_to_smb = str(sys.argv[1])
    path_to_local_dir = str(sys.argv[2])

    mount(path_to_smb, path_to_local_dir)

    input("Press any key to unmount: ")
    unmount(path_to_local_dir)

if __name__ == '__main__':
    main()