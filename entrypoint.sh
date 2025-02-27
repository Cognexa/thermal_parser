#!/bin/bash

export LD_LIBRARY_PATH="/usr/lib/dji/release_x64:$LD_LIBRARY_PATH"
exec "$@"
