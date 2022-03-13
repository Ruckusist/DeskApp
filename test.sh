# test.sh
# Start a Tmux Session, run the tests.
# Delete all tests when leaving Tmux.

# SERVER START UP
tmux new-session -d -s Game_Server;
tmux send -t Game_Server "python -m venv Test_Server" ENTER;
tmux send -t Game_Server "source Test_Server/bin/activate" ENTER;
tmux send -t Game_Server "echo 'Now in the Server Test Enviroment.'" ENTER;
tmux send -t Game_Server "python game/Server/game.py" ENTER;

# CLIENT START UP
tmux new-session -d -s Game_Client;
tmux send -t Game_Client "python -m venv Test_Client" ENTER;
tmux send -t Game_Client "source Test_Client/bin/activate" ENTER;
tmux send -t Game_Client "echo 'Now in the Client Test Enviroment.'" ENTER;
tmux send -t Game_Client "echo 'Setting up Exit Door; Type stop to exit'" ENTER;
tmux send -t Game_Client "alias stop='tmux detach'" ENTER;
tmux send -t Game_Client '. install.sh' ENTER;
tmux send -t Game_Client 'cd game/Client' ENTER;
tmux send -t Game_Client "echo '|  - TYPE stop TO EXIT -  |'" ENTER;
tmux send -t Game_Client 'python game_client.py' ENTER;
# clear;
tmux a -t Game_Client;
tmux send -t Game_Client 'deactivate' ENTER;
tmux send -t Game_Client 'cd ..' ENTER;
tmux send -t Game_Client 'cd ..' ENTER;
tmux send -t Game_Client 'rm -rf Test_Client' ENTER;
tmux send -t Game_Client 'exit' ENTER;
# tmux send-keys -t Game_Client C-d;

# tmux a -t Game_Server;
tmux send-keys -t Game_Server C-c;
tmux send -t Game_Server 'deactivate' ENTER;
tmux send -t Game_Server 'rm -rf Test_Server' ENTER;
tmux send -t Game_Server 'exit' ENTER;
# tmux send-keys -t Game_Server C-d;

echo "Concluded test run. Removed Test Enviroment.";