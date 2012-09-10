#!/bin/bash

EXPECTED_ARGS=3

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: `basename $0` <name> <version> <size-kilobytes>"
  exit 55
fi

pushd .
NAME=$1
VER=$2
SIZE=$3

SOURCES=$NAME-scratch/$NAME-$VER

echo $NAME
echo $VER
echo $SOURCES

rm -rf $NAME-scratch/
mkdir -p $SOURCES
cat specfile-template.ini | sed 's/%%NAME%%/'$NAME'/g' | sed 's/%%VERSION%%/'$VER'/g' > $NAME-scratch/$NAME.spec
echo "Dummy text file for $NAME" > $SOURCES/$NAME-test-file.txt
dd if=/dev/urandom of=$SOURCES/$NAME-dummy-data.dat bs=1k count=$SIZE
cat binary-template.ini | sed 's/%%NAME%%/'$NAME'/g' | sed 's/%%VERSION%%/'$VER'/g' > $SOURCES/$NAME
chmod +x $SOURCES/$NAME

# Create SPECS directory if it doesn't exists
if [ ! -d ~/rpmbuild/SPECS ]; then
    mkdir -p ~/rpmbuild/SPECS
fi

mv $NAME-scratch/$NAME.spec ~/rpmbuild/SPECS

# Untar
cd $NAME-scratch/
tar czvf $NAME-$VER.tar.gz *

# Create SOURCES directory if it doesn't exists
if [ ! -d ~/rpmbuild/SOURCES ]; then
    mkdir -p ~/rpmbuild/SOURCES
fi

mv $NAME-$VER.tar.gz ~/rpmbuild/SOURCES/

cd ~/rpmbuild/SPECS

# Check if rpmbuild is installed
if [ ! -e /usr/bin/rpmbuild ]; then
    echo "The rpm-build command was not found. Aborting."; exit 1;
fi

rpmbuild -bb $NAME.spec
popd 

# Cleanup
rm -rf $NAME-scratch/
