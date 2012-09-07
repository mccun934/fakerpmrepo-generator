#!/usr/bin/python

import subprocess
import sys
import optparse
import random
import os
import shutil
from optparse import OptionParser

def generate_errata(template, last_rev, name, version):
    errata = template
    errata = errata.replace("%%ERRATAID%%",('RHEA-2012:%s' % random.randint(1,10000)))
    errata = errata.replace("%%REL%%", str(last_rev))                
    errata = errata.replace("%%NAME%%", name)
    errata = errata.replace("%%VER%%", version)
    return errata
  
  

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


def read_dictionary(wordsfile='words'):
    """
    Reads a plain text file of names, one per line, which will be used
    to generate the names of RPMs.
    """
    try:
        fd = open(wordsfile)
        wordslist = [word.replace(" ", "").strip() for word in fd.readlines()]
        fd.close()
    except Exception, e:
        print "Was not able to open the words file %s: %s" % (wordsfile, str(e))
        sys.exit(-1)

    return wordslist


def cleanup_directory(outputdir):
    """
    Make sure we have a clean slate.
    """

    if os.path.isdir(outputdir):
        shutil.rmtree(outputdir)
    os.mkdir(outputdir)


def read_template(template_path):
    """
    Returns 
    """

    try:
        fd = open(template_path, "r")
        template = fd.read()
        fd.close()
    except Exception, e:
        print "Was not able to open errata template file: %s" % str(e)
        sys.exit(-1)

    return template


def uniquefy_package(package_names, max_size):
    """
    Returns a random and unique package name and version.
    """
    package_name = random.choice(package_names).rstrip()
    first_rev = str(random.randint(0,10))
    middle_rev = str(random.randint(0,10))
    last_rev = str(random.randint(0,10))
    version = "%s.%s.%s" % (first_rev, middle_rev, last_rev)
    size = str(random.randint(0, max_size))

    return (package_name, version, size)


def generate_repo(output, number, size, multiples):
    """
    """
    cleanup_directory(os.path.expanduser(output))

    # List of names for our packages
    package_names = read_dictionary()

    all_errata = ""

    errata_template = read_template("errata-template.xml")

    for package in range(number):
        (package_name, version, package_size) = uniquefy_package(package_names, size)
        shell_exec("./generate-package.bash %s %s %s" % (package_name, version, package_size))

        if multiples:
            # Counter to increment revision version
            last_rev = int(version[-1])
            # Generate 0-3 newer versions of the package
            for j in range(random.randint(0,3)):

                last_rev += 1
                new_version = version[:-1] + str(last_rev)
                shell_exec("./generate-package.bash %s %s %s" % (package_name, new_version, package_size))
                # Generate some errata
                all_errata += generate_errata(errata_template, last_rev, package_name, version)
                
    # Generate one specific package name you know is always there with multiple revs
    shell_exec("./generate-package.bash acme-package 1.0.1 1")
    shell_exec("./generate-package.bash acme-package 1.0.2 1")
    all_errata += generate_errata(errata_template, "1.0.1 ", "acme-package", "1.0.2")
    shell_exec("./generate-package.bash acme-package 1.1.2 1")
    all_errata += generate_errata(errata_template, "1.0.2 ", "acme-package", "1.1.2")
    
    
    #bad string concats but I'm lazy                
    all_errata = "<?xml version=\"1.0\"?>\n<updates>" + all_errata 
    all_errata = all_errata + "</updates>\n"
    updatedinfo = os.path.expanduser(os.path.join(output, "updateinfo.xml"))
    try:
        errata_xml = open(updatedinfo, 'w')
        errata_xml.write(all_errata)
        errata_xml.close()
    except Exception, e:
        print "Could not save the errata file! %s" % str(e)
        sys.exit(-1)


    os.system("mv ~/rpmbuild/RPMS/noarch/*elfake* %s" % output)
    os.system("createrepo %s" % output)
    os.system("modifyrepo %s/updateinfo.xml %s/repodata/" % (output,output))

    print "\n\n\n"
    print "==========================================================="
    print "Your new fake repo is available at: %s" % output
    print "You may want to clean out your $HOME/rpmbuild dir as well.\n"


if __name__ == '__main__':

    description = "Generate a yum repository with fake packages and errata."

    usage = "Usage: %prog [[OUTPUT] [NUMBER] [MULTIPLES] [SIZE]]"
    epilog = "Constructive comments and feedback can be sent to mmccune at redhat dot com" \
        " and omaciel at ogmaciel dot com."
    version = "%prog version 0.1"

    parser = OptionParser(usage=usage, description=description, epilog=epilog, version=version)
    parser.add_option('-s', '--size',  dest='size', 
        help='maximum size in KB for created packages', type=int, default=100)
    parser.add_option('-n', '--number',  dest='number',  type=int, default=5)
    parser.add_option('-m', '--multiples',  dest='multiples',  
        help="generate 0-3 random new versions of each package and errata",
        action="store_true", default=False)
    parser.add_option('-o', '--output',  dest='output', type="str", default='/var/tmp/generated-repo')

    (options, args) = parser.parse_args()

    output = options.output
    number = options.number
    size = options.size
    multiples = options.multiples

    generate_repo(output, number, size, multiples)
