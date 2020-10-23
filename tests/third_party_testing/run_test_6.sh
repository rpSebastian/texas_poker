num_players=6
for connections in 1 50 100 500 1000;
do
    for num_matches in 1 10 20 50; 
    do
        echo $connections, $num_matches
        python battle_n_paris_m_matches.py --num_players=$num_players --connections=$connections --num_matches=$num_matches
    done
done

