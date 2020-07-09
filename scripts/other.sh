CURPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [ -f "$CURPATH/nohup.out" ]; then
    rm $CURPATH/nohup.out
fi
cd $CURPATH/../server/
rm -rf ./logs/runtime.log
nohup python init/init_listener.py >>../scripts/nohup.out 2>&1 &
nohup python init/init_room_manager.py >>../scripts/nohup.out 2>&1 &
cd $CURPATH/../server/agent
nohup python agent_receiver.py >> $CURPATH/nohup.out 2>&1 &



