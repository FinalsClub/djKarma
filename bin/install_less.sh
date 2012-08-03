#!/bin/bash

# This is required to get the less >> css compiler we use for our stylesheets on a linux machine.
# This assumes you have build-essential installed, and the perl program unp available in the ubuntu repos
# sudo apt-get install unp build-essential

wget http://nodejs.org/dist/v0.8.3/node-v0.8.3.tar.gz
unp node-v0.8.3.tar.gz 
node-v0.8.3/
./configure
make
sudo make install
npm install less
