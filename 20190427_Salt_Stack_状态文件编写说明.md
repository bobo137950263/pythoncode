# SLS编写规范
---
## 规范要点说明

首先，状态的执行不可回滚，执行完了就是执行完了，并不会中断回滚，其次，状态的执行，可以反复执行，也就是说一个状态文件，可以多次来进行调用。

在编写状态文件过程中，有以下几点需要注意的:

 - 在一个sls状态文件中，任务ID必须要唯一，也许在一个sls状态文件中，有多个任务，但是要保证每个任务的ID必须是唯一的，最好的是能做到整个状态文件执行的时候，是唯一的；因为在进行状态间关系判断的时候，都是基于模块+任务ID的方式进行判断的，并不会判断到该模块下的方法；
 - 在同一个任务ID下，一个模块，只能调用一次，不允许出现多次，虽然一个模块下有多个方法，但是也只能调用一次该模块，进而就是说只能使用该模块的一种方法；
 - 严格按照YAML的格式，编写状态文件；
 - 尽量将一个多功能的整体模块，拆分成多个专用专用功能的单独模块，保证每个状态文件，只是单一的实现某一个功能，在其他的时候能够进行相互调用；
 - 按照应用程序和功能不同，层次化的组织功能状态文件和模块。

下面就说一下在状态文件中的几个部分。

### 程序安装pkg

	[root@master /srv/salt/base/web/apache]# cat apache.sls 
	apache-installed:
	  pkg.installed:
	    - names:
	      - httpd
	      - httpd-devel

这是一个简单的apache安装的状态模块，其中：

- **apache-installed**：就是这个状态文件的一个任务ID，唯一代表这个任务的，自定义随便编写，只是要能代表这个任务就行，没有什么特殊的含义。
- **pkg.installed**：是指调用pkg模块下的installed方法，这个和python中的模块调用方式一样的，使用.来进行选择。
- 第三行开始，是一个字典的值，-names表示安装的参数，属性值，和后面组成的一个列表，name是键，列表是值，值是httpd和httpd-devel。

其实在状态文件的编写过程中，可以直接将names里面的字段就直接写成任务ID，由于上面的是一下安装两个软件，所以就可以写成两段。如下所示：

	httpd:
	  pkg.installed
	httpd:
	  pkg.installed

这个看上去就很简单，两个任务，组成一个状态文件，每个任务都是调用的pkg模块的installed方法。任务ID+模块，形成一个字典，而在模块里面，可以是列表，可以是字典，也可以直接就是值。

常用的模块有三个，pkg、file和service模块。一般在部署的时候都会用到这三个模块，分别对应的是软件安装、配置文件管理、状态服务管理，提供的功能都是单独的，所以在编写的时候，尽量将三个模块分开来写。

### 文件管理file

文件管理模块，在软件配置管理中很有用，通常就是将一些通用性的文件，放在master上，然后直接分发到所有相关的minion上，比普通的cp高效的多，salt-cp可以直接将master上的指定文件（不能是文件目录）拷贝到minion上，file文件管理，也只能对文件进行操作，不能对目录进行操作，对目录的操作，还是用scp等相关命令来操作吧。

对于httpd服务，最关键的文件，就是/etc/httpd/conf/httpd.conf文件，一个基本的file文件管理模块，就是在master上的存放一个httpd.conf文件，然后制定给其他minion。

	apache-file:
	  file.managed:
	    - name: /etc/httpd/conf/httpd.conf
	    - source: salt://files/web/apache/httpd.conf
	    - backup: minion
		- user: root
		- group: root
		- mode: 644

上面就是编写的一个apache配置文件管理的状态文件：

- **apache-file**：是该状态模块的任务ID
- **file.managed**：是指调用file模块中的managed方法，下面的都是该方法需要用到的参数，以字典的形式传参进去
- **name**：表示的是该文件要存放在minion的路径，可以和任务ID通用，可以直接将name后面的值作为任务ID
- **source**：表示的该文件，在master上存放的位置，其中salt://是固定格式，代指的是该状态文件所处的环境env，也就是base或者是prod对应的file_root目录，这里是base环境，所以使用的目录是/srv/base，后面的路径就是在该目录下的路径
- **root和group**：表示该文件的属主和属组，权限的定义
- **mode**：是指该文件的权限，644是一般文件的普通权限
- **backup**：表示的是在minion上，对更新前的文件进行备份，备份的路径在/var/cache/salt/minion下

以上就是一个简单的文件管理的模块，使用该模块，就能将master上的文件，传递到指定的minion上。

### 服务管理service

在有了程序安装和配置文件管理之后，剩下的就是对程序的运行进行定义了，无非就是开机是否启动，现在是否运行等相关的配置。

	apache-service:	
	  service.running:
	    - name: httpd
	    - enable: True
	    - reload: True


