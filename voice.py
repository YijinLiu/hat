import os
import re
import subprocess

from gtts import gTTS
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy

def play_remote(audio_file: str, host: str, port: int = 22, username: str = None,
                password: str = None):
    if host == 'localhost':
        subprocess.run(['cvlc', audio_file], capture_output=True)
        return

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    client.connect(host, port = port, username = username, password = password)

    # Copy file to remote host if needed.
    sftp = client.open_sftp()
    remote_file = os.path.basename(audio_file)
    try:
        sftp.stat(remote_file)
    except IOError:
        print(f'Copying {audio_file} to {host}:{remote_file} ...')
        sftp.put(audio_file, remote_file)
    sftp.close()

    stdin, stdout, stderr = client.exec_command(f'cvlc {remote_file}')
    stdin.close()
    stdout.close()
    stderr.close()

    client.close()

illegal_filename_characters_pattern = re.compile(r'[\s+:/\\]+')
def _text_to_filename(text: str) -> str:
    return re.sub(illegal_filename_characters_pattern, '-', text)

def gtts(text: str, data_dir: str) -> str:
    mp3_file = os.path.join(data_dir, _text_to_filename(text) + '.mp3')
    if not os.path.exists(mp3_file):
        print(f'Will TTS "{text}" to {mp3_file}.')
        os.makedirs(data_dir, mode = 0o700, exist_ok = True)
        audio = gTTS(text = text, lang = 'en', slow = False)
        audio.save(mp3_file)
    return mp3_file

def gtts_remote(text: str, data_dir: str,
                host: str, port: int = 22,
                username: str = None, password: str = None):
    play_remote(gtts(text, data_dir), host, port = port, username = username, password = password)
