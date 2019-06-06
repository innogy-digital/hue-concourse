Connect phillips hue to concourse ci
====================================

This little python script connects our builds pipelines to our hue lights. 

Pipeline Running -> light blinks yellow

Pipeline Broken -> lights blink red

Pipeline Success -> lights light green  


Start
-----
`./__main__.py`


Configuration
-------------
Enter hue username in `HUE_USERNAME` in `hueci/app.py`.

To assign a pipeline to a lamp, see `LAB` in `hueci/app.py`.
