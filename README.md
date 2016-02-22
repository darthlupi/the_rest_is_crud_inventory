# the_rest_is_crud_inventory
This project is a combination of the following projects 
  * ajaxCRUD by http://www.loudcanvas.com,
  * MySQL-CRUD-API by https://www.leaseweb.com
  * ansible python module
  
The idea is to create a web based inventory that is modifiable from a web interface or from REST calls.
I also have created python scripts that will validate health and configuration via ssh and ansible facts.
These functions are still a little crude, but they can be found in the scripts directory.

Setup:

1. Install a LAMP server.
2. Move the contents of this project to your web server's document root, or create your own VirtualHost for this little application.
3. Create a database with what ever name you choose.
4. Create the following table within that database:

DROP TABLE IF EXISTS `servers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `servers` (
  `primary_ip` varchar(15) DEFAULT NULL,
  `idrac_ip` varchar(15) DEFAULT NULL,
  `os_version` varchar(99) DEFAULT NULL,
  `status` varchar(25) DEFAULT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `application` varchar(50) DEFAULT NULL,
  `contact` varchar(99) DEFAULT NULL,
  `hostname` varchar(25) DEFAULT NULL,
  `groups` varchar(999) DEFAULT NULL,
  `comments` varchar(999) DEFAULT NULL,
  `location` varchar(25) DEFAULT NULL,
  `environment` varchar(25) DEFAULT NULL,
  `builder` varchar(60) DEFAULT NULL,
  `manufacturer` varchar(99) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`)
) ENGINE=MyISAM AUTO_INCREMENT=3377 DEFAULT CHARSET=latin1;

5. Grant all privileges to the table to what ever username you choose identified by what ever password you choose.
6. Configure your database and login information in these two places:
  a. inventory/preheader.php
  b. api/api.php at the END of the file
7. I have fun python script that will take a csv and list of columns as input to populate the table.  
  a.  Example to load csv:  scripts/inventory_pop.py  --infile="file.csv" --columns="host,ip,ilo"
  b.  Example to load host using anisble facts: scripts/inventory_pop.py  --infile="file.lst" --ansible="yes"
