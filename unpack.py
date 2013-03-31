# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.


import argparse, os, re, subprocess
from label_episodes import extension


#def unpack(directory, target):
def unpack(directory):
    for root, dirs, files in os.walk('python/Lib/email'):
        for f in files:
            if extension(f).lower() == ".rar":
                rar = os.path.join(root, f)
                print "Unpacking {}...".format(rar),
                code = subprocess.call("unrar", "e", rar)
                if code != 0:
                    print " Error!"
                else:
                    print " Done."
                    #print "Moving {} to {}."


if __name__ == "__main__":
    description = "Unpacks all RAR archives in the specified directory and "  \
                  "subdirectories."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--dir", help="The directory containing the RAR "
                        "files to unpack. Defaults to present working "
                        "directory.", default="./")
#    parser.add_argument("-t", "--target", help="The directory to which to "
#                        "move the unpacked files. Defaults to the source "
#                        "directory.", default=None)
    args = parser.parse_args()

#    label_episodes(args.dir, args.target if args.target else args.dir)
    label_episodes(args.dir)