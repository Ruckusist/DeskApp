echo "Transfering Game File"
sshpass -p "dad2344" scp -P 31415 game.py dad@ruckusist.com:;
echo "Transfering Messages File"
sshpass -p "dad2344" scp -P 31415 messages.py dad@ruckusist.com:;
echo "Finished Transfer"