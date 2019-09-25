---

#利用salt stack pillar安装多组keepalived

---

### 环境描述

在生产环境中，需要搭建三套keepalived环境，3个master和3个backup，要安装的软件和配置文件，虽然不是很多，一个一个配置也工作量不大，最近看了一下salt的状态模块，感觉可以通过salt来直接进行安装并自定义配置，下面记录一下操作的过程。

### 操作过程

首先先分析一下keepalive的配置文件，主要需要修改的地方有6处：

	Keepalived_Router_ID: router_id
	Keepalived_Interface: interface
	Keepalived_Mcast_src_ip: mcast_src_ip
	Keepalived_Virtual_Router_ID: virtual_router_id
	Keepalived_status: state
	Keepalived_priority: priority
	Keepalived_Virtual_Ipaddress: virtual_ipaddress

最开始想到的是，利用master和backup的区分，然后基于virtual_router_id来设置ip地址，所以想的是每一组keepalived做两个状态文件，一个文件是master主机用，一个是backup主机用，这样就需要做6个状态文件，虽然是能实现自动化配置，但是需要创建和修改的配置文件也是不少，划不来。

所以想到了pillar的方式，在salt中，为每一个主机，定义keepalived相关的属性参数，然后在安装配置keepalived的时候，基于这些属性参数，自定义修改配置文件，然后生效。首先对6台主机进行配置规划，也就是这6个字段。

|Minion|10.2.86.76|10.2.86.77|10.2.86.106|10.2.86.107|10.2.86.115|10.2.86.116|
|:---|:---|:---|:---|:---|:---|:---|
|**Keepalived_Router_ID**|76|77|106|107|115|116|
|**Keepalived_Interface**|eth2|eth2|eth1|eth1|eth1|eth1|
|**Keepalived_Mcast_src_ip**|10.2.86.76|10.2.86.77|10.2.86.106|10.2.86.107|10.2.86.115|10.2.86.116|
|**Keepalived_Virtual_Router_ID**|118|118|110|110|108|108|
|**Keepalived_status**|master|backup|master|backup|master|backup|
|**Keepalived_priority**|120|100|120|100|120|100|
|**Keepalived_Virtual_Ipaddress**|10.2.86.118/26|10.2.86.118/26|10.2.86.110/26|10.2.86.110/26|10.2.86.108/26|10.2.86.108/26|

在master上，为每个minion配置这些pillar属性。顶层创建top.sls文件，然后在top文件中定义minion和对应pillar的对应关系，然后创建状态文件。

启用pillar，在/etc/salt/master文件中，修改pillar_roots，设置base的路径为/srv/salt/base/pillar
	
	pillar_roots:
	  base:
	    - /srv/salt/base/pillar

	
创建keepalived目录，在该目录中，放置对应节点的pillar定义，编写top文件

	[root@mysqlbackup pillar]# cat top.sls 
	base:
	  '10.2.86.76':
	    - keepalived.Keepalived_76
	[root@mysqlbackup pillar]# cat keepalived/Keepalived_76.sls 
	Keepalived_Router_ID: 76
	Keepalived_Interface: eth2
	Keepalived_Mcast_src_ip: 10.2.86.76
	Keepalived_Virtual_Router_ID: 118
	Keepalived_status: master
	Keepalived_priority: 120
	Keepalived_Virtual_Ipaddress: 10.2.86.118/26

编写完成后，查看生效情况

	[root@mysqlbackup pillar]# salt '10.2.86.76' pillar.ls
	10.2.86.76:
	    - Keepalived_Interface
	    - Keepalived_priority
	    - Keepalived_Virtual_Router_ID
	    - Keepalived_Router_ID
	    - Keepalived_status
	    - Keepalived_Virtual_Ipaddress
	    - Keepalived_Mcast_src_ip
	[root@mysqlbackup pillar]# salt '10.2.86.76' pillar.items
	10.2.86.76:
    ----------
    Keepalived_Interface:
        eth2
    Keepalived_Mcast_src_ip:
        10.2.86.76
    Keepalived_Router_ID:
        76
    Keepalived_Virtual_Ipaddress:
        10.2.86.118/26
    Keepalived_Virtual_Router_ID:
        118
    Keepalived_priority:
        120
    Keepalived_status:
        master

