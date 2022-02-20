echo "Creating index settings and mappings"
curl -k -X DELETE -u admin:admin  "https://localhost:9200/bbuy_products"
#curl -k -X DELETE -u admin:admin  "https://localhost:9200/bbuy_queries"

curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d @opensearch/bbuy_products.json
#curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d @opensearch/bbuy_queries.json

echo "Indexing product data"
nohup python index_products.py -s datasets/product_data/products > logs/index_products.log &

#echo "Indexing queries data"
#nohup python index_queries.py -s datasets/train.csv > logs/index_queries.log &

#cd logstash/logstash-7.16.3/
#echo "Launching Logstash indexing in the background via nohup.  See product_indexing.log and queries_indexing.log for log output"
#echo "Cleaning up any old indexing information by deleting products_data.  If this is the first time you are running this, you might see an error."
#rm -rf logstash/logstash-7.16.3/products_data
#nohup bin/logstash  --pipeline.workers 1 --path.data ./products_data -f ../../logstash/index-bbuy.logstash > product_indexing.log &
#echo "Cleaning up any old indexing information by deleting query_data.  If this is the first time you are running this, you might see an error."
#rm -rf /workspace/logstash/logstash-7.16.3/query_data
#nohup bin/logstash --pipeline.workers 1 --path.data ./query_data -f ../logstash/index-bbuy-queries.logstash > queries_indexing.log &