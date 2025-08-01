import os
import time
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Konfiguration
SERVER = "192.168.137.184"
USERNAME = "blockbastaz"
KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")  # Pfad zu deinem privaten SSHKey
REMOTE_PATH = "/home/blockbastaz/EchoCloud"  # Zielordner auf Server (bereits korrekt)
LOCAL_PATH = "C:/Users/royal/PycharmProjects/EchoCloud"  # Projektverzeichnis auf Windows

class SyncHandler(FileSystemEventHandler):
    def __init__(self, sftp):
        self.sftp = sftp

    def on_modified(self, event):
        if not event.is_directory:
            self.upload_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.upload_file(event.src_path)

    def upload_file(self, path):
        # Ignoriere temporäre oder Backup-Dateien
        if not os.path.isfile(path):
            return
        if path.endswith('~') or path.endswith('.swp') or path.endswith('.tmp'):
            return

        relative_path = os.path.relpath(path, LOCAL_PATH)
        remote_file = os.path.join(REMOTE_PATH, relative_path).replace("\\", "/")

        # Erstelle evtl. fehlende Remote-Verzeichnisse
        dir_path = os.path.dirname(remote_file)
        try:
            self.sftp.stat(dir_path)
        except FileNotFoundError:
            mkdir_p(self.sftp, dir_path)

        self.sftp.put(path, remote_file)
        print(f"[Synced] {path} -> {remote_file}")


def mkdir_p(sftp, remote_directory):
    dirs = remote_directory.split("/")
    current = ""
    for d in dirs:
        if d == "":
            continue
        current += f"/{d}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)

def upload_dir(sftp, local_dir, remote_dir):
    """Rekursiv komplettes Verzeichnis hochladen"""
    for root, dirs, files in os.walk(local_dir):
        # Erstelle Remote-Verzeichnisse
        relative_path = os.path.relpath(root, local_dir)
        remote_path = os.path.join(remote_dir, relative_path).replace("\\", "/")
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            mkdir_p(sftp, remote_path)

        # Dateien hochladen
        for file in files:
            local_file = os.path.join(root, file)
            remote_file = os.path.join(remote_path, file).replace("\\", "/")
            sftp.put(local_file, remote_file)
            print(f"[Initial Upload] {local_file} -> {remote_file}")

def main():
    key = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)

    transport = paramiko.Transport((SERVER, 22))
    transport.connect(username=USERNAME, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Initialer Upload des kompletten Projektordners
    upload_dir(sftp, LOCAL_PATH, REMOTE_PATH)

    event_handler = SyncHandler(sftp)
    observer = Observer()
    observer.schedule(event_handler, LOCAL_PATH, recursive=True)
    observer.start()

    print("[Watcher started] Änderungen werden live hochgeladen... (Strg+C zum Beenden)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    sftp.close()
    transport.close()

if __name__ == "__main__":
    main()
