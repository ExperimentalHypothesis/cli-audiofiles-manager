import os, re, argparse

class RegexPatternsProvider:
    """ Base class for encapsulating regex patterns to have them in one place """

    # one CD leading zero (01 song name.mp3)
    p1_song = re.compile(r"(^\d\d)(\s)([\w+\s().,:#=\-`&'?!\[\]]*)$")
    # one CD no leading zero (1 song name.mp3)
    p2_song = re.compile(r"(^\d)(\s)([A-Z][\w+\s().,\-:#=`&'?!\[\]]*)$")
    # multiple CD separated (1 01 song name.mp3)
    p3_song = re.compile(r"(^\d\s\d\d)(\s)([\w+\s().\-,:#=&`'?!\[\]]*)$")
    # multiple CD (101 song name.mp3)
    p4_song = re.compile(r"(^\d\d\d)(\s)([\w+\s().,:\-#=&'?`!\[\]]*)$")

    # name of album
    p1_album = re.compile(r"^[a-zA-zä\s!'&.,()\-]*[\d]?[\d]?[()]?$")
    # 2002 name of album
    p2_album = re.compile(r"^(\d\d\d\d)(\s?)([a-zA-z\s!'’&.()+~,üäöáçăóéűęěščřžýáíţ0-9\-]*)$")
    # name of album, 2002
    p3_album = re.compile(r"^([a-zA-z\s!'&]*)([,]\s)(\d\d\d\d)$")

    # 01 name of song -- name of artist -- name of album
    p_broadcast = re.compile(r"^(\d\d)(\s[A-Z][\w\s!'’&.()+~,üäöáçăóéűęěščřžýáíţ0-9\-]*)--(\s[A-Z][\w\s!'’&.()+~,üäöáçăóéűęěščřžýáíţ0-9\-]*)--(\s[A-Z][\w\s!'’&.()+~,üäöáçăóéűęěščřžýáíţ0-9\-]*)$")

    def __str__(self):
        return "Class for encapsulating regex patterns. Used as base class for other that inherits the data. It does not contain any functions. All data are class-level"

