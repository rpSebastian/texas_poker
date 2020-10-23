CURPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [ -f "$CURPATH/nohup.out" ]; then
    rm $CURPATH/nohup.out
fi
cd $CURPATH/../multi_gev_server/
rm -rf ./utils/runtime.log

nohup python -u server.py >> $CURPATH/nohup.out 2>&1 &
cd $CURPATH/../multi_gev_server/agent
nohup python -u agent_receiver.py >> $CURPATH/nohup.out 2>&1 &