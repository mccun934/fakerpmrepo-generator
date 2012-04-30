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

mv $NAME-scratch/$NAME.spec ~/rpmbuild/SPECS
cd $NAME-scratch/
tar czvf $NAME-$VER.tar.gz *
mv $NAME-$VER.tar.gz ~/rpmbuild/SOURCES/
cd ~/rpmbuild/SPECS
rpmbuild -bb $NAME.spec
popd 
rm -rf $NAME-scratch/
