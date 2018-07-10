#!/bin/bash

env LD_LIBRARY_PATH="/usr/lib:/usr/include:lib/" ./blenderplayer $@ client.blend
