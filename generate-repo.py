#!/usr/bin/python

import datetime
import multiprocessing
from Queue import Queue
import random
from optparse import OptionParser
import os
import shutil
import subprocess
import sys
import threading

TYPES = ["security","bugfix","enhancement"]
FORMAT = "%Y-%m-%d %H:%M:%S"
try:
    ERRATA_TEMPLATE = open(os.path.join(os.path.dirname(__file__), "errata-template.xml")).read()
except Exception, e:
    print "Was not able to open errata template file: %s" % str(e)
    sys.exit(-1)

jobs = Queue()
all_errata = []
errata_lock = threading.Lock()
print_lock = threading.Lock()


def generate_errata(last_rev, name, version):
    errata = ERRATA_TEMPLATE
    errata = errata.replace("%%ERRATAID%%",('RHEA-2012:%s' % random.randint(1,10000)))
    errata = errata.replace("%%REL%%", str(last_rev))                
    errata = errata.replace("%%NAME%%", name)
    errata = errata.replace("%%VER%%", version)
    errata = errata.replace("%%TYPE%%", TYPES[random.randint(0,2)])
    errata = errata.replace("%%DATE%%", datetime.date(datetime.date.today().year - 1, random.randint(1,12), random.randint(1,28)).strftime(FORMAT))
    return errata
  

def shell_exec(command):
    with print_lock:
        print "Executing: $ %s" % command
    process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    output = process.communicate()
    stdout = output[0]
    stderr = output[1]
    if process.returncode != 0:
        print "STDOUT: %s" % stdout
        print "STDERROR: %s" % stderr
        exit(process.returncode)


def read_dictionary(wordsfile):
    """
    Reads a plain text file of names, one per line, which will be used
    to generate the names of RPMs.
    """
    try:
        with open(os.path.expanduser(wordsfile)) as fd:
            wordslist = [(word.replace(" ", "").strip()).replace("-", "") for word in fd.readlines()]
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


def generate_package(multiples, package_names, size): 
    errata = []
    while not jobs.empty():
        job = jobs.get()
        (package_name, version, package_size) = uniquefy_package(package_names, size)
        shell_exec("./generate-package.bash %s %s %s" % (package_name, version, package_size))

        if multiples:
            # Counter to increment revision version
            last_rev = int(version[-1])
            # Generate 1-3 newer versions of the package
            for j in range(random.randint(1,3)):
                last_rev += 1
                new_version = version[:-1] + str(last_rev)
                shell_exec("./generate-package.bash %s %s %s" % (package_name, new_version, package_size))

            # Generate some errata
            errata.append(generate_errata("1", package_name, new_version))
        jobs.task_done()

    with errata_lock:
        all_errata.extend(errata)


def generate_repo(output, number, size, multiples, dictionary, processes):
    """
    """
    cleanup_directory(os.path.expanduser(output))

    # List of names for our packages
    package_names = read_dictionary(dictionary)

    for package in range(number):
        jobs.put(number)

    for i in range(processes):
        worker = threading.Thread(target=generate_package, args=[multiples, package_names, size])
        worker.start()

    jobs.join()
                
    # Generate one specific package name you know is always there with multiple revs
    shell_exec("./generate-package.bash acme-package 1.0.1 1")
    shell_exec("./generate-package.bash acme-package 1.0.2 1")
    all_errata.append(generate_errata("1", "acme-package", "1.0.2"))
    shell_exec("./generate-package.bash acme-package 1.1.2 1")
    all_errata.append(generate_errata("1", "acme-package", "1.1.2"))
    
    
    #bad string concats but I'm lazy                
    errata_xml = "<?xml version=\"1.0\"?>\n<updates>" + ''.join(all_errata)
    errata_xml = errata_xml + "</updates>\n"
    updatedinfo = os.path.expanduser(os.path.join(output, "updateinfo.xml"))
    try:
        with open(updatedinfo, 'w') as errata_file:
            errata_file.write(errata_xml)
    except Exception, e:
        print "Could not save the errata file! %s" % str(e)
        sys.exit(-1)


    os.system("mv ~/rpmbuild/RPMS/noarch/* %s" % output)
    os.system("createrepo %s" % output)
    os.system("modifyrepo %s/updateinfo.xml %s/repodata/" % (output,output))

    print "\n\n\n"
    print "==========================================================="
    print "Your new fake repo is available at: %s" % output
    print "You may want to clean out your $HOME/rpmbuild dir as well.\n"


if __name__ == '__main__':

    description = "Generate a yum repository with fake packages and errata."

    usage = "Usage: %prog [[OUTPUT] [DICTIONARY] [NUMBER] [MULTIPLES] [SIZE]]"
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
    parser.add_option('-d', '--dictionary', dest='dictionary', type=str, default='words.txt')
    parser.add_option('-p', '--processes', dest='processes', type=int,
                      default=multiprocessing.cpu_count(),
                      help='number of process to use (default: number of cores)')

    (options, args) = parser.parse_args()

    output = options.output
    number = options.number
    size = options.size
    multiples = options.multiples
    dictionary = options.dictionary
    processes = options.processes

    generate_repo(output, number, size, multiples, dictionary, processes)
