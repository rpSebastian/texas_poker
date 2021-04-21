#! /usr/bin/bash
if [ -f "/home/dell/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/dell/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/dell/miniconda3/bin:$PATH"
    fi
conda activate
pids1=`ps -ef | grep "python -u server" | grep -v grep | awk '{print $2}'`
pids2=`ps -ef | grep "python -u agent" | grep -v grep | awk '{print $2}'`
pids=${pids1}" "${pids2}
echo $pids | xargs kill -9

CURPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [ -f "$CURPATH/nohup.out" ]; then
    rm $CURPATH/nohup.out
fi
cd $CURPATH/../multi_gev_server/
# rm -rf ./utils/runtime.log

nohup python -u server.py >> $CURPATH/nohup.out 2>&1 &
cd $CURPATH/../multi_gev_server/agent
echo $CURPATH
nohup python -u agent_receiver.py >> $CURPATH/nohup.out 2>&1 &

