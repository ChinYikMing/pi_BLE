#!/usr/bin/env bash


sudo hciconfig hci0 up
#sudo ./people_counter.py
#flask --app web/people_counter_server run
#sudo parallel ::: ./people_counter.py flask --app web/people_counter_server run
#
(echo 'sudo ./people_counter.py'; echo 'flask --app web/people_counter_server run') | sudo parallel -j0 --lb

#parallel -j0 --lb  <<EOF
#echo ./people_counter.py
#echo flask --app web/people_counter_server run
#EOF

