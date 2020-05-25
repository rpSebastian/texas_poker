CURPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [ -f "$CURPATH/nohup.out" ]; then
    rm $CURPATH/nohup.out
fi
cd $CURPATH/../server/
nohup python init/init_agent.py  >>../scripts/nohup.out 2>&1 &
nohup python init/init_listener.py >>../scripts/nohup.out 2>&1 &
for((i=1;i<=1;i++));  
do   
    nohup python init/init_room_manager.py >>../scripts/nohup.out 2>&1 &
done  
nohup python init/init_scheduler.py >>../scripts/nohup.out 2>&1 &
