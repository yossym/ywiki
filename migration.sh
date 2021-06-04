#!/usr/bin/bash -ue
# $Id: migration.sh,v 1.1 2018/12/08 22:43:55 yossym Exp yossym $
if [ "${USER}" = "root" ]; then

    if [ $# != 1 ]; then
        echo $0 [parent directory name]
        exit 1
    fi

	chmod +x *.cgi
	chown apache.apache wiki
	chmod 755 ..
	chown apache ..
	chgrp apache ..


    conf=$(cat << EOS  > /etc/httpd/conf.d/${1}.conf
# for erver version: Apache/2.4.6 (CentOS)
#
# /etc/httpd/conf.d/${1}.conf
# 新規作成
# 拡張子 cgi および pl を CGI として扱う
<Directory "/var/www/html/${1}">
    Options +ExecCGI -Indexes
    AddHandler cgi-script .cgi .pl

    AuthUserFile /etc/httpd/conf/.htpasswd
    AuthGroupFile /dev/null
    AuthName "Basic Auth"
    AuthType Basic
    Require valid-user
</Directory>
EOS
)

echo "execute to root user"
echo "systemctl restart httpd"

	exit 0
else
	echo "chenge root user."
	echo "su -"
	exit -1
fi
