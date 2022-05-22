#!/bin/sh
# give me your cloud name
echo "give me your cloud name:" 
read CLOUD_NAME   
echo "give me your Tennat name:" 
read TENANT_NAME


#test=wget 
#toto="-O"
#koko=temp.openrc.txt
#url=http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc
#url_test=http://172.16.1.71:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc
#echo $test $url_test $toto $koko
#$test $url_test $toto $koko 
#download openrc
#"wget http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc -O temp.openrc.txt"
echo "wget http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc -O temp.openrc.txt"
wget "http://nexus3-prod.radcom.co.il:8081/repository/radcom-files/openrc/${CLOUD_NAME}/${CLOUD_NAME}-${TENANT_NAME}-openrc" -O temp.openrc.txt

#echo source /media/sf_share_local_ubuntu/work/temp.openrc.sh
#SCRIPT_PATH="/media/sf_share_local_ubuntu/work/temp.openrc.sh"
#sh  /media/sf_share_local_ubuntu/work/temp.openrc.sh
# . $SCRIPT_PATH

#while read line;  do  "$line" ; done < temp.openrc.sh

#for template in  `openstack port list --network $1 | awk '{print $2}'`
#do
#        echo "${template}"
#        openstack port delete ${template}
#done
#for i in `cat temp.openrc.sh |  awk '{print $2}'`;do echo $i;done

#for i in `echo temp.openrc.sh`;do echo $i;done

#export PATH=$PATH:/media/sf_share_local_ubuntu/work/temp.openrc.sh

for i in `cat temp.openrc.txt | grep -v PS1 |  awk '{print $2}'`;do export "$i";done

#openstack stack list | grep nc 
#BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#echo this is your base dir $BASEDIR
#source  ${BASEDIR}/temp.openrc.txt

#export PATH="$PATH:test"
#export MESSAGE="Now i am available on the current shell"
#source ./temp.openrc.txt.sh





