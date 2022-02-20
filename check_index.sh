while [ true ];
do
  echo "Queries:"
  curl -k -XGET -uadmin:admin "https://localhost:9200/_cat/count/bbuy_queries";
  echo "Products:"
  curl -k -XGET -uadmin:admin "https://localhost:9200/_cat/count/bbuy_products";
  sleep 100;
done