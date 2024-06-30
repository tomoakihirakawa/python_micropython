#!/bin/bash

# python3 ./extract_comments.py README.md ./
# echo 'python3 ./extract_comments.py README.md ./'

(cd ./example_ServoMotor/; python3.11 ../extract_comments.py README.md ./ ../)
echo '(cd ./example_ServoMotor/; python3 ../extract_comments.py README.md ./ ../)'

(cd ./example_DistanceSensor/; python3.11 ../extract_comments.py README.md ./ ../)
echo '(cd ./example_DistanceSensor/; python3 ../extract_comments.py README.md ./ ../)'

(cd ./example_StepperMotor/; python3.11 ../extract_comments.py README.md ./ ../)
echo '{cd ./example_StepperMotor/; python3 ../extract_comments.py README.md ./ ../)'

(cd ./example_OpenCV/; python3.11 ../extract_comments.py README.md ./ ../)
echo '{cd ./example_OpenCV/; python3 ../extract_comments.py README.md ./ ../)'

python3.11 generate_readme.py