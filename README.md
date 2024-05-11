
**Guidline to Run this project******


**1. install the required dependecies in you virtual environment by runing this command**

    pip freeze > requirements.txt
   
**2.  Run this command to scrape data**

    -> scrapy crawl ScrapEmailsSpider -a query="softwae house in UK" -o res.csv

    query:  based on query will search on google
    -o   :  this tag helps to generate ouput in files (csv, xslx ...)
    -a   : mentioned for arguments that we are passing as query
     
