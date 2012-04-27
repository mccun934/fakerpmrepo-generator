#!/usr/bin/python

import sys
import optparse
import random
import os
from optparse import OptionParser

if __name__ == '__main__':
 
    parser = OptionParser("usage: %prog [options]")
    parser.add_option('--numpackages',  dest='numpackages',  type="int", default=5)
    (options, args) = parser.parse_args(sys.argv[1:])

    os.system("rm -rf /var/tmp/generated-repo")
    os.system("mkdir /var/tmp/generated-repo")

    file = open('/usr/share/dict/words')
    lines = file.readlines()
    version_numbers = range(10)
    packages = options.numpackages
    for i in range(packages):
        name = random.choice(lines).rstrip()
        version = "%s.%s.%s" % (str(random.randint(0,10)),
                              str(random.randint(0,10)),
                              str(random.randint(0,10)))
        size = str(random.randint(0,1000))
        # print "./generate-package.bash %s %s %s" % (name, version, size)
        os.system("./generate-package.bash %s %s %s" % (name, version, size))

    os.system("mv ~/rpmbuild/RPMS/noarch/*elfake* /var/tmp/generated-repo")
    os.system("createrepo /var/tmp/generated-repo")
    print "\n\n\n"
    print "==========================================================="
    print "Your new fake repo is available at: /var/tmp/generated-repo\n"
    
    
