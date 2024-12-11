import datetime
import os
import pickle
import subprocess
import sys
from dataclasses import dataclass
from datetime import timedelta
from typing import List

import gi.repository.GLib
from dbus.mainloop.glib import DBusGMainLoop
from mpris2 import Player, SomePlayers, Interfaces
from mpris2.types import Metadata_Map

DBusGMainLoop(set_as_default=True)

max_processes = 10
musicFolder = os.path.expanduser("~/Music/")


@dataclass
class Track:
    title: str
    album: str
    album_artist: str
    artist: str
    disc: int
    track: int
    start: timedelta
    stop: timedelta = timedelta(0)
    def escapedTitle(self):
        return self.title.replace('/', '_')

    def to_list(self, in_file: str) -> List[str]:
        global musicFolder
        metadata = [f"title={self.title}", f"album={self.album}", f"album_artist={self.album_artist}",
                    f"artist={self.artist}", f"disc={self.disc}", f"track={self.track}"]
        options = ["-ss", "{:.6f}".format(self.start.total_seconds() - 0.25), "-to",
                   "{:.6f}".format(self.stop.total_seconds() + 0.25)]
        for x in ffmpegCmd:
            yield x
        yield "-i"
        yield in_file
        for x in options:
            yield x
        for x in metadata:
            yield "-metadata"
            yield x
        if not (self.album == ""):
            yield musicFolder + self.album + "/" + self.escapedTitle() + ".mp3"
        else:
            yield musicFolder + self.escapedTitle() + ".mp3"


def make_track(mpris, start_time: datetime.datetime):
    get = mpris.Metadata.get
    album = get(Metadata_Map.ALBUM).title()
    album_artist = get(Metadata_Map.ALBUM_ARTIST)[0].title()
    artist = get(Metadata_Map.ARTIST)[0].title()
    disc_number = get(Metadata_Map.DISC_NUMBER).real
    track_number = get(Metadata_Map.TRACK_NUMBER).real
    title = get(Metadata_Map.TITLE).title()
    start = datetime.datetime.now() - start_time
    return Track(title=title, album=album, album_artist=album_artist, artist=artist, disc=disc_number,
                 track=track_number, start=start)


mainloop = gi.repository.GLib.MainLoop()

last_title: str = ""
times: List[Track]
first_title: str = ""
record_file = ""
record_format = "flac"
albums: set[str]
ffmpegCmd = ["ffmpeg", "-nostdin", "-hide_banner", "-y"]
recordStart: datetime.datetime = datetime.datetime.now()

pw_cat: subprocess.Popen[str]


def change_handler(self, *args, **kw):
    global recordStart
    metadata = args[0].get("Metadata")
    global mprisPlayer
    if metadata is None:
        metadata = mprisPlayer.Metadata
    get = metadata.get
    if mprisPlayer.PlaybackStatus == "Paused":

        if get(Metadata_Map.TITLE).title() == first_title:
            mprisPlayer.Stop()
            times[-1].stop = datetime.datetime.now() - recordStart
            write_split()
            return
        else:
            mprisPlayer.Play()

    global last_title

    new_title: str = get(Metadata_Map.TITLE)
    if new_title != last_title:
        global albums
        track = make_track(mprisPlayer, recordStart)
        albums.add(track.album)
        times[-1].stop = track.start
        times.append(track)
        last_title = track.title


def convert(tracks: List[Track], inputfile: str, albums: set[str], convert_to_mp3: bool = True):
    global musicFolder
    for album in albums:
        album.replace('/','_')
        if not os.path.exists(musicFolder + album):
            os.mkdir(musicFolder + album)
    converted_name = inputfile[:-len(record_format)] + "mp3"
    if convert_to_mp3:
        subprocess.run(ffmpegCmd + ["-i", f"{inputfile}", f"{converted_name}"])
    else:
        converted_name = inputfile
    processes = set()
    for x in tracks:
        processes.add(subprocess.Popen(list(x.to_list(converted_name))))
        if len(processes) >= max_processes:
            os.wait()
            processes.difference_update([p for p in processes if p.poll() is not None])
    # Check if all the child processes were closed
    for p in processes:
        if p.poll() is None:
            p.wait()


def write_split():
    global record_file, times, pw_cat, record_format

    global mainloop
    mainloop.quit()
    pw_cat.send_signal(4)
    print("Finished recording")
    data = {"inputFile": record_file, "albums": albums, "tracks": times}
    backup_file = open(list(albums)[0] + datetime.datetime.now().isoformat(timespec='seconds') + "_times.txt", "wb")
    pickle.dump(data, backup_file)

    convert(times, record_file, albums)
    mainloop.quit()
    sys.exit(0)

def main(player, mprisID):
    global mprisPlayer, track, first_title, last_title, albums, first_album, record_format, record_file, pw_cat, recordStart, times, mainloop
    if player==None:
        player = mprisID
    mprisPlayer = Player(dbus_interface_info={'dbus_uri': '.'.join([Interfaces.MEDIA_PLAYER, mprisID])})
    mprisPlayer.PropertiesChanged = change_handler
    track = make_track(mprisPlayer, datetime.datetime.now())
    first_title = track.title
    last_title = first_title

    albums = {track.album}
    first_album = track.album
    
    if not os.path.exists(musicFolder):
        os.mkdir(musicFolder)
    record_file = musicFolder + track.album + "." + record_format
    command = ['pw-record', '--target', player, f"{record_file}"]
    print(command)
    pw_cat = subprocess.Popen(command)
    recordStart = datetime.datetime.now()

    mprisPlayer.Play()
    track.start = timedelta(0)
    times = [track]
    mainloop.run()

def cli():
    import argparse
    global musicFolder
    parser = argparse.ArgumentParser(
            prog="mprisRecordPW",
            description="Record Audio with Pipewire and split it according to mpris data."
            )
    parser.add_argument('--playername', nargs="?", metavar="player", help="The name of the mpris Player", default="spotify", choices=SomePlayers.get_dict().values())
    parser.add_argument('--pw-name', dest="pwName",  help="The name to connect to in Pipewire")
    parser.add_argument('--convert', dest="backup_file", type=argparse.FileType('rb'), help="Convert an allready recorded file using the backup_file" )
    parser.add_argument('--dest', default=musicFolder, help="The folder in wich to save the recordings")
    arguments = parser.parse_args()
    musicFolder = arguments.dest
    if not musicFolder.endswith("/"):
        musicFolder = musicFolder+"/"
    if arguments.backup_file!=None:
        data = pickle.load(arguments.backup_file)
        print(data)
        record_file = data['inputFile']
        albums = data['albums']
        times = data['tracks']
        convert(times, record_file, albums)
    else:
        main(mprisID=arguments.playername, player=arguments.pwName)

if __name__ == '__main__':
    cli()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
