# test.sh
# Start a Tmux Session, run the tests.
# Delete all tests when leaving Tmux.

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

echo "Concluded test run. Removed Test Enviroment.";