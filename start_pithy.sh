#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

forever start $DIR/pithy/index.js 8001 --codebase=$DIR/code --histbase=$DIR/code_stamped > $DIR/pithy.log

