for ftype in org clean cure
do
    for ptype in random scaffold
    do
        for name in aqua phys esol ochem aqsol chembl kinect
        do
            locat=''$name'_'$ftype'_'$ptype'/'
            echo $locat
            grep -r "Overall" $locat | cut -d" " -f 1,5- | sort -k 2 | cut -d"/" -f 9- | cut -d" " -f 2- | head -n 1 
        done
        echo ""
    done
    echo ""
done


#grep -r "Overall" aqua_org_random/* | cut -d" " -f 1,5- | sort -k 2 | cut -d"/" -f 9- | cut -d" " -f 2-
#grep -r "Overall" phys_org_random/* | cut -d" " -f 1,5- | sort -k 2 | cut -d"/" -f 9- | cut -d" " -f 2-
#grep -r "Overall" esol_org_random/* | cut -d" " -f 1,5- | sort -k 2 | cut -d"/" -f 9- | cut -d" " -f 2-
#grep -r "Overall" ochem_org_random/* | cut -d" " -f 1,5- | sort -k 2 | cut -d"/" -f 9- | cut -d" " -f 2-
