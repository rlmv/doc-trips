

for file in *.sql; do 
    echo $file 
    mysql -uroot test < $file 
done
