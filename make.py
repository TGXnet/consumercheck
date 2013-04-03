#!/usr/bin/python

# os.system() or os.popen()
# os.execv(), os.system() and os.startfile()
# shutil.move()
# subprocess module

# FIXME: optparse replaced by argparse from python v2.7
import os
from optparse import OptionParser
from subprocess import Popen

def make_clean():
    print("Hello clean")

def make_doc():
    print("Hello doc")
    home = os.getcwd()
    os.chdir(os.path.join(home, "docs-user"))
    print(os.getcwd())
    tg = Popen(["make", "html"])

def make_tags():
    print("Generate TAGS")
    tg = Popen(["ctags", "-e", "--recurse", "-f", "TAGS"])

def make_pack():
    print("Hello pack")

def make_fixme():
    print("Hello fixme")
    tg = Popen(["grep", "--recursive", "--line-number",  "--after-context=2",  "--fixed-strings", "FIXME", "src"])

def main():
    usage = "usage: %prog [target]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean", default=False,
                      help="Make clean (remove .pyc)")
    parser.add_option("-d", "--doc",
                      action="store_true", dest="doc", default=False,
                      help="Make documentation")
    parser.add_option("-t", "--tags",
                      action="store_true", dest="tags", default=False,
                      help="Generate TAGS")
    parser.add_option("-p", "--pack",
                      action="store_true", dest="pack", default=False,
                      help="Make windows package")
    parser.add_option("-f", "--fixme",
                      action="store_true", dest="fixme", default=False,
                      help="Filter FIXME tags")

    (options, args) = parser.parse_args()

    if options.clean:
        make_clean()
    if options.doc:
        make_doc()
    if options.tags:
        make_tags()
    if options.pack:
        make_pack()
    if options.fixme:
        make_fixme()



if __name__ == "__main__":
    main()
