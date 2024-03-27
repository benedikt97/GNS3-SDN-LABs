
for i in 172.30.240.41 172.30.240.42 172.30.240.43 172.30.240.44 172.30.240.45
do
	echo "$i"
	sshpass -p "YourPaSsWoRd" ssh admin@$i sudo chmod 777 /etc/sonic/config_db.json
	sshpass -p "YourPaSsWoRd" scp ./json-up/$i.json admin@$i:/etc/sonic/config_db.json 
	sshpass -p "YourPaSsWoRd" ssh admin@$i sudo config reload -f -y
done
