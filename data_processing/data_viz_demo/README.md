# Soil Power Data Visualization Webapp v0.1

**To get started**:

1) Place the webapp folder in the same folder as your data folder, so that it looks like:\
    main_dir\
     |-- data\
     |-- webapp\
     Alternatively, you can modify line 13, working_dir to whatever directory is above your data directory.
     Data should hold TEROS and soil data files.
     
2) Create a virtual environment or install requirements.txt to your python (basically install flask, numpy, pandas)

3) Run server.py in either an IDE or python server.py

4) Go to  http://127.0.0.1:5000/ to see the visualization



**Instructions for using the webapp**

- By default, the webapp will attempt to render soil data. It will take awhile to load the first time,
so just wait for the chart to appear

- You can choose whether to look at TEROS or soil data in the control panel to the left.

- To zoom in on the x axis, click and drag on the chart. The y axis is automatic

- To enable/disable different series, you can click on the series in the legend.


Please reach out on Slack or logandanek@gmail.com if you have any questions.

