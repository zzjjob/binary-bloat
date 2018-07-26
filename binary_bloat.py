#!/usr/bin/python

import os
import sys
import optparse
import hashlib

prefix = sys.path[0]
if not os.path.exists(prefix + "/.tmp/"):
	 os.mkdir(prefix + "/.tmp/")

nm = "nm"
objdump = "objdump"
inputfile = ""
openfile = "index.html"
md5_file = ".tmp/inputfile.md5"
nm_out = ".tmp/nm.out"
objdump_out = ".tmp/objdump.out"

# ===========
usage="""%prog MODE /path/to/binary.so

Modes are:
  syms: output symbols json suitable for a webtreemap
  dump: print symbols sorted by size (pipe to head for best output)
  sections: output binary sections json suitable for a webtreemap"""

parser = optparse.OptionParser(usage=usage)
parser.add_option('-f', '--force', action='store_true', dest='force',
                  help='Force generator output [default=False]')

opts, args = parser.parse_args()

if len(args) != 2 or (args[0] not in ["syms", "dump", "sections"]):
    parser.print_usage()
    sys.exit(1)

mode = args[0]
inputfile = os.path.abspath(args[1])

if not os.path.isfile("%s"%(inputfile)):
    print("%s NOT FOUND!"%(inputfile))
    sys.exit(1)

# file inputfile
arch = os.popen("file %s"%(inputfile)).read()
if arch.find("ARM"):
	nm = "arm-linux-androideabi-nm"
	objdump = "arm-linux-androideabi-objdump"

os.chdir(prefix)

# use cache
inputfile_modify = True
print(">> Verify md5")
md5_new = hashlib.md5(open(inputfile).read()).hexdigest()

if (os.path.isfile(md5_file)):
    md5_before = open(md5_file).read()
    inputfile_modify = (md5_new != md5_before)

open(md5_file, "w").write(md5_new)

# nm -C -S -l /path/to/binary > nm.out
if mode == "syms":
    if opts.force or (not os.path.isfile(nm_out) or inputfile_modify):
        print(">> Wait generator %s"%(nm_out))
        os.system("%s -C -S -l %s > %s"%(nm, inputfile, nm_out))
    else:
        print(">> Use cached %s"%(nm_out))
# objdump -h /path/to/binary > objdump.out
elif mode == "sections":
    if opts.force or (not os.path.isfile(objdump_out) or inputfile_modify):
        print(">> Wait generator %s"%(objdump_out))
        os.system("%s -h %s > %s"%(objdump, inputfile, objdump_out))
    else:
        print(">> Use cached %s"%(objdump_out))
elif mode == "dump":
    if opts.force or (not os.path.isfile(nm_out) or inputfile_modify):
        print(">> Wait generator %s"%(nm_out))
        os.system("%s -C -S -l %s > %s"%(nm, inputfile, nm_out))
    else:
        print(">> Use cached %s"%(nm_out))
	openfile = ".tmp/bloat.json"

# bloat.py --strip-prefix=./ syms > bloat.json
print(">> Wait generator %s"%(openfile))
os.system("./bloat.py \
	--nm-output=%s \
	--objdump-output=%s \
	--strip-prefix=./.tmp/ %s > ./.tmp/bloat.json"%(nm_out, objdump_out, mode))

# open file
os.system("open ./%s"%(openfile))

