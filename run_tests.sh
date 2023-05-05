python3 run.py test > test/test.log &
API_PID=$(ps -aux | grep 'run.py' | awk '{print $2}' | head -1)
sleep 3
pytest . -vv
kill -9 $API_PID
rm instance/test.db