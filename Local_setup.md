### Local setup instructions 
Tested only on Mac. Windows setup will require different steps for setting up and configuring Python virtual environment

1. Clone your github repo locally
2. Start Opensearch locally via Docker

       cd docker 
       docker-compose up

3. Follow instructions in README.md to download data from kaggle
4. Setup python environment. You can either do it via virtulalenv like it is done in Gitpod

       pyenv virtualenv 3.9.7 search_with_ml_opensearch
       pyenv virtualenv 3.9.7 search_with_ml_week1
       pyenv virtualenv 3.9.7 search_with_ml_week2
       pyenv virtualenv 3.9.7 search_with_ml_week3
       pyenv virtualenv 3.9.7 search_with_ml_week4
 or 
setup via conda/miniconda or any preferred way to set up python virtual environment
for Conda/Miniconda (assuming it is already downloaded)

       conda create -n search_with_ml python=3.8
       conda activate search_with_ml
       pip install -r requirements_week1.txt
       pip install pandas click

6. Download logstash (if you are going to use it. I ended up rewriting indexing in python)

       curl -o logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz https://artifacts.opensearch.org/logstash/logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
       tar -xf logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz
       rm logstash-oss-with-opensearch-output-plugin-7.13.2-linux-x64.tar.gz

7. Running indexing using python (For using logstash follow README.md instructions)
Download indexing implementation in python

       wget https://raw.githubusercontent.com/dshvadskiy/search_with_machine_learning_course/main/index_products.py
       wget https://raw.githubusercontent.com/dshvadskiy/search_with_machine_learning_course/main/index_queries.py
       wget https://raw.githubusercontent.com/dshvadskiy/search_with_machine_learning_course/main/index-data.sh
       chmod +x index-data.sh
8. Run indexing 
 
       ./index-data.sh 
9. Configure and run Flask app in PyCharm

       Edit Configurations->Add Configuration->Flask server
       target:week1
       Additional options: --port 3000
       FLASK_ENV: development
       Python environment: <environment you configured in Step 4>    

    If Flask server configuration not available (PyCharm Community Edition???) just configure to run as python app and set environment variables

       FLASK_APP = week1
       FLASK_ENV = development
       FLASK_DEBUG = 1

       python -m flask run --port 3000
