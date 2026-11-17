wget -O /etc/opkg/emil-dream-feed.conf http://dreambox4u.com/emilnabil237/feed/emil-dream-feed.conf
echo "     DOWNLOADING FEED EMIL OK "
wait
echo ""
echo "##############################################################"
opkg update
echo "##############################################################"
echo "**************************************************************"
echo "   UPLOADED SCRIPT  BY  >>>>   EMIL_NABIL "
sleep 4;
echo ". >>>>         RESTARING     <<<<"
echo "**********************************************************************************"
wait
killall -9 enigma2
exit 0

