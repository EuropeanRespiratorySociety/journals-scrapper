#Quick export to csv
scrapy crawl article --output=../../Projects/scrapy-journals/data/erj-test.csv

# Saves state of the spider
scrapy crawl article -s  JOBDIR=./data

source venv/bin/activate

<collection>.deleteMany({"canonical":{$regex : ".*\.DC1"}})

# Build 

`docker build -t <name> .`
`docker run -a <name>`