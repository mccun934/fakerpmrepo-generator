fakerpmrepo-generator
=====================

Creates a set of RPM packages between 1-1000KB in size with random names and versions read in from a "dictionary" file.

An example can be found at: http://mmccune.fedorapeople.org/random/

Each package installs the following files:

/etc/<name>-test-file.txt
/var/lib/<name>-dummy-data.dat
/usr/sbin/<name> executable script, eg:

For package rexline-5.7.9-1.elfake.noarch.rpm you get:

$ rexline
====================================

rexline version 5.7.9

Thank you for installing [rexline]

====================================


Run the top level script:

    $ ./generate-repo.py --number=10
    Executing: $ ./generate-package.bash Denmark 4.4.6 75
    Executing: $ ./generate-package.bash Iceland 4.7.3 35
    Executing: $ ./generate-package.bash Cameroon 2.10.1 86
    Executing: $ ./generate-package.bash Indonesia 10.9.7 72
    Executing: $ ./generate-package.bash Mongolia 0.1.0 60
    Executing: $ ./generate-package.bash Monaco 10.2.6 100
    Executing: $ ./generate-package.bash Moldova 7.3.8 97
    Executing: $ ./generate-package.bash Tanzania 7.9.7 53
    Executing: $ ./generate-package.bash Chad 6.3.3 92
    Executing: $ ./generate-package.bash EquatorialGuinea 5.0.6 75
    Executing: $ ./generate-package.bash acme-package 1.0.1 1
    Executing: $ ./generate-package.bash acme-package 1.0.2 1
    Executing: $ ./generate-package.bash acme-package 1.1.2 1
    Spawning worker 0 with 13 pkgs
    Workers Finished
    Gathering worker results

    Saving Primary metadata
    Saving file lists metadata
    Saving other metadata
    Generating sqlite DBs
    Sqlite DBs complete
    Wrote: /var/tmp/generated-repo/repodata/updateinfo.xml.xz
               type = updateinfo
           location = repodata/4ade90b07e0ce0471b412a3db19d90e27583337a019813e9a457921aaf791f02-updateinfo.xml.xz
           checksum = 4ade90b07e0ce0471b412a3db19d90e27583337a019813e9a457921aaf791f02
          timestamp = 1347059999.84
      open-checksum = 63e1ea95e0722e1f9d7d93030fc59e4e972333562e268753121be3d70552f006
    Wrote: /var/tmp/generated-repo/repodata/repomd.xml

    ===========================================================
    Your new fake repo is available at: /var/tmp/generated-repo
    You may want to clean out your $HOME/rpmbuild dir as well.


===========================================================
Your new fake repo is available at: /var/tmp/generated-repo

$ ls /var/tmp/generated-repo/
acme-package-1.0.1-1.elfake.noarch.rpm      Indonesia-10.9.7-1.elfake.noarch.rpm
acme-package-1.0.2-1.elfake.noarch.rpm      Moldova-7.3.8-1.elfake.noarch.rpm
acme-package-1.1.2-1.elfake.noarch.rpm      Monaco-10.2.6-1.elfake.noarch.rpm
Cameroon-2.10.1-1.elfake.noarch.rpm         Mongolia-0.1.0-1.elfake.noarch.rpm
Chad-6.3.3-1.elfake.noarch.rpm              repodata/
Denmark-4.4.6-1.elfake.noarch.rpm           Tanzania-7.9.7-1.elfake.noarch.rpm
EquatorialGuinea-5.0.6-1.elfake.noarch.rpm  updateinfo.xml
Iceland-4.7.3-1.elfake.noarch.rpm