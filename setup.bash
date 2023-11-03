#!/usr/bin/env bash

sudo hciconfig hci0 up
sudo ./people_counter.py &
flask --app web/people_counter_server run