minion的pillar生效之后，就开始修改默认的配置文件，将相关的变量，设置为pillar取值。

	[root@mysqlbackup keepalived]# cat ../files/keepalived/keepalived.conf
	! Configuration File for keepalived
	
	global_defs {
	   notification_email { 
	     acassen@firewall.loc
	   }
	   notification_email_from Alexandre.Cassen@firewall.loc  
	   smtp_server 127.0.0.1     
	   smtp_connect_timeout 30    
	   router_id {{ pillar['Keepalived_Router_ID'] }} 
	}
	
	vrrp_script chk_mysql_port {     
	    script "/opt/chk_mysql.sh"   
	    interval 2           
	    weight -5            
	    fall 2             
	    rise 1             
	}
	
	vrrp_instance VI_1 {
	    state {{ pillar['Keepalived_status'] }}
	    nopreempt           
	    interface {{ pillar['Keepalived_Interface'] }}          
	    mcast_src_ip {{ pillar['Keepalived_Mcast_src_ip'] }}
	    virtual_router_id {{ pillar['Keepalived_Virtual_Router_ID'] }}    
	    priority {{ pillar['Keepalived_priority'] }}          
	    advert_int 1          
	    authentication {
	        auth_type PASS 
	        auth_pass 1111 
	    }
	    virtual_ipaddress {
	        {{ pillar['Keepalived_Virtual_Ipaddress'] }}
	    }
	   # track_script {  
	   #     chk_mysql_port
	   # }
	}

下一步是编写状态文件，一个状态文件中，包含keepalived的安装、配置文件管理和服务管理。

	[root@mysqlbackup keepalived]# cat keepalived.sls 
	include:
	  - keepalived.keepalived-install
	  - keepalived.configuration
	  - keepalived.services
	[root@mysqlbackup keepalived]# cat keepalived-install.sls 
	keepalived-install:
	  pkg.installed:
	    - names:
	      - keepalived
	[root@mysqlbackup keepalived]# cat configuration.sls 
	configuration:
	  file.managed:
	    - name: /etc/keepalived/keepalived.conf
	    - source: salt://files/keepalived/keepalived.conf
	    - user: root
	    - group: root
	    - mode: 644
	    - backup: minion
	    - template: jinja
	[root@mysqlbackup keepalived]# cat services.sls 
	keepalived-service:
	  service.running:
	    - name: keepalived
	    - enable: True
	    - watch:
	      - file: /etc/keepalived/keepalived.conf
	    - reload: True

下一步就是在指定的minion上执行该状态文件，检查安装的结果。

	[root@mysqlbackup keepalived]# salt '10.2.86.76' state.sls keepalived.keepalived
	10.2.86.76:
	----------
	          ID: keepalived-install
	    Function: pkg.installed
	        Name: keepalived
	      Result: True
	     Comment: All specified packages are already installed
	     Started: 08:06:42.776064
	    Duration: 1295.253 ms
	     Changes:   
	----------
	          ID: configuration
	    Function: file.managed
	        Name: /etc/keepalived/keepalived.conf
	      Result: True
	     Comment: File /etc/keepalived/keepalived.conf updated
	     Started: 08:06:44.075458
	    Duration: 125.626 ms
	     Changes:   
	              ----------
	              diff:
	                  --- 
	                  +++ 
	                  @@ -23,7 +23,7 @@
	                       nopreempt           
	                       interface eth2          
	                       mcast_src_ip 10.2.86.76
	                  -    virtual_router_id 76    
	                  +    virtual_router_id 118    
	                       priority 120          
	                       advert_int 1          
	                       authentication {
	----------
	          ID: keepalived-service
	    Function: service.running
	        Name: keepalived
	      Result: True
	     Comment: Service reloaded
	     Started: 08:06:44.278083
	    Duration: 91.662 ms
	     Changes:   
	              ----------
	              keepalived:
	                  True
	
	Summary for 10.2.86.76
	------------
	Succeeded: 3 (changed=2)
	Failed:    0
	------------
	Total states run:     3
	Total run time:   1.513 s

在minion上查看配置文件，相关的变量参数，都是根据系统的pillar进行自定义配置的。

	! Configuration File for keepalived
	
	global_defs {
	   notification_email { 
	     acassen@firewall.loc
	   }
	   notification_email_from Alexandre.Cassen@firewall.loc  
	   smtp_server 127.0.0.1     
	   smtp_connect_timeout 30    
	   router_id 76 
	}
	
	vrrp_script chk_mysql_port {     
	    script "/opt/chk_mysql.sh"   
	    interval 2           
	    weight -5            
	    fall 2             
	    rise 1             
	}
	
	vrrp_instance VI_1 {
	    state master
	    nopreempt           
	    interface eth2          
	    mcast_src_ip 10.2.86.76
	    virtual_router_id 118    
	    priority 120          
	    advert_int 1          
	    authentication {
	        auth_type PASS 
	        auth_pass 1111 
	    }
	    virtual_ipaddress {
	        10.2.86.78/26
	    }
	   # track_script {  
	   #     chk_mysql_port
	   # }
	}

