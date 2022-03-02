# test.sh
# Start a Tmux Session, run the tests.
# Delete all tests when leaving Tmux.

tmux new-session -d -s deskapp_test;
tmux send "python -m venv test" ENTER;
tmux send "source test/bin/activate" ENTER;
tmux send "echo 'Now in the Test Enviroment.'" ENTER;
tmux send '. install.sh' ENTER;
# tmux split-window;
clear;
tmux a -t deskapp_test;
deactivate
rm -rf test
echo "Concluded test run. Removed Test Enviroment."