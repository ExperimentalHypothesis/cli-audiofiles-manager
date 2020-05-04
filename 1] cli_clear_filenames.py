""" Script for clearing name of songs, albums and artist """

import os, re, argparse

def clear_filenames(root:str) -> None:
        """ Deletes '- _' from title, album, song names and makes all names Titlecased. This is used primarily for audio folders from Bandcamp """

        ext = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.alac', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.nmf', '.nsf', '.ogg', '.oga', '.mogg', '.opus', '.ra', '.rm', '.raw', '.sln', '.tta', '.voc', '.vox', '.wav', '.wma', '.wv', '.webm', '.8svx']

        yr_rgx = re.compile(r"\d\d\d\d")

        for artist in os.listdir(root):
            # this is just because i run this script fromt the root folder for simplicity sake
            if not os.path.isdir(os.path.join(root, artist)):
                continue

            for album in os.listdir(os.path.join(root, artist)):

                # make all songnames titlecased and replace - _ if they are present
                for file in os.listdir(os.path.join(root, artist, album)):
                    song_name, ext = os.path.splitext(os.path.join(root, artist, album, file))
                    if file != os.path.basename(song_name.title()+ext):
                        src_name = os.path.join(root, artist, album, file)
                        dst_name = os.path.join(root, artist, album, song_name.title()+ext)
                        os.rename(src_name, dst_name)
                    if file.endswith(tuple(ext)) and any(char in file for char in ["-","_"]):
                        src_file = os.path.join(root, artist, album, file)
                        dst_file = os.path.join(root, artist, album, file.replace("-", " ").replace("_", " "))
                        print(f"Stripping dashes/underscores {src_file}")
                        os.rename(src_file, dst_file)

                # strip year from filename if present
                for file in os.listdir(os.path.join(root, artist, album)):
                    if re.search(yr_rgx, file):
                        new_name = re.sub(yr_rgx, "", file)
                        src_name = os.path.join(root, artist, album, file)
                        dst_name = os.path.join(root, artist, album, new_name)
                        print(f"Stripping year from {src_name}")
                        os.rename(src_name, dst_name)

                # make all albumnames titlecased and replace - _ if they are present
                src_album = os.path.join(root, artist, album)
                album = album.title()
                dst_album = os.path.join(root, artist, album)
                os.rename(src_album, dst_album)
                if any(char in album for char in ["-", "_"]):
                    src_album = os.path.join(root, artist, album)
                    dst_album = os.path.join(root, artist, album.replace("-", " ").replace("_"," "))
                    print(f"Stripping dashes/underscores from {src_album}")
                    os.rename(src_album, dst_album)

            # make all artistname titlecased and replace - _ if they are present
            src_artist = os.path.join(root, artist)
            artist = artist.title()
            dst_artist = os.path.join(root, artist)
            os.rename(src_artist, dst_artist)
            if any(char in artist for char in ["-", "_"]):
                src_artist = os.path.join(root, artist)
                dst_artist = os.path.join(root, artist.replace("-", " ").replace("_", " "))
                print(f"Stripping dashes/underscores from {src_artist}")
                os.rename(src_artist, dst_artist)


def main():
    """ Run the script as command line interface """
    parser = argparse.ArgumentParser(description="Renames the audio files and folder in specified root directory.")
    parser.add_argument("-p", "--path", help="specify the root directory path", type=str, default=os.getcwd())
    args = parser.parse_args()
    path = args.path
    
    clear_filenames(path)


if __name__ == "__main__":
    main()
