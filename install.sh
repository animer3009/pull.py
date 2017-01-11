#!/bin/bash

INIT=$(ps -p 1 |tail -n 1 |awk '{print $4}')

install() {
cp pull.py /usr/local/bin/
chmod 750 /usr/local/bin/pull.py
cp pull_py_default /etc/default/pull_py
if [ "$INIT" = 'init' ]; then 
cp pull_py_upstart.conf /etc/init/pull_py.conf
#cp pull_py_upstart.override /etc/init/pull_py.override
elif [ "$INIT" = 'systemd' ]; then
cp pull_py_systemd /etc/systemd/system/pull_py.service
systemctl enable pull_py.service
fi
#cp pull_py_cron /etc/cron.d/pull_py
#service cron reload
bash pull_py_iptables
echo -e "\e[32mPull.py successfuly installed.\nTo start it please set variables in /etc/default/pull_py and run: start pull_py.\nCron job to automaticaly start and stop pyll.py script, is located on /etc/cron.d/pull_py.\e[m"
echo -e "\e[31mPlease remember! It is necessary, that READ_ONLY user is member of project in gitlab (with reader privileges) from which you will to pull, and web-hook is configured with IP-Address of this server.\nWeb-Hook URL Example: http://10.10.120.1:8000\e[m"
echo -e "\e[31mAlso Remembrer to restrict access to .git directory in web-apps document-root. See configuration examples in pull_py_apache.example file.\e[m"
}

install_unpriv() {
echo -e "\e[31m Please enter username or uid under which privileges pull.py script will be run.\nUSER:\e[m"
read SETUID
cp pull.py /usr/local/bin/
chmod 750 /usr/local/bin/pull.py
setfacl -m u:"$SETUID":rwx /usr/local/bin/pull.py
setfacl -m u:"$SETUID":rwx /var/log
cp pull_py_default /etc/default/pull_py
if [ "$INIT" = 'init' ]; then 
cp pull_py_upstart.conf /etc/init/pull_py.conf
sed -i "s/#setuid/setuid\ $SETUID/" /etc/init/pull_py.conf 
#cp pull_py_upstart.override /etc/init/pull_py.override
elif [ "$INIT" = 'systemd' ]; then
cp pull_py_systemd /etc/systemd/system/pull_py.service
sed -i "s/Environment=UPRIV=root/Environment=UPRIV=$SETUID/" /etc/systemd/system/pull_py.service
systemctl enable pull_py.service
fi
#cp pull_py_cron /etc/cron.d/pull_py
#service cron reload
bash pull_py_iptables
echo -e "\e[32mPull.py successfuly installed.\nTo start it please set variables in /etc/default/pull_py and run: start pull_py.\nCron job to automaticaly start and stop pyll.py script, is located on /etc/cron.d/pull_py.\e[m"
echo -e "\e[31mPlease remember! It is necessary, that READ_ONLY user is member of project in gitlab (with reader privileges) from which you will to pull, and web-hook is configured with IP-Address of this server.\nWeb-Hook URL Example: http://10.10.120.1:8000\e[m"
echo -e "\e[31mAlso Remembrer to restrict access to .git directory in web-apps document-root. See configuration examples in pull_py_apache.example file.\e[m"
}

uninstall() {
if [ "$INIT" = 'init' ]; then 
stop pull_py 2>/dev/null
rm /etc/init/pull_py.conf
#rm /etc/init/pull_py.override
elif [ "$INIT" = 'systemd' ]; then
systemctl stop pull_py.service 2>/dev/null
rm /etc/systemd/system/pull_py.service
systemctl daemon-reload
fi
rm /usr/local/bin/pull.py
rm /etc/default/pull_py
#rm /etc/cron.d/pull_py
rm /var/log/pull.py.log
#service cron reload
echo -e "\e[32mPull.py successfuly uninstalled.\e[m"
}


case "$1" in
        install)
            install
            ;;

        install_unpriv)
            install_unpriv
            ;;
         
        uninstall)
            uninstall
            ;;
         
        *)
            echo $"Usage: $0 {install|install_unpriv|uninstall}"
            exit 1
esac
