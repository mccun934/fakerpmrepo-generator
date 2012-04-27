#!/usr/bin/python

import subprocess
import sys
import optparse
import random
import os
from optparse import OptionParser

def shell_exec(command):
    print "Executing: $ %s" % command
    process = subprocess.Popen(command, stderr = subprocess.PIPE, stdout = subprocess.PIPE, shell = True)
    output = process.communicate()
    stdout = output[0]
    stderr = output[1]
    if process.returncode != 0:
        print "STDOUT: %s" % stdout
        print "STDERROR: %s" % stderr
        exit(process.returncode)
    


if __name__ == '__main__':
 
    parser = OptionParser("Generate a yum repository with fake packages and errata\n\n%prog [options]")
    parser.add_option('--maxpackagesize',  dest='maxpackagesize', 
                      help='maximum size in KB for created packages', type="int", default=100)
    parser.add_option('--numpackages',  dest='numpackages',  type="int", default=5)
    parser.add_option('--multiversion',  dest='multiversion',  
                        help="generate 0-3 random new versions of each package and errata",
                        action="store_true", default=False)
    parser.add_option('--outputdir',  dest='outputdir', type="str", default='/var/tmp/generated-repo')
    (options, args) = parser.parse_args(sys.argv[1:])

    outputdir = options.outputdir
    os.system("rm -rf %s" % outputdir)
    os.system("mkdir %s" % outputdir)

    file = open('/usr/share/dict/words')
    lines = file.readlines()
    version_numbers = range(10)
    packages = options.numpackages
    all_errata = ""
    for i in range(packages):
        name = random.choice(lines).rstrip()
        first_rev = random.randint(0,10)
        middle_rev = random.randint(0,10)
        last_rev = random.randint(0,10)
        version = "%s.%s.%s" % (str(first_rev),
                              str(middle_rev),
                              str(last_rev))
        size = str(random.randint(0,options.maxpackagesize))
        # print "./generate-package.bash %s %s %s" % (name, version, size)
        shell_exec("./generate-package.bash %s %s %s" % (name, version, size))
        if (options.multiversion):
            
            et = open('./errata-template.xml')
            errata_template = et.read()
            # Generate 0-3 newer versions of the package
            for j in range(random.randint(0,3)):
                last_rev = last_rev + 1
                version = "%s.%s.%s" % (str(first_rev),
                                      str(middle_rev),
                                      str(last_rev))
                #print "    ./generate-package.bash %s %s %s" % (name, version, size)
                shell_exec("./generate-package.bash %s %s %s" % (name, version, size))
                # Generate some errata
                errata = errata_template
                errata = errata.replace("%%ERRATAID%%",('RHEA-2012:%s' % random.randint(1,10000)))
                errata = errata.replace("%%REL%%", str(last_rev))                
                errata = errata.replace("%%NAME%%", name)
                errata = errata.replace("%%VER%%", version)
                all_errata += errata
                
    #bad string concats but I'm lazy                
    all_errata = "<?xml version=\"1.0\"?>\n<updates>" + all_errata 
    all_errata = all_errata + "</updates>\n"
    errata_xml = open('%s/updateinfo.xml' % outputdir, 'w')
    errata_xml.write(all_errata)

    

    os.system("mv ~/rpmbuild/RPMS/noarch/*elfake* %s" % outputdir)
    os.system("createrepo %s" % outputdir)
    os.system("modifyrepo %s/updateinfo.xml %s/repodata/" % (outputdir,outputdir))
    print "\n\n\n"
    print "==========================================================="
    print "Your new fake repo is available at: %s\n" % outputdir
    
    