- **apche-service**:表示的是该任务的任务ID
- **service.running**：表示的是调用service模块，running 方法，下面的都是该方法需要的参数
- **name**：表示该服务的名称，是在/etc/init.d/下的软连接名称，也就是service名称，意思是启动该服务
- **enable**：表示该服务开机启动
- **reload**：当出现要求时，reload该服务，如果不定义该字段，要求是重启该服务，restart


### 状态间关系

在之前定义的那些状态模块之间，有些状态模块，是要依赖于其他状态模块的执行，或者根据其他状态模块的变更，影响本模块的执行。模块状态之间的关系，主要有以下的几种：

- Require：本模块的执行，需要其他状态模块已经执行完成，比如服务状态模块的运行，需要先有程序安装状态
- require_in：本模块的执行，被其他状态模块执行所依赖，和require是一个相反的关系
- watch：监控，本模块的执行，监控其他状态模块是否执行，如果其他状态模块出现变更，对应的要按照本状态模块定义的方式，执行本状态模块
- watch_in：被模块的执行，被其他状态模块所监控，本状态模块的执行，会影响其他状态模块
- include：包含，在本状态模块中，包含了其他的状态模块，按照顺序，执行其他的状态模块，新更新的saltstack中不再按照状态模块的编写顺序来执行，只要有，就可以
- unless：除非，只有当条件状态模块不成立时，才会执行本状态模块，比如软件安装，当软件已经安装时，就不执行软件安装模块，当软件未安装时，才会执行该状态模块
- only：只有当后面的状态成立时，才会执行本状态模块

因为有以上的几种状态间关系，按照状态模块编写的规范，将一个apache的安装、配置和服务管理，分别拆分成三个状态模块，然后用一个状态模块include这三个状态模块，在执行的时候，只要执行这一个状态模块就可以了。

所以，一个apache的安装、配置和启动过程，可以编写成如下的状态文件。

	[root@master ~]# cd /srv/salt/base/
	[root@master /srv/salt/base]# ls
	files  web
	[root@master /srv/salt/base]# cd web/
	[root@master /srv/salt/base/web]# ls
	apache-configuration-file.sls  apache-install.sls  apache_new.sls  apache-service.sls  apache.sls
	[root@master /srv/salt/base/web]# cat apache-install.sls 
	apache-install:
	  pkg.installed:
	    - names:
	      - httpd
	      - httpd-devel
	[root@master /srv/salt/base/web]# cat apache-configuration-file.sls 
	apache-configuration-file:
	  file.managed:
	    - name: /etc/httpd/conf/httpd.conf
	    - source: salt://files/web/apache/httpd.conf
	    - backup: minion
	    - user: root
	    - group: root
	    - mode: 644
	[root@master /srv/salt/base/web]# cat apache-service.sls 
	apache-service:
	  service.running:
	    - name: httpd
	    - enable: True
	    - reload: True
	    - require:
	      - pkg: apache-install
	      - file: /etc/httpd/conf/httpd.conf
	    - watch:
	      - file: /etc/httpd/conf/httpd.conf

include文件如下。最后要执行的状态文件，也就是这个web.apache，因为是要和base路径相比，所以写全路径。：

	[root@master /srv/salt/base/web]# cat apache.sls
	include:
	  - web.apache-install
	  - web.apache-configuration-file
	  - web.apache-service

开始直接调用该状态模块。

	[root@master /srv/salt/base/web]# salt '192.168.64.151' state.sls web.apache test=True
	192.168.64.151:
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd
	      Result: None
	     Comment: The following packages would be installed/updated: httpd
	     Started: 17:36:45.757830
	    Duration: 1100.791 ms
	     Changes:   
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd-devel
	      Result: None
	     Comment: The following packages would be installed/updated: httpd-devel
	     Started: 17:36:46.858907
	    Duration: 36.992 ms
	     Changes:   
	----------
	          ID: apache-configuration-file
	    Function: file.managed
	        Name: /etc/httpd/conf/httpd.conf
	      Result: None
	     Comment: The file /etc/httpd/conf/httpd.conf is set to be changed
	     Started: 17:36:46.903774
	    Duration: 53.369 ms
	     Changes:   
	----------
	          ID: apache-service
	    Function: service.running
	        Name: httpd
	      Result: None
	     Comment: Service httpd not present; if created in this state run, it would have been started
	     Started: 17:36:46.962406
	    Duration: 23.148 ms
	     Changes:   
	
	Summary for 192.168.64.151
	------------
	Succeeded: 4 (unchanged=4)
	Failed:    0
	------------
	Total states run:     4
	Total run time:   1.214 s
	[root@master /srv/salt/base/web]# 

