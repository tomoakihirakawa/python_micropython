#!/bin/bash

# python3 ./extract_comments.py README.md ./
# echo 'python3 ./extract_comments.py README.md ./'

(cd ./example_ServoMotor/; python3 ../extract_comments.py README.md ./ ../)
echo '(cd ./example_ServoMotor/; python3 ../extract_comments.py README.md ./ ../)'

(cd ./example_ultrasonic_sistance_sensor/; python3 ../extract_comments.py README.md ./ ../)
echo '(cd ./example_ultrasonic_sistance_sensor/; python3 ../extract_comments.py README.md ./ ../)'

python3 generate_readme.py