#! /usr/bin/bash
pids1=`ps -ef | grep "python -u server" | grep -v grep | awk '{print $2}'`
pids2=`ps -ef | grep "python -u agent" | grep -v grep | awk '{print $2}'`
pids=${pids1}" "${pids2}

if [ "$pids" == "" ]
then
    echo "already stopped!"
    exit 0
fi

echo $pids | xargs kill -9
if [ $? -eq 0 ]
then
    echo "stopped"
    exit 0
else
    echo "stop failed!"
    echo -1
fi
