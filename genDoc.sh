#!/bin/bash

# python3 ./extract_comments.py README.md ./
# echo 'python3 ./extract_comments.py README.md ./'

(cd ./example_ServoMotor/; python3.11 ../extract_comments2.py README.md -source ./ -include ../)
echo '(cd ./example_ServoMotor/; python3 ../extract_comments2.py README.md -source ./ -include ../)'

(cd ./example_DistanceSensor/; python3.11 ../extract_comments2.py README.md -source ./ -include ../)
echo '(cd ./example_DistanceSensor/; python3 ../extract_comments2.py README.md -source ./ -include ../)'

(cd ./example_StepperMotor/; python3.11 ../extract_comments2.py README.md -source ./ -include ../)
echo '{cd ./example_StepperMotor/; python3 ../extract_comments2.py README.md -source ./ -include ../)'

(cd ./example_OpenCV/; python3.11 ../extract_comments2.py README.md -source ./ -include ../)
echo '{cd ./example_OpenCV/; python3 ../extract_comments2.py README.md -source ./ -include ../)'

python3.11 generate_readme.py