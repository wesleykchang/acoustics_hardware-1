#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/pithy

forever start index.js 8001 --codebase=../code --histbase=../code_stamped > ../logs/pithy.log