class RegexMatcher(RegexPatternsProvider):
    """ Class for checking regex matches for songs and albums. It holds paths of all matched and unmatched files or folders in separated sets for further processing. """

    ext =  ext = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.alac', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.nmf', '.nsf', '.ogg', '.oga', '.mogg', '.opus', '.ra', '.rm', '.raw', '.sln', '.tta', '.voc', '.vox', '.wav', '.wma', '.wv', '.webm', '.8svx']

    def __init__(self, root:str) -> None:
        self._root = root

        self.p1_song_matches = set()
        self.p2_song_matches = set()
        self.p3_song_matches = set()
        self.p4_song_matches = set()
        self.no_song_matches = set()
        self.p1_album_matches = set()
        self.p2_album_matches = set()
        self.p3_album_matches = set()
        self.no_album_matches = set()


    def __str__(self) -> str:
        return f"RegexMatcher - {self.root}"


    def __repr__(self) -> str:
        return f"RegexMatcher(root='{self.root}')"


    @property
    def root(self):
        return self._root


    @root.setter
    def root(self, value:str):
        if value != self._root:
            self.p1_song_matches.clear()
            self.p2_song_matches.clear()
            self.p3_song_matches.clear()
            self.p4_song_matches.clear()
            self.no_song_matches.clear()
            self.p1_album_matches.clear()
            self.p2_album_matches.clear()
            self.p3_album_matches.clear()
            self.no_album_matches.clear()

            self._root = value


    def get_all_regex_song_match(self) -> None:
        """ Get all audio files with particular regex pattern """
        self.p1_song_matches.clear()
        self.p2_song_matches.clear()
        self.p3_song_matches.clear()
        self.p4_song_matches.clear()
        self.no_song_matches.clear()

        for artist_folder in os.listdir(os.path.join(self.root)):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist_folder)):
                continue
            for album_folder in os.listdir(os.path.join(self.root, artist_folder)):
                for file in os.listdir(os.path.join(self.root, artist_folder, album_folder)):
                    if file.endswith(tuple(RegexMatcher.ext)):
                        file, ext = os.path.splitext(file)
                        if RegexMatcher.p1_song.match(file):
                            print(f"{file+ext} -> p1_song match")
                            self.p1_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))
                        elif RegexMatcher.p2_song.match(file):
                            print(f"{file+ext} -> p2_song match")
                            self.p2_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))
                        elif RegexMatcher.p3_song.match(file):
                            print(f"{file+ext} -> p3_song match")
                            self.p3_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))
                        elif RegexMatcher.p4_song.match(file):
                            print(f"{file+ext} -> p4_song match")
                            self.p4_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))
                        else:
                            self.no_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))
                            print(f"{file+ext}  :: path {os.path.join(artist_folder, album_folder)} -> no regex match")


    def get_no_regex_song_match(self) -> None:
        """ Get audio files that did not match any regex pattern """
        self.no_song_matches.clear()
        for artist_folder in os.listdir(os.path.join(self.root)):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist_folder)):
                continue
            for album_folder in os.listdir(os.path.join(self.root, artist_folder)):
                for file in os.listdir(os.path.join(self.root, artist_folder, album_folder)):
                    if file.endswith(tuple(RegexMatcher.ext)):
                        file, ext = os.path.splitext(file)
                        if RegexMatcher.p1_song.match(file):      continue
                        elif RegexMatcher.p2_song.match(file):    continue
                        elif RegexMatcher.p3_song.match(file):    continue
                        elif RegexMatcher.p4_song.match(file):    continue
                        else:
                            print(f"{file+ext} :: path {os.path.join(artist_folder, album_folder)} -> no regex match")
                            self.no_song_matches.add(os.path.join(self.root, artist_folder, album_folder, file+ext))


    def get_all_regex_album_match(self) -> None:
        """ Get regex match pattern for all albums """
        self.p1_album_matches.clear()
        self.p2_album_matches.clear()
        self.p3_album_matches.clear()
        self.no_album_matches.clear()

        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                if RegexMatcher.p1_album.match(album):
                    print(album, f" -> p1_album match :: path {os.path.join(self.root, artist)}")
                    self.p1_album_matches.add(os.path.join(self.root, artist, album))
                elif RegexMatcher.p2_album.match(album):
                    print(album, f" -> p2_album match :: path {os.path.join(self.root, artist)}")
                    self.p2_album_matches.add(os.path.join(self.root, artist, album))
                elif RegexMatcher.p3_album.match(album):
                    print(album, f" -> p3_album match :: path {os.path.join(self.root, artist)}")
                    self.p3_album_matches.add(os.path.join(self.root, artist, album))
                else:
                    print(album, " -> no match")
                    self.no_album_matches.add(os.path.join(self.root, artist, album))


    def get_no_regex_album_match(self) -> None:
        """ Get albums that did not match any regex pattern """
        self.no_album_matches.clear()
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                if RegexMatcher.p1_album.match(album):      continue
                elif RegexMatcher.p2_album.match(album):    continue
                elif RegexMatcher.p3_album.match(album):    continue
                else:
                    print(f"{album} :: path {os.path.join(self.root, artist)} -> no regex match")
                    self.no_album_matches.add(os.path.join(self.root, artist, album))


    @staticmethod
    def count_albums_with_regex_matched_songs(s:set) -> int:
        """ Returns number of albums whose songs did match particular regex pattern.
        Used mostly with set of not matched songs to see, how many albums will be tagged """
        uni_paths = {os.path.split(song) for song in s}
        return len(uni_paths)


    @staticmethod
    def print_albums_with_regex_matched_songs(s:set) -> int:
        """ Prints the albums whose songs did match particular regex pattern.
        Used mostly with set of not matched songs to see, which albums will not be tagged """
        uni_paths = {os.path.dirname(song) for song in s}
        for i in uni_paths:
            print(i)


def main():
    """ Run the script as command line interface """
    parser = argparse.ArgumentParser(description="Checking name integrity based on patterns")

    parser.add_argument("-q", "--quite", action="store_true")
    parser.add_argument("-p", "--path", help="root path to the folder with audio", default=os.getcwd())
    parser.add_argument("-as", "--allsongs", action="store_true")
    parser.add_argument("-aa", "--allalbums", action="store_true")
    parser.add_argument("-ns", "--nosongs", action="store_true")
    parser.add_argument("-na", "--noalbums", action="store_true")

    args = parser.parse_args()
    path = args.path
    show_all_songs_matches = args.allsongs
    show_no_songs_matches = args.nosongs
    show_all_albums_matches = args.allalbums
    show_no_albums_matches = args.noalbums

    r = RegexMatcher(path)
    if args.quite:
        if show_all_albums_matches:
            r.get_all_regex_album_match()
        if show_all_songs_matches:
            r.get_all_regex_song_match()
        if show_no_songs_matches:
            r.get_no_regex_song_match()
        if show_no_albums_matches:
            r.get_no_regex_album_match()
    else:
        if show_all_albums_matches:
            print(f":::showing all albums that had matched a particular pattern.:::\n")
            r.get_all_regex_album_match()
        if show_all_songs_matches:
            print(f":::showing all songs that had matched a particular pattern:::\n")
            r.get_all_regex_song_match()
        if show_no_songs_matches:
            print(f":::showing all songs that did not match any particular pattern:::\n")
            r.get_no_regex_song_match()
        if show_no_albums_matches:
            print(f":::showing all albums that did not match any particular pattern:::\n")
            r.get_no_regex_album_match()


if __name__ == "__main__":
    main()
