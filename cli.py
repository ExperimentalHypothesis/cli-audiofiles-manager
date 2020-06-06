""" Microframework for managing audiofiles on filesystem """


import os, re, argparse, shutil, subprocess

class DataProvider:
    """ Base class for encapsulating file extension and regex patterns to have them in one place. It does not contain any functions. All data are class-level """

    ext = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.alac', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.nmf', '.nsf', '.ogg', '.oga', '.mogg', '.opus', '.ra', '.rm', '.raw', '.sln', '.tta', '.voc', '.vox', '.wav', '.wma', '.wv', '.webm', '.8svx']

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


class NameNormalizer(DataProvider):
    """ Class for clearing out the names of songs, artists and albums, the goal is to have:
        - Clear {artist_name} in the form of plain "artist name"          => for example "Steve Roach"
        - Clear {album_name} in the form of plain "album name"            => for example "Structures Of Silence"
        - Clear {song name} in the of "song name" with track number       => for example "01 Early Man.mp3"
    """

    def __init__(self, root:str):
        """ Specify the root path """
        self.root = root


    def __str__(self):
        return f"NameNormalizer - {self.root}"


    def strip_artist_album_name_from_songname(self) -> None:
        """ Strip out artist name and album name if they are a part of name of a song name. Special case are albums with one track only since the track is usualy called with the same name as the album so in the case on one-track album, the name of the track will be 01 - <name of the album>.mp3
         """
        for artist_folder in os.listdir(self.root):
            if not os.path.isdir(os.path.join(self.root, artist_folder)):
                continue
            for album_folder in os.listdir(os.path.join(self.root, artist_folder)):
                tracklist = [track for track in os.listdir(os.path.join(self.root, artist_folder, album_folder)) if track.endswith(tuple(self.ext))]
               
                # if i have a one-track album, rename it as 01 <name of the album>.mp3
                if len(tracklist) == 1:
                    print(f"Album {album_folder} contains only one track ==> normalizing it..")
                    for file in os.listdir(os.path.join(self.root, artist_folder, album_folder)):
                        if file.endswith(tuple(self.ext)):
                            _, extension = os.path.splitext(os.path.join(self.root, artist_folder, album_folder, file))
                            filename = f"01 {album_folder}"
                            src_file = file
                            dst_file = filename + extension
                            print(f"Renaming {os.path.join(artist_folder, album_folder, src_file)} to {os.path.join(artist_folder, album_folder, dst_file)}")
                            os.rename(os.path.join(self.root, artist_folder, album_folder, src_file), os.path.join(self.root, artist_folder, album_folder, dst_file))
               
                # if i have album where all the songs have artist name in its name, remove this artist name from it
                if len(tracklist) > 1 and all(artist_folder in song for song in tracklist):
                    print(f"Album {album_folder} contains artist name '{artist_folder}' as part of all audio tracks => stripping it out..")
                    for file in os.listdir(os.path.join(self.root, artist_folder, album_folder)):
                        if file.endswith(tuple(self.ext)):
                            src_file = file
                            dst_file = file.replace(artist_folder, "", 1)
                            print(f"Renaming {os.path.join(artist_folder, album_folder, src_file)} to {os.path.join(artist_folder, album_folder, dst_file)}")
                            os.rename(os.path.join(self.root, artist_folder, album_folder, src_file), os.path.join(self.root, artist_folder, album_folder, dst_file))

                # if i have album where all the songs have album name in its name, remove this album name from it
                if len(tracklist) > 1 and all(album_folder in song for song in tracklist):
                    print(f"Album {album_folder} contains album name '{album_folder}' as part of all audio tracks => stripping it out..")
                    for file in os.listdir(os.path.join(self.root, artist_folder, album_folder)):
                        if file.endswith(tuple(self.ext)):
                            src_file = file
                            dst_file = file.replace(album_folder, "", 1)
                            print(f"Renaming {os.path.join(artist_folder, album_folder, src_file)} to {os.path.join(artist_folder, album_folder, dst_file)}")
                            os.rename(os.path.join(self.root, artist_folder, album_folder, src_file), os.path.join(self.root, artist_folder, album_folder, dst_file))


    def strip_year_from_songname(self) -> None:
        """ deletes (year) and Cd and _- from song name """
        yr_parens = re.compile(r"[(]\d\d\d\d[)]")
        cd = re.compile(r"Cd\s?\d\d?")
        for path, dirs, folders in os.walk(self.root):
            for file in folders:
                if file.endswith(tuple(self.ext)):
                    if re.search(yr_parens, file) or re.search(cd, file) or "-" in file or "_" in file or "[" in file or "]" in file:
                        new_file_name = re.sub(yr_parens, "", file).strip()
                        new_file_name = re.sub(cd, "", new_file_name).strip()
                        new_file_name = new_file_name.replace("-", " ").replace("_", " ").strip()
                        new_file_name = new_file_name.replace("[", "").replace("]", "").strip()
                        src_file = os.path.join(path, file)
                        dst_file = os.path.join(path, new_file_name)
                        os.rename(src_file, dst_file)


    def strip_dash_from_artist_album_song(self) -> None:
        """ Deletes '-' from title, album, song names. This is used for Bandcamp name normalization. """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                for file in os.listdir(os.path.join(self.root, artist, album)):
                    if file.endswith(tuple(self.ext)) and "-" in file:
                        src_file = os.path.join(self.root, artist, album, file)
                        dst_file = os.path.join(self.root, artist, album, file.replace("-", " "))
                        print(f"Stripping - from song {src_file}")
                        os.rename(src_file, dst_file)
                if "-" in album:
                    src_album = os.path.join(self.root, artist, album)
                    dst_album = os.path.join(self.root, artist, album.replace("-", " "))
                    print(f"Stripping - from album {src_album}")
                    os.rename(src_album, dst_album)
            if "-" in artist:
                src_artist = os.path.join(self.root, artist)
                dst_artist = os.path.join(self.root, artist.replace("-", " "))
                print(f"Stripping - from artist {src_artist}")
                os.rename(src_artist, dst_artist)


    def strip_dash_underscores_from_songname(self) -> None:
        """ deletes _ and - from all song names """
        for path, dirs, folders in os.walk(self.root):
            for file in folders:
                if file.endswith(tuple(self.ext)) and ("-" in file or "_" in file):
                    new_file_name = file.replace("-", " ").replace("_", " ")
                    src_name = os.path.join(path, file)
                    dst_name = os.path.join(path, new_file_name)
                    print(f"Striping -_ from song name {src_name} -> {dst_name}")
                    os.rename(src_name, dst_name)


    def strip_whitespaces_from_songname(self) -> None:
        """ delete multiple spaces in song names, ale trailing space at the end as well """
        for path, dirs, files in os.walk(self.root):
            for file in files:
                if "  " in file or file[0] == " ":
                    src_file = os.path.join(path, file)
                    file = re.sub(r"[\s]+", " ", file).strip()
                    dst_file = os.path.join(path, file)
                    print(f"Stripping whitespace from {src_file} --> {dst_file}")
                    os.rename(src_file, dst_file)
                path_file_without_ext, ext = os.path.splitext(os.path.join(path, file))
                if path_file_without_ext[-1] == " ":
                    new_file_name = path_file_without_ext.strip()+ext
                    src_file = os.path.join(path, file)
                    dst_file = os.path.join(path, new_file_name)
                    print(f"Stripping whitespace as last char {src_file} --> {dst_file}")
                    os.rename(src_file, dst_file)


    def strip_dot_after_track_from_songname(self) -> None:
        """ some songs have this format: 01. songname.mp3, or 1. songname, strip the . """
        for path, dirs, files in os.walk(self.root):
            for file in files:
                file_name, ext = os.path.splitext(os.path.join(path, file))
                basename = os.path.basename(file_name)
                try:
                    if os.path.basename(file_name)[2] == "." or os.path.basename(file_name)[1] == ".":
                        src_file = os.path.join(path, file)
                        dst_file = os.path.join(path, file_name.replace(".","", 1)+ext)
                        print(f"Stripping dot from {file}")
                        os.rename(src_file, dst_file)
                except IndexError as e:
                    print(f"{e}, {os.path.join(path, file)} does not have song name")


    def strip_parens_around_track_from_songname(self) -> None:
        """ some songs have this format: (02) Secret Light At The Upper Window, strip the () """
        for path, dirs, folders in os.walk(self.root):
            for file in folders:
                if file.endswith(tuple(self.ext)):
                    if file[0] == "(" and file[3] == ")":
                        src_name = os.path.join(path, file)
                        dst_name = os.path.join(path, file.replace("(","", 1).replace(")","", 1))
                        print(f"Stripping parens arount songname {file}")
                        os.rename(src_name, dst_name)

    #NOT READY
    def strip_whatever_from_name(self, s:set, substrings:list) -> None:
        """ used for manual clearing for songs or albums that had no regex match - takes a list os strings that should be stripped out """
        for path in s:
            head, tail = os.path.split(path)
            for substring in substrings:
                if substring in tail:
                    new_tail = tail.replace(substring, "").strip()
                    dst = os.path.join(head, new_tail)
                    try:
                        os.rename(path, dst)
                    except Exception as e:
                        print(e)

    # # NOT INCLUDED
    # def split_tracknumber_from_name_in_songname(self, s:set) -> None:
    #     """ some song have this format 10songname.mp3, this will meke it 10 songname.mp3 """
    #     for song in s:
    #         head, tail = os.path.split(song)
    #         if tail[:2].isdigit() and (isinstance(tail[2:], str) and tail[2] != " "):
    #             new_tail = tail[:2] + " " + tail[2:]
    #             src = song
    #             dst = os.path.join(head, new_tail)
    #             print(f"Spliting tracknumber from name {tail} -> {new_tail}")
    #             os.rename(src, dst)

    # # NOT INCLUDED
    # def strip_year_from_albumname(self) -> None:
    #     """ deletes year from album name """
    #     for artist in os.listdir(self.root):
    #         for album in os.listdir(os.path.join(self.root, artiself.p2_album.match(album) or self.p3_album.match(album):
    #                 p2_match = self.p2_album.match(album)
    #                 p3_match = self.p3_album.match(album)
    #                 try:
    #                     album_title = p2_match.group(3)
    #                 except AttributeError:
    #                     pass
    #                 try:
    #                     album_title = p3_match.group(1)
    #                 except AttributeError:
    #                     pass
    #
    #                 src_name = os.path.join(self.root, artist, album)
    #                 dst_name = os.path.join(self.root, artist, album_title)
    #                 print(f"Renaming album, stripping year {album} -> {album_title}")
    #                 if not os.path.exists(dst_name):
    #                     os.rename(src_name, dst_name)
    #                 else:
    #                     print(f"Ablbum {dst_name} already exists, removing duplicates")
    #                     shutil.rmtree(src_name)


    def strip_apimatch_from_albumname(self) -> None:
        """ strip [api match 131243] from album folder """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                if "api match" in album:
                    album_name = album.rsplit(' [api')[0]
                    src_name = os.path.join(self.root, artist, album)
                    dst_name = os.path.join(self.root, artist, album_name)
                    print(f"reaming {src_name} to {dst_name}")
                    os.rename(src_name, dst_name)


    def lowercase_artist(self) -> None:
        """ make artist folder lowercase """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            if artist != artist.lower():
                src_name = os.path.join(self.root, artist)
                dst_name = os.path.join(self.root, artist.lower())
                print(f"Lowercasing artist {src_name} to {dst_name}")
                os.rename(src_name, dst_name)


    def titlecase_artist(self) -> None:
        """ make artist folder titlecase """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            if artist != artist.title():
                src_name = os.path.join(self.root, artist)
                dst_name = os.path.join(self.root, artist.title())
                print(f"Titlecasing artist {src_name} to {dst_name}")
                os.rename(src_name, dst_name)


    def lowercase_album(self) -> None:
        """ make album folder lowercase """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                if album != album.lower():
                    src_name = os.path.join(self.root, artist, album)
                    dst_name = os.path.join(self.root, artist, album.lower())
                    print(f"Lowercasing album {src_name} to {dst_name}")
                    os.rename(src_name, dst_name)


    def titlecase_album(self) -> None:
        """ make album folder lowercase """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                if album != album.title():
                    src_name = os.path.join(self.root, artist, album)
                    dst_name = os.path.join(self.root, artist, album.title())
                    print(f"Titlecasing album {src_name} to {dst_name}")
                    os.rename(src_name, dst_name)


    def lowercase_song(self) -> None:
        """ make song name lowercase """
        for artist in os.listdir(self.root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                for song in os.listdir(os.path.join(self.root, artist, album)):
                    if song != song.lower():
                        src_name = os.path.join(self.root, artist, album, song)
                        dst_name = os.path.join(self.root, artist, album, song.lower())
                        print(f"Lowercasing {os.path.join(artist, album, song)} ==> {os.path.join(artist, album, song.lower())}")
                        os.rename(src_name, dst_name)


    def titlecase_song(self) -> None:
        """ make song name titlecased """
        for artist in os.listdir(self.root):
            # this is just because i run this script from the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                for song in os.listdir(os.path.join(self.root, artist, album)):
                    song_name, ext = os.path.splitext(os.path.join(self.root, artist, album, song))
                    if song != os.path.basename(song_name.title()+ext):
                        src_name = os.path.join(self.root, artist, album, song)
                        dst_name = os.path.join(self.root, artist, album, song_name.title()+ext)
                        print(f"Titlecasing {os.path.join(artist, album, song)} ==> {os.path.join(artist, album, os.path.basename(song_name.title()+ext))}")
                        os.rename(src_name, dst_name)


    def titlecase_all(self) -> None:
        """ title all names of songs, artists, albums """
        NameNormalizer.titlecase_song(self)
        NameNormalizer.titlecase_album(self)
        NameNormalizer.titlecase_artist(self)

    def lowercase_all(self) -> None:
        """ lowercase all names of songs, artists, albums """
        NameNormalizer.lowercase_song(self)
        NameNormalizer.lowercase_album(self)
        NameNormalizer.lowercase_artist(self)


    def sort_audiofolders(self, root, target) -> None:
        """ Move audio folders into correct path in alphabetical structure. Used for moving properly named files to completed folder. """
        
        print(self.root)
        for artist in os.listdir(self.root):  
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            os.chdir(self.root)
            artist_path = os.path.abspath(artist)
            os.chdir(artist_path)
            for album in os.listdir(artist_path):
                if os.path.isdir(os.path.abspath(album)):
                    album_path = os.path.abspath(album)
                    dir_path = os.path.dirname(album_path)
                    target_dir = os.path.join(target, artist[0].lower(), artist, album)
                    if os.path.exists(target_dir):
                        print(f"album '{album}' on path '{album_path}' is existing on target path, skipping..")
                        continue
                    else:
                        print(f"album '{album}' on path '{album_path}' is not existing on target path '{target_dir}', moving now.. ")
                        shutil.move(album_path, target_dir)

    # def __call__(self, root):
    #     """ Calls the functions in appropriate order. It can be called either on the clas itself NameNormalizer(path) or on an object """
    #     NameNormalizer.strip_apimatch_from_albumname(root)
    #     NameNormalizer.strip_year_from_albumname(root)
    #     NameNormalizer.titlecase_all(root)
    #     NameNormalizer.strip_year_from_songname(root)
    #     NameNormalizer.strip_artist_album_name_from_songname(root)
    #     NameNormalizer.strip_whitespaces_from_songname(root)
    #     NameNormalizer.strip_dot_after_track_from_songname(root)
    #     NameNormalizer.strip_parens_around_track_from_songname(root)
    #     NameNormalizer.strip_whitespaces_from_songname(root)

class RegexMatcher(DataProvider):
    """ Class for checking regex matches for songs and albums. It holds paths of all matched and unmatched files or folders in separated sets for further processing. """

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
                    if file.endswith(tuple(self.ext)):
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
                    if file.endswith(tuple(self.ext)):
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


class BroadcastFileNormalizer(DataProvider):
    """ Class for handling files used in broadcasting server. It normalizes names, bitrate and volume of songs and moves them to proper folders. Empty folders are deleted afterwards. """

    def __init__(self, root:str):
        self._root = root
        self.renamed = set()
        self.not_renamed = set()
        self.not_matched = set()

    def __repr__(self):
        return f"BroadcastFileNormalizer('{self.root}')"

    @property
    def root(self):
        return self._root

    def normalize_names(self, dst_taildir) -> None:
        """ Renames songs for radio server, following this pattern: 01 Name Of Artist -- Name Of Album -- Name Of Song.mp3
        The names for artist, album, song should be first cleared, since the final name is parsed from the filesystem names.
        All files are moved to the particular folder - '2] to be bitnormed' is default
        """

        basedir, taildir = os.path.split(self.root) # tail will be swapped to '2] to be bitnormed'
        # dst_taildir = '2] to be bitnormed' # hardcoced since i dont assume i will change it

        for artist in os.listdir(self.root):
             # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(self.root, artist)):
                continue
            for album in os.listdir(os.path.join(self.root, artist)):
                try:
                    for song in os.listdir(os.path.join(self.root, artist, album)):
                        src = os.path.join(self.root, artist, album, song)
                        if song.endswith(tuple(self.ext)):
                            if(BroadcastFileNormalizer.p1_song.match(song) or BroadcastFileNormalizer.p2_song.match(song) \
                                or BroadcastFileNormalizer.p3_song.match(song) or BroadcastFileNormalizer.p4_song.match(song)):
                                p1_match = BroadcastFileNormalizer.p1_song.match(song)
                                p2_match = BroadcastFileNormalizer.p2_song.match(song)
                                p3_match = BroadcastFileNormalizer.p3_song.match(song)
                                p4_match = BroadcastFileNormalizer.p4_song.match(song)
                                try:
                                    tracknumber, _, title = p1_match.groups()
                                except AttributeError:
                                    pass
                                try:
                                    tracknumber, _, title = p2_match.groups()
                                except AttributeError:
                                    pass
                                try:
                                    tracknumber, _, title = p3_match.groups()
                                except AttributeError:
                                    pass
                                try:
                                    tracknumber, _, title = p4_match.groups()
                                except AttributeError:
                                    pass
                                new_title = "".join([tracknumber, " ", artist, " -- ", album, " -- ", title])
                                dst = os.path.join(basedir, dst_taildir, artist, album, new_title)
                                dst_dir, dst_file = os.path.split(dst)
                                if not os.path.exists(dst_dir):
                                    os.makedirs(dst_dir)
                                if not os.path.exists(dst):
                                    print(f"Renaming for broadcast and moving from {src} to {dst}")
                                    shutil.move(src, dst)
                                elif os.path.exists(dst):
                                    print(f"File on path {dst} already exists, removing duplicates")
                                    os.remove(src)
                                self.renamed.add(dst)
                            else:
                                print(f"File on path {src} does not match any pattern --> not renamed (and moved to set)")
                                self.not_renamed.add(src)
                except Exception as e:
                    print(e, os.path.join(self.root, artist, album))


    # def check_names_integrity(self, dir_) -> None:
    #     """ Check if all song name match the broadcast pattern before u move them to the server """
    #     ext = get_all_audio_extensions()
    #     for path, dirs, folders in os.walk(dir_):
    #         for file in folders:
    #             if file.endswith(tuple(self.ext)):
    #                 filename, ext = os.path.splitext(os.path.join(path, file))
    #                 if self.p_broadcast.match(os.path.basename(filename)):
    #                     continue
    #                 else:
    #                     self.not_matched.add(filename)
    #                     print(filename, "-> not matched")


    def check_bitrate(self, min_bitrate=b'128000') -> None:
        """ Make a map of files having less bitrate than specified """
        command = "ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1"
        d = {}
        for path, dirs, files in os.walk(self.root):
            for file in files:
                if file.endswith(tuple(self.ext)):
                    file_name = os.path.join(path, file)
                    full_command = "".join(command + f' "{file_name}"')
                    out = subprocess.check_output(full_command)
                    if out < min_bitrate:
                        d[file_name] = out

        return(d)


    def count_audiofiles(self, path:str) -> int:
        """ Count audiofiles in a directory, serves as a helper to deleting """
        counter = 0
        for item in os.listdir(path):
            if any(ex in item for ex in self.ext):
                counter += 1
            elif item.endswith(".py"):
                counter +=1
            else:
                continue
        return counter


    def delete_folders_without_audio(self) -> None:
        """ Delete folders where no audio files are left """
        counter = 0
        for path, dirs, _ in os.walk(self.root):
            if len(dirs) == 0 and self.count_audiofiles(path) == 0:
                counter += 1
                print(f"deleting.. {path}")
                shutil.rmtree(path)
        if counter > 0:
            return self.delete_folders_without_audio()
        else:
            return None

# TODO variables.. bitrate and paths
def change_bitrate(source_dir=os.getcwd()) -> None:
    """Change bitrate to 128k value"""
    codec = " [lame]"
    path_replacement = "3] to be transfered"
    head, tail = os.path.split(source_dir)

    for path, dirs, files in os.walk(source_dir):
        for file in files:
            filepath_source = os.path.abspath(os.path.join(path, file))
            index = filepath_source.rfind(".") #DEBUG
            filepath_norm = filepath_source[:index] + codec + filepath_source[index:] #DEBUG
            filepath_target = filepath_norm.replace(tail, path_replacement)
            print(filepath_target)
            dirpath_target = os.path.dirname(filepath_target)
            # make it work for flac, alac and other extensions..
            if not file.endswith(".mp3"):
                filename, extension = os.path.splitext(filepath_target)
                filepath_target = filename + ".mp3"
            # check the existence to avoid overwiting
            if os.path.exists(filepath_target): 
                print(f"file {filepath_target} already exists, skipping..")
                continue
            # check the existence to avoid eror
            if not os.path.exists(dirpath_target): 
                os.makedirs(dirpath_target)
            print(f"encoding from {filepath_source} to {filepath_target}")
            subprocess.run(f'ffmpeg -i "{filepath_source}" -metadata comment="ripped with lame @128k" -codec:a libmp3lame -b:a 128k -ar 44100 "{filepath_target}"')



def main():
    """ Run the script as command line interface """
    parser = argparse.ArgumentParser(description="Renames the audio files and folder in specified root directory.")

    # general swithces
    parser.add_argument("-src", "--sourcepath", help="specify the root directory path", default=os.getcwd())
    parser.add_argument("-dst", "--destinationpath", help="specify where the files should be moved", default=r'Z:\Music\!!! completed, tagged !!!')
    parser.add_argument("-q", "--quite", action="store_true")

    # titlecase/lowercase switches  #TODO add  mutualexclusive group
    parser.add_argument("-ta", "--titleall", help="titlecases song, album, artist names", action="store_true")
    parser.add_argument("-ts", "--titlesong", help="titlecases song names", action="store_true")
    parser.add_argument("-tal", "--titlealbum", help="titlecases album names", action="store_true")
    parser.add_argument("-tar", "--titleartist", help="titlecases artist names", action="store_true")
    parser.add_argument("-la", "--lowerall", help="lowercase song, album, artist names", action="store_true")
    parser.add_argument("-ls", "--lowersong", help="lowercase song names", action="store_true")
    parser.add_argument("-lal", "--loweralbum", help="lowercase album names", action="store_true")
    parser.add_argument("-lar", "--lowerartist", help="lowercases artist names", action="store_true")

    # stripping switches
    parser.add_argument("-sta", "--stripartistalbum", help="strip out artist name and album name if they are a part of name of a song name", action="store_true")
    parser.add_argument("-sty", "--stripyear", help="strips out (year) and Cd and _- from song name", action="store_true") # TODO rozdelit year and CD??
    parser.add_argument("-std", "--stripdashes", help="strips out dashes from title, album, song names, primary used for Bandcamp name normalization", action="store_true")
    parser.add_argument("-stu", "--stripunderscores", help="strip out underscores from song names", action="store_true") # TODO udelat to pro autora i album
    parser.add_argument("-stw", "--stripwhitespace", help="delete multiple spaces in song names, ale trailing space at the end as well", action="store_true")
    parser.add_argument("-stt", "--stripdot", help="some songs have this format: 01. songname.mp3, this flag strips the .", action="store_true")
    parser.add_argument("-stp", "--stripparens", help="some songs have this format: (02) songname, this flag strips the ()", action="store_true")
    parser.add_argument("-ste", "--stripelse", help="this flag strips whatever else is specified in additional params [used for manual clearing mostly]") # TODO... variable list of chars.. 

    # splitting switches
    #TODO

    # moving to proper folder in main filesystem
    parser.add_argument("-sort", "--sortfolders", help="moves audiofile folder to proper place based on artist/album name", action="store_true")

    # printing/checking switches
    parser.add_argument("-sams", "--allsongs", help="shows all song that were matched with some regex", action="store_true")
    parser.add_argument("-sama", "--allalbums", help="shows all albums that were matched with some regex", action="store_true")
    parser.add_argument("-snms", "--nosongs", help="shows all songs that were NOT matched with any regex", action="store_true")
    parser.add_argument("-snma", "--noalbums", help="shows all albums that were NOT matched with any regex", action="store_true")
    parser.add_argument("-cb", "--checkbitrate", help="show files that have bitrate less then specified", action="store_true") # TODO... vriable bitrate

    # switch to process normalization naming, moving and deleting for broadcasting
    parser.add_argument("-nn", "--normalizenames", help="renames the files (. -- . -- .) and moves them to another folder, destination folder can be specified using -d flag", action="store_true")
    parser.add_argument("-d", "--destinationdir", help="destination directory for renamed files", default="2] to be bitnormed")
    parser.add_argument("-de", "--deleteempty", help="deletes folders containing no audio files", action="store_true")
    parser.add_argument("-nb", "--bitnorm", help="normalize bitrate to 128k", action="store_true") #TODO add variable bitrates...

    args = parser.parse_args()

    # get the global args
    src = args.sourcepath
    dst = args.destinationpath
    quite = args.quite

    # dir where to move normalized names for brodcast
    dst_taildir = args.destinationdir

    # initialize the classes
    name_normalizer = NameNormalizer(src)
    rgx_matcher = RegexMatcher(src)
    brdcast_normalizer = BroadcastFileNormalizer(src)

    # name normalization options
    if args.titleall: name_normalizer.titlecase_all()
    if args.titlesong: name_normalizer.titlecase_song()
    if args.titlealbum: name_normalizer.titlecase_album()
    if args.titleartist: name_normalizer.titlecase_artist()
    if args.lowerall: name_normalizer.lowercase_all()
    if args.lowersong: name_normalizer.lowercase_song()
    if args.loweralbum: name_normalizer.lowercase_album()
    if args.lowerartist: name_normalizer.lowercase_artist()
    if args.stripartistalbum: name_normalizer.strip_artist_album_name_from_songname()
    if args.stripyear: name_normalizer.strip_year_from_songname()
    if args.stripdashes: name_normalizer.strip_dash_from_artist_album_song()
    if args.stripparens: name_normalizer.strip_parens_around_track_from_songname()
    if args.stripunderscores: name_normalizer.strip_dash_underscores_from_songname()
    if args.stripwhitespace: name_normalizer.strip_whitespaces_from_songname()
    if args.stripelse: name_normalizer.strip_whatever_from_name()
    if args.stripdot: name_normalizer.strip_dot_after_track_from_songname()
    if args.sortfolders: name_normalizer.sort_audiofolders(root=src, target=dst)

    # displaying options
    if args.allsongs: rgx_matcher.get_all_regex_song_match()
    if args.allalbums: rgx_matcher.get_all_regex_album_match()
    if args.nosongs: rgx_matcher.get_no_regex_song_match()
    if args.noalbums: rgx_matcher.get_no_regex_album_match()
    if args.checkbitrate: brdcast_normalizer.check_bitrate()

    # broadcaster options
    if args.normalizenames: brdcast_normalizer.normalize_names(dst_taildir=dst_taildir)
    if args.checkbitrate: print(brdcast_normalizer.check_bitrate())
    if args.deleteempty: brdcast_normalizer.delete_folders_without_audio()
    if args.bitnorm: change_bitrate()




if __name__ == "__main__":
    main()
    