直接运行

	[root@master /srv/salt/base/web]# salt '192.168.64.151' state.sls web.apache
	192.168.64.151:
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd
	      Result: True
	     Comment: The following packages were installed/updated: httpd
	     Started: 18:23:04.089367
	    Duration: 4671.199 ms
	     Changes:   
	              ----------
	              httpd:
	                  ----------
	                  new:
	                      2.4.6-88.el7.centos
	                  old:
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd-devel
	      Result: True
	     Comment: The following packages were installed/updated: httpd-devel
	     Started: 18:23:08.838010
	    Duration: 4121.905 ms
	     Changes:   
	              ----------
	              httpd-devel:
	                  ----------
	                  new:
	                      2.4.6-88.el7.centos
	                  old:
	----------
	          ID: apache-configuration-file
	    Function: file.managed
	        Name: /etc/httpd/conf/httpd.conf
	      Result: True
	     Comment: File /etc/httpd/conf/httpd.conf updated
	     Started: 18:23:12.968319
	    Duration: 128.822 ms
	     Changes:   
	              ----------
	              diff:
	                  --- 
	                  +++ 
	                  @@ -39,7 +39,7 @@
	                   # prevent Apache from glomming onto all bound IP addresses.
	                   #
	                   #Listen 12.34.56.78:80
	                  -Listen 80
	                  +Listen 8080
	                   
	                   #
	                   # Dynamic Shared Object (DSO) Support
	----------
	          ID: apache-service
	    Function: service.running
	        Name: httpd
	      Result: True
	     Comment: Service httpd has been enabled, and is running
	     Started: 18:23:14.481901
	    Duration: 275.229 ms
	     Changes:   
	              ----------
	              httpd:
	                  True
	
	Summary for 192.168.64.151
	------------
	Succeeded: 4 (changed=4)
	Failed:    0
	------------
	Total states run:     4
	Total run time:   9.197 s

在minion上能够查看到master的文件信息，已经本地备份的配置文件信息。

	[root@Cobbler-client minion]# tree
	.
	├── accumulator
	├── extmods
	├── file_backup
	│   └── etc
	│       └── httpd
	│           └── conf
	│               ├── httpd.conf_Mon_Apr_22_10:38:47_860981_2019
	│               ├── httpd.conf_Mon_Apr_22_10:44:09_456547_2019
	│               ├── httpd.conf_Mon_Apr_22_10:44:29_386093_2019
	│               └── httpd.conf_Sun_May_05_18:23:13_095365_2019
	├── files
	│   └── base
	│       ├── files
	│       │   └── web
	│       │       └── apache
	│       │           └── httpd.conf
	│       └── web
	│           ├── apache-configuration-file.sls
	│           ├── apache-install.sls
	│           ├── apache_new.sls
	│           ├── apache-service.sls
	│           └── apache.sls
	├── highstate.cache.p
	├── proc
	└── sls.p
	
	13 directories, 12 files

	[root@Cobbler-client minion]# netstat -ltnp
	Active Internet connections (only servers)
	Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
	tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      6743/sshd           
	tcp6       0      0 :::8080                 :::*                    LISTEN      8504/httpd          
	tcp6       0      0 :::22                   :::*                    LISTEN      6743/sshd           
	[root@Cobbler-client minion]# 

可以尝试将配置文件修改，然后重新执行该状态。观察日志输出，可以看到minion上面的状态变化。
	
	[root@master /srv/salt/base/web]# salt '192.168.64.151' state.sls web.apache
	192.168.64.151:
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd
	      Result: True
	     Comment: All specified packages are already installed
	     Started: 18:33:05.818647
	    Duration: 938.056 ms
	     Changes:   
	----------
	          ID: apache-install
	    Function: pkg.installed
	        Name: httpd-devel
	      Result: True
	     Comment: All specified packages are already installed
	     Started: 18:33:06.756942
	    Duration: 22.211 ms
	     Changes:   
	----------
	          ID: apache-configuration-file
	    Function: file.managed
	        Name: /etc/httpd/conf/httpd.conf
	      Result: True
	     Comment: File /etc/httpd/conf/httpd.conf updated
	     Started: 18:33:06.782167
	    Duration: 61.853 ms
	     Changes:   
	              ----------
	              diff:
	                  --- 
	                  +++ 
	                  @@ -39,7 +39,7 @@
	                   # prevent Apache from glomming onto all bound IP addresses.
	                   #
	                   #Listen 12.34.56.78:80
	                  -Listen 8080
	                  +Listen 80
	                   
	                   #
	                   # Dynamic Shared Object (DSO) Support
	----------
	          ID: apache-service
	    Function: service.running
	        Name: httpd
	      Result: True
	     Comment: Service reloaded
	     Started: 18:33:06.895152
	    Duration: 79.117 ms
	     Changes:   
	              ----------
	              httpd:
	                  True
	
	Summary for 192.168.64.151
	------------
	Succeeded: 4 (changed=2)
	Failed:    0
	------------
	Total states run:     4
	Total run time:   1.101 s
	[root@master /srv/salt/base/web]# 

可以看到，minion上的httpd服务是执行的reload。然后在minion上就可以查看到该服务现在监听的端口，已经发生了变化。

	[root@Cobbler-client minion]# netstat -ltnp
	Active Internet connections (only servers)
	Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
	tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      6743/sshd           
	tcp6       0      0 :::80                   :::*                    LISTEN      8504/httpd          
	tcp6       0      0 :::22                   :::*                    LISTEN      6743/sshd           
	[root@Cobbler-client minion]# 
