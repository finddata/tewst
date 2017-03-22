#!/usr/bin/env perl
require "/usr/cadtools/bin/modules.dir/module.pm" ;
require '../lib/html_utils.pl';
BEGIN {
    push (@INC,"../lib");	
    push (@INC,"../lib/GraphUtils/lib");
}
use CGI qw/:all/;
use CGI ':cgi-lib';
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
require '../lib/html_utils.pl';
#use encryption;
use DBI;
use Net::LDAP;
use POSIX;
use Date::Format;
use Switch;
use Data::Dumper;
# Datagen package for XML dump for graphs
#use Graph_DataGen;
use Date::Parse;
# Use Plotter
#use Plotter::InitCharts;
use Getopt::Long;
my $site;
GetOptions("site=s" => \$site)
    or die "Error in command line arguments\n";
    if($site eq ''){
      $site = 'Bangalore';
    }
defined $site
   or die "usage: $0 site_name\n";
my %site_map = (
    Bangalore  => [ qw(rsdb_bangalore_current) ],
    Norwood    => [ qw(rsdb_norwood_current) ],
    Wilmington => [ qw(rsdb_wilmington_current) ],
    Limerick   => [ qw(rsdb_wilmington_current) ],
);

### Loading rs moudule for web
&module("load rs");
# Warnings and Strict are commented due to some strange behaviour of hashes
use CGI qw/:all/;
use CGI ':cgi-lib';
use CGI::Carp qw(fatalsToBrowser);
use DBI;
### Global Variables
$GLOBAL{'CURRENT_PAGE'} = self_url;
$GLOBAL{'HOME'} = $GLOBAL{'CURRENT_PAGE'};
$GLOBAL{'HOME'} =~s/\?.*//;
my %GLOBAL =();
$GLOBAL{'CONTACT_SUPPORT'} = 'bhargav.bhat@analog.com';
$GLOBAL{'CURRENT_PAGE'} = self_url;
$GLOBAL{'HOME'} = $GLOBAL{'CURRENT_PAGE'};
$GLOBAL{'HOME'} =~s/\?.*//;

# Get all the CGI variables into a single hash
my $CGI_params = Vars;
my %CGI_PARAM  = %$CGI_params;

%MACHINE_DATA=();
##function calls
ShowHeader();

ShowContents();

### Header ###
sub ShowHeader {  
	print "Content-type: text/html\n\n";

	my $message = "<BR><i> Data served by $Mode, Refresh the page to see latest information</i><BR>";   
print <<HEADER;
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<center><title>RS Dash-Board</title></center>
		</head> 
		<head>
	<link rel="stylesheet" type="text/css" href="../lib/DataTables/media/css/jquery.dataTables.css"> 
       		<link rel="stylesheet" type="text/css" href="../lib/DataTables/examples/resources/syntax/shCore.css">
		<script language="javascript" type="text/javascript" src="../lib/flot/current/jquery.js"></script>
		<script type="text/javascript" language="javascript" src="../lib/DataTables/media/js/jquery.dataTables.js"></script>
		<script type="text/javascript" language="javascript" src="../lib/DataTables/examples/resources/syntax/shCore.js"></script>
		<script type="text/javascript" language="javascript" src="../lib/DataTables/examples/resources/demo.js"></script>
		<script type="text/javascript" language="javascript" src="../lib/DataTables/extensions/ColVis/js/dataTables.colVis.js"></script>         
		<script type="text/javascript" language="javascript" src="../lib/DataTables/extensions/TableTools/js/dataTables.tableTools.js"></script>               
		 <script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.js"></script>
	<!--	 <script language="javascript" type="text/javascript" src="  ../lib/flot/current/demo_table.css"></script> -->
        		 <script language="javascript" type="text/javascript" src="  ../lib/new_style.css"></script>

		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.categories.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.pie.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.stack.js"></script>
		<script language="javascript" type="text/javascript" src=" ../lib/flot/current/jquery.flot.axislabels.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.resize.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.tooltip.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.flot.navigate.js "></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/date.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.dataTables.min.js"></script>
		<script language="javascript" type="text/javascript" src="  ../lib/flot/current/jquery.validate.js"></script>
		<script language="javascript" type="text/javascript" src="../lib/flot_test.js"></script>
		<script language="javascript" type="text/javascript" src="../lib/flot.js"></script>
	<link rel="stylesheet" type="text/css" href="../lib/stylesheet.css">
		<link rel="stylesheet" type="text/css" href="../lib/DataTables/media/css/jquery.dataTables.css"> 
	<link rel="stylesheet" type="text/css" href="../lib/DataTables/examples/resources/syntax/shCore.css">
	<!--	<link rel="stylesheet" type="text/css" href=" ../lib/mystyle.css">-->
	<!--	<link rel="stylesheet" type="text/css" href="../lib/DataTables/extensions/ColVis/css/dataTables.colVis.css"> 
		<link rel="stylesheet" type="text/css" href="../lib/DataTables/extensions/TableTools/css/dataTables.tableTools.css"> -->
	<!--	<link rel="stylesheet" type="text/css" href="../etc/css/styles.css" /> -->


		<script type="text/javascript" language="javascript" src="../lib/DataTables/examples/resources/syntax/shCore.js"></script>
		<script type="text/javascript" language="javascript" src="../lib/DataTables/examples/resources/demo.js"></script>

		<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
		<META HTTP-EQUIV="Expires" CONTENT="-1">

		
		</head>
HEADER
}
## mysq connect ###
sub connect {
	$host     = "devgam.spd.analog.com";
	$database = "rsdb_bangalore_current" ;
	$user     = "db_cad" ;
	$pw       = "Cad123";

	my $dsn = "DBI:mysql:host=$host";
	my $dbh = DBI->connect($dsn, $user, $pw) ||
		die "ERROR: can't connect to database server\n";
	return $dbh;
		$host     = "devgam.spd.analog.com";
	$database = "rsdb_norwood_current" ;
	$user     = "db_cad" ;
	$pw       = "Cad123";

	my $dsn = "DBI:mysql:host=$host";
	my $dbh = DBI->connect($dsn, $user, $pw) ||
		die "ERROR: can't connect to database server\n";
	return $dbh;
		$host     = "devgam.spd.analog.com";
	$database = "rsdb_wilmington_current" ;
	$user     = "db_cad" ;
	$pw       = "Cad123";

	my $dsn = "DBI:mysql:host=$host";
	my $dbh = DBI->connect($dsn, $user, $pw) ||
		die "ERROR: can't connect to database server\n";
	return $dbh;
		$host     = "devgam.spd.analog.com";
	$database = "rsdb_limerick_current" ;
	$user     = "db_cad" ;
	$pw       = "Cad123";

	my $dsn = "DBI:mysql:host=$host";
	my $dbh = DBI->connect($dsn, $user, $pw) ||
		die "ERROR: can't connect to database server\n";
	return $dbh;
}
### contents###
sub ShowContents {
	my @arr = @{$site_map{$site}};
  	header_page($arr[0]);
	pend_reasons_desc($arr[0]);
	ShowBhappy($arr[0]);
	#print "$sql_new_time \n";
	#print "Site=$site_selected";	   
	#pending_running_partition($arr[0]);
	job_type($arr[0]);
	machine_status($arr[0]);
	ShowBqueues($arr[0]);
	ShowBload($arr[0]);
 	print_overall_summary($arr[0]);  
}

#### printing overall ussage #####
sub machine_status
{
 	 my $str= shift;
 	# print "****$str\n****";
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	#my $stmt = "select * from machine_status where site=\"$site_selected\" order by time desc limit 1;";
	my $stmt="select distinct * from machine_status;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not in7sert_machine data";
	if(my @columns = $sth->fetchrow_array() ) {
		for(my $i=0;$i<@columns;$i++) {
			if($i==0 )
			{
				$sql_time=$columns[$i];
				next;

			} 		  
			$MACHINE_DATA{$i}{'align'} = 'center';		  
			$MACHINE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
		}	    
	}
}

### function for computing the job type###
sub job_type
{
	my $str = shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	#my $stmt = "select * from  job_status where time=$sql_time and site=\"$site_selected\";";
	my $stmt="select distinct* from job_status order by time desc ;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not in7sert_job_type data";
	while(my @columns = $sth->fetchrow_array() ) {
		for(my $i=0;$i<@columns;$i++) {
			if($i==0 )
			{
				next;

			} 
			if($i==2)
			{		  
				$JOB_DATA_pend{$columns[1]} = "$columns[$i]";		
			}
			if($i==3)
			{		  
				$JOB_DATA_run{$columns[1]} = "$columns[$i]";		
			}

			}	    

	}

	$sth->finish;
	$DBH->disconnect();
}



sub header_page
{
my $str=shift;
print "		<table nosave=\"\" border=\"0\" cols=\"2\" width=\"100%\"> \n";                              
print "		<tbody> \n";
print "		<tr style=\"font-weight: bold;\" > \n";         
print "		<td style=\"border:none\"><img alt=\"\" src=\"../adi_images/ADI_Logo_AWP.png\" style=\"width: 200px; height: 60px;\"></td> \n";
print "	        <td style=\"border:none; width: 60%; height: 60px;\"> <font size=\"8\"><center> RS DashBoard</center></td> \n";
print "<td style=\"border:none; width: 800px;align:right\"> \n";
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	#my $stmt = "select distinct site from summary;";
	my $stmt="select * from summary;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not in7sert_header data";
	while (my @columns = $sth->fetchrow_array() ) {
		for(my $i=0;$i<@columns;$i++) {
			#print "*** $columns[$i] \n";
                      if($columns[$i] =~/^\s*$/)
                       {
                           next;
		      }
                     else
                     {
			push(@values,$columns[$i]);
                     # print "** $columns[$i] \n";
                     }
}
 }	    

print start_form();

print " <br> &nbsp<B>Site</B> &nbsp";
$site_selected="bangalore";
#@values=@columns;
my @values = ('Bangalore', 'Norwood','Wilmington','Limerick');
print popup_menu(
       -name    => 'popup1',
       -values  => \@values,
       -default => 'value2'
         );
print "&nbsp &nbsp &nbsp &nbsp &nbsp  ";
print hidden(-name =>"view",
      -value => $CGI_PARAM{'view'});  
print submit('submit');
print end_form;

 $site_selected = $CGI_PARAM{'popup1'};
if($site_selected =~ /^\s*$/)
{

$site_selected="Bangalore";
}

print "	</td></tr> \n";

print "</tbody> \n";
print "</table> \n";


}

sub print_overall_summary  
{

 	 my $str = shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	my $stmt="select distinct * from summary order by time desc ;";
	#my $stmt = "select * from summary where site=\"$site_selected\" order by time desc limit 1;;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not in7sert_overall_summarydata";
	print "<script language=\"javascript\" type=\"text/javascript\"> \n"; 
	print "\$(document).ready(function(){ \n";
	%TABLE_DATA =();        
	while (my @columns = $sth->fetchrow_array() ) {
		my %TABLE_DATA =();        
		for(my $i=0;$i<@columns;$i++) {
			if($i==0 )
			{
				$sql_time=$columns[$i];
				next;

			} 		  
			$TABLE_DATA{$i}{'align'} = 'center';		  
			$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
		}
		$cpu_in_use=$TABLE_DATA{6}{'ENTRY'}-$TABLE_DATA{7}{'ENTRY'}-$TABLE_DATA{8}{'ENTRY'}-$TABLE_DATA{9}{'ENTRY'};
		$free_cpu_slots=$TABLE_DATA{3}{'ENTRY'};
		print "var data_cpu = [[\"Free \($free_cpu_slots\)\",\"$free_cpu_slots\"],\
				       [\"Used \($TABLE_DATA{4}{'ENTRY'}\)\",\"$TABLE_DATA{4}{'ENTRY'}\"]] \n";
		$used_cpu_load=$TABLE_DATA{1}{'ENTRY'};
		$free_cpu_load=100-$used_cpu_load;
		$load_average=$TABLE_DATA{6}{'ENTRY'};
		$cpu_util= "$TABLE_DATA{2}{'ENTRY'} %";
		$slots_used=$TABLE_DATA{4}{'ENTRY'};
		$slots_max=$TABLE_DATA{4}{'ENTRY'};
		$total_machines=$TABLE_DATA{1}{'ENTRY'};	    
		$total_cpu_slots=$free_cpu_slots+$TABLE_DATA{4}{'ENTRY'};

		print "var data_load = [[\"Used Cpu Load\",$used_cpu_load],[\"Free Cpu Load\",$free_cpu_load]]; \n";
		
		
		print "var data_running=[[\"Adice \($JOB_DATA_run{$feature}\)\",$TABLE_DATA{5}{'ENTRY'}],\
					 [\"Incisive \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{5}{'ENTRY'}],\
				         [\"Spectre \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLEL_DATA{5}{'ENTRY'}],\
					 [\"Vcs \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{5}{'ENTRY'}],\
					 [\"Calibre \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{5}{'ENTRY'}],\
                                         [\"Others \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{5}{'ENTRY'}]] \n";
               print "var data_pending=[[\"Adice \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{4}{'ENTRY'}],\
					 [\"Incisive \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{4}{'ENTRY'}],\
				         [\"Spectre \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLEL_DATA{4}{'ENTRY'}],\
					 [\"Vcs \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{4}{'ENTRY'}],\
					 [\"Calibre \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{4}{'ENTRY'}],\
                                         [\"Others \($TABLE_DATA{1}{'ENTRY'}\)\",$TABLE_DATA{4}{'ENTRY'}]] \n";

    
=d                                     
		print "var data_running=[[\"Queue Name \($JOB_DATA_run{5}{'ENTRY}\)\",$JOB_DATA_run{5}{'ENTRY'}],\
					 [\"Incisive \($JOB_DATA_run{incisive}\)\",$JOB_DATA_run{incisive}],\
					[\"Spectre \($JOB_DATA_run{spectre}\)\",$JOB_DATA_run{spectre}],\
					 [\"Vcs \($JOB_DATA_run{vcs}\)\",$JOB_DATA_run{vcs}],\
					 [\"Calibre \($JOB_DATA_run{calibre}\)\",$JOB_DATA_run{calibre}],\
					 [\"Others \($JOB_DATA_run{others}\)\",$JOB_DATA_run{others}]\
 					 ]; \n";
		print "var data_pending=[[\"Adice \($JOB_DATA_pend{adice}\)\",$JOB_DATA_pend{adice}],\
				         [\"Incisive \($JOB_DATA_pend{incisive}\)\",$JOB_DATA_pend{incisive}],\
					 [\"Spectre \($JOB_DATA_pend{spectre}\)\",$JOB_DATA_pend{spectre}],\
					 [\"Vcs \($JOB_DATA_pend{vcs}\)\",$JOB_DATA_pend{vcs}],\
					 [\"Calibre \($JOB_DATA_pend{calibre}\)\",$JOB_DATA_pend{calibre}],\
					 [\"Others \($JOB_DATA_pend{others}\)\",$JOB_DATA_pend{others}]\
					]; \n";
					
=cut

		
		print "var data_machine=[[\"Available \($MACHINE_DATA{1}{'ENTRY'}\)\",$MACHINE_DATA{1}{'ENTRY'}],\
					 [\"Closed \($MACHINE_DATA{2}{'ENTRY'}\)\",$MACHINE_DATA{2}{'ENTRY'}],\
				         [\"Used \($MACHINE_DATA{3}{'ENTRY'}\)\",$MACHINE_DATA{3}{'ENTRY'}],\
					 [\"Busy \($MACHINE_DATA{4}{'ENTRY'}\)\",$MACHINE_DATA{4}{'ENTRY'}],\
					 [\"Reserved \($MACHINE_DATA{5}{'ENTRY'}\)\",$MACHINE_DATA{5}{'ENTRY'}],\
                                         [\"Down \($MACHINE_DATA{6}{'ENTRY'}\)\",$MACHINE_DATA{6}{'ENTRY'}]] \n";
		foreach $feature(keys %JOB_DATA_run)
		{
			$jobs_running +=$JOB_DATA_run{$feature};			
		}		
	}
	$total_machines=`bload | grep lin | wc -l`;
	print   " \n pieChart(\"placeholder30\",data_machine,{title:\"<b><center>Machine Status<center></b>\"});";
	print   " \n pieChart(\"placeholder29\",data_cpu,{title:\"<b><center>CPU Slots</center></b>\"});\n";
	print   " \n pieChart(\"placeholder39\",data_running,{title:\"<b><center>Jobs Running</center></b>\"});\n";
	print   " \n pieChart(\"placeholder41\",data_pending,{title:\"<b><center>Jobs Pending</center></b>\"});\n";
	print "});";
	print "</script>";

##################################################################
	print "		<table style=\"text-align: center; width: 100%; height: 4px;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\"> \n";
	print "		<tbody> \n";
	print "		<tr style=\"font-weight: bold;\" align=\"center\"> \n";
	print "		<td colspan=\"1\" rowspan=\"1\"  style=\"background-color:rgb(135,206,250); height: 38px;\"<center>TIMESTAMP:$sql_new_time <center>SITE:$site_selected</center></td> \n";
	print "		</tr> \n";
	print "		</tbody> \n";
	print "		</table> \n";
#</br><br><br><br><br><br><b>Jobs Running&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp :</b> $jobs_running
	print "<table style=\"border:none;border-color:black;width: 100%;\" border=\"1\"\"> \n";
	print "      <tbody> \n"; 
	print "	<tr> \n";
	print "	  <td colspan=\"1\"> <b>CPU Load Average :</b>$load_average % </td> \n";
	print "	  <td colspan=\"1\"><b>CPU Slot Utilization :</b>$cpu_util  </td> \n";
	print "	  <td colspan=\"1\"><b>Total Machines :</b>$total_machines </td> \n";
	print "	  <td colspan=\"1\"><b>Total CPU Slots:</b> $total_cpu_slots</td> \n";
	print "	  <td colspan=\"1\"><b>Jobs Pending :</b> $jobs_pending </td> \n";
	print "	  <td colspan=\"1\"><b>Jobs Running :</b> $jobs_running </td> \n";
	print "	</tr> \n";
	print "	<tr> \n";
	print "</tbody></table> \n";
	#print "**** $site_selected \n";
	print "<table style=\"border:none;border-color:black;width: 100%;\" border=\"1\"\"> <tbody>\n";
	print " <td colspan=\"1\" style=\"width: 800px;height: 200px;padding-left: 40px;padding-right: 40px;padding-top:0px;padding-bottom: 40px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder29\" ></div> </td>  \n";
	print " <td colspan=\"1\" style=\"width: 800px;height: 200px;padding-left: 40px;padding-right: 40px;padding-top:0px;padding-bottom: 40px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder30\" ></div> </td> \n";
	print " <td colspan=\"1\" style=\"width: 800px;height: 200px;padding-left: 40px;padding-right: 40px;padding-top:0px;padding-bottom: 40px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder39\" ></div> </td> \n";
	print " <td colspan=\"1\"style=\"width: 800px;height: 200px;padding-left: 40px;padding-right: 40px;padding-top:0px;padding-bottom: 40px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder41\" ></div> </td> \n";
	
	print "	</tr> \n";
	print "      </tbody> \n";
	print "    </table>  \n";
	print "<table style=\"border:none;border-color:black;width:100%;\" border=\"1\"\"> <tbody>\n";
	print "<tr> <td style=\"width: 100%;padding-left: 10px;padding-right: 40px;padding-top:0px;padding-bottom: 20px;padding-top: 20px;font-style:x-small;\"> \n";
	print " <div id=\"placeholder28\"; style=\"width:1800px\" ></div></td></tr> \n"; 
	print "</tbody></table></table> \n";
	print "<table style=\"border:none;border-color:black;width:100%;\" border=\"1\"\"> <tbody>\n";
	print " <tr><td style=\"width:100%;padding-left: 10px;padding-right: 40px;padding-top:0px;padding-bottom: 20px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder49\"; style=\"width:1800px\" ></div></td></tr> \n"; 
	print "</tbody></table></table> \n";
	print "<table style=\"border:none;border-color:black;width:100%;\" border=\"1\"\"> <tbody>\n";
	print " <tr><td style=\"width:100%;padding-left: 10px;padding-right: 40px;padding-top:0px;padding-bottom: 20px;padding-top: 20px;\"> \n";
	print " <div id=\"placeholder26\"; style=\"width:1800px\"></div> </td></tr> </tbody></table></table> \n";
}
### Bqueues table ###
sub ShowBqueues {
  	my $str = shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	#my $stmt = "select * from queues where time=$sql_time and site=\"$site_selected\";";
	my $stmt="select distinct * from queues order by time desc ;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not insert data_queues";
	print "<script language=\"javascript\" type=\"text/javascript\"> \n"; 
	print "\$(document).ready(function(){ \n";
	print "var header = [\"Queue Name\",\"Description\",\"Priority\",\"Jobs Pending\",\"Jobs Running\",\"Lallot\",\"Slots Used\",\"Slots Free\",\"Load Avg\",\"Allowed Users\",\"Machines\"];\n";    
	print "var data = [ ";
	%TABLE_DATA =();        
	while (my @columns = $sth->fetchrow_array() ) {
		my %TABLE_DATA =();        
		for(my $i=0;$i<@columns;$i++) {
			next if($i==12||$i==13 );
			if($i==0)
			{				
				#$TABLE_DATA{0}{'align'} = 'center';
				#$TABLE_DATA{0}{'ENTRY'} = "<img src='../lib/DataTables/examples/resources/details_open.png'>";
				next;
			}
			
			if($i==4)
			{
			#$TABLE_DATA{$i}{'align'} = 'center';		  
			#$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";
			$jobs_running += "$columns[$i]";	
				$temp=$columns[2]; 		
			}
			if($i==5)
			{
			
				$jobs_pending += "$columns[$i]";	
				$temp=$columns[2]; 

						#$TABLE_DATA{$i}{'align'} = 'center';		  
#			$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
			}
			if($i==7)
			{

			}
			if($i==6)
			{
				$columns[$i]="$columns[$i]";
			}
			
			
			
			if($i==12)
			{      	 
				$queue_allowed_user{$columns[1]}=$columns[$i];      
				$queue_desc{$columns[1]}=$columns[2];
                                @temp=split("",$columns[$i]);   
                                $temp=@temp;
                                if($temp>0)
                                 {


                                  }
                                 else
                                  {
					$columns[$i]="ALL";

                                  }
                               if($columns[$i]="")
                                  {
                                   $columns[$i]="ALL";
				 }	
			}		  
			$TABLE_DATA{$i}{'align'} = 'center';		  
			$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
		}	    
		&AddTableRow1(\%TABLE_DATA);
		$queue_hash{$columns[1]}=$columns[13];		
	}
	print "];\n";
	#print "\n table(\"placeholder26\",data,{title:\"<BR><font size=20><b><center>RS Machine Status</center></b></font><BR>\",colTitles:header})\n";
	print "\n table(\"placeholder49\",data,{title:\"<BR><font size=20><b><center>RS Queue Status</center></b></font><BR>\",colTitles:header})\n";
	print "  var otable = \$('#placeholder49-table').DataTable({ \n";
	print " retrieve: true, \n";
	print "    }); \n";
	print "\$(\'#placeholder49-table tbody tr\').on(\'click\', \'td:nth-child(1)\', function (f) { \n";
	print "     var tr = \$(this).closest(\'tr\');\n";
	print " var row = otable.row(tr); \n";
	print "\n var js_hash = { ";
	foreach $queue (keys %queue_allowed_user) {
		$counter=0;
                 
		$value="<b>allowed_users/grp(s)</b>:"; 
                $all_flag=0;
                foreach $machine(split(" ",$queue_allowed_user{$queue})) {
                        $all_flag=1;
			$value .="$machine";
			$value .=",";   
			if($counter==10)
			{
				$value .="<BR>";
				$counter=0; 
			}
			$counter++;

		}
                if($all_flag)
                {
                  

                }
               else
               {
                 	$value="<b>allowed_users/grp(s)</b>: ALL"; 

               }
		print "\"$queue\":\"<b>Description :</b> $queue_desc{$queue} <br> $value\",";
		$value="";
	}
	print "}; \n";
	print "var  queue_name=\$( this ).next().text(); \n";
	print "if(f.handled !== true) \n";
	print " { \n";
	print "  f.handled = true; \n";
	print "}\n";
	print "var cell=otable.cell( this ); \n";
	print  "   if (row.child.isShown()) { \n";
	#print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_open.png'>\").draw(); \n";
	print "     row.child.hide(); \n";
	print "    tr.removeClass(\'shown\'); \n";
	print "    } else {l \n";
	print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_close.png'>\").draw(); \n";
	print "    row.child(js_hash[queue_name]).show(); \n";
	print "        tr.addClass(\'shown\'); \n";
	print "     } \n";
	print "  }); \n";
	print "});";
	print "</script>";
}

####Bload Table #####
sub ShowBhappy {
	$str=shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
        #print "*** $site_selected \n";
	$DBH->do("USE $str;");
	my $stmt="select * from users where site=\"$site_selected\" order by time desc";
	#my $stmt="select * from users";
	my $sth = $DBH->prepare( $stmt );
	#$sth->execute() or print "Could not99 insert data";
	if(my @columns = $sth->fetchrow_array())
	{
		$sql_time=$columns[0];

	}
	#my $stmt = "select * from users where time=$sql_time and site=\"$site_selected\";";
	my $stmt="select distinct * from users order by time desc ;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not insert data_Bhappy";
	my $stmt="select from_unixtime(time),userid from users order by time desc";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not99_ShowBhappy insert data";
	if(my @columns = $sth->fetchrow_array())
	{
		$sql_new_time=$columns[0];
	}
	#my $stmt = "select * from users where time=$sql_time and site=\"$site_selected\";";
	my $stmt="select distinct * from users order by time desc ;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not insert data_Bhappy";
	print "<script language=\"javascript\" type=\"text/javascript\"> \n"; 
	print "\$(document).ready(function(){ \n";
	     print "var header = [\"Userid\",\"Groupid\",\"Jobs Running\",\"Jobs Pending\",\"Job Limit\",\"Run Failures\",\"Queue Name\",\"Atp\",\"Pend Reasons\"];\n";
	
	#print "var header = [\"userid\",\"groupid\",\"jobs_running\",\"jobs_pending\",\"job_limit\",\"run_failures\",\"queue_name\",\"atp\",\"pend_reasons\"];\n";

 if($site_selected ne "Bangalore")
     {

	     print "var header = [\"Userid\",\"Groupid\",\"Jobs Running\",\"Jobs Pending\",\"Job Limit\",\"Run Failures\",\"Queue Name\",\"Atp\",\"Pend Reasons\"];\n";
	
     #print "var header = [\"Userid\",\"Groupid\",\"Jobs Running\",\"Jobs Pending\",\"Job Limit\",\"Run Failures\",\"Queue Name\",\"Atp\",\"Pend Reasons\"];\n";
	

}
	print "var data = [ ";
	%TABLE_DATA =();        
	while (my @columns = $sth->fetchrow_array() ) {
		my %TABLE_DATA =();        
		for(my $i=0;$i<@columns;$i++) {
			next if($i==0); 
			if($i==2)
			{

			}
                        

			if($i==3)
			{

			}
			if($i==4)
			{
			}
			if($i==5)
			{
				$jobs_pending += "$columns[$i]";	
				$temp=$columns[2]; 


			}
			if($i==6)
			{
                        }
                        if($i==7)
                        {     
                        }
                        if($i==8)
                        {
                        }
			if($i==9)
			{
				$columns[9]=~s/-//;
				if($columns[9] eq "")
				{
					$pend_reason_hash{$columns[1]}="";

				}
				else
				{

					@temp=split(",",$columns[9]);
					foreach $value (@temp)
					{
						@temp_1=split(":",$value);
						$temp_1[0]=~s/\s+//;
						@temp_2=split("",$temp_1[0]); 
						foreach $value_1 (@temp_2)
						{ 
							$value_1=~s/\s+//;
							if(exists $pend_desc{$value_1} )
							{
								$value_2=$pend_desc{$value_1};
								$pend_reason_hash{$columns[1]} .="$value_1 : $value_2 <br>";
								#$pend_reason_hash{$columns[2]} .="$value_1 : $value_2 <br>";

							}
						}

					}

				}
                       $columns[10]=$columns[9];
                       next;
			} 

			$TABLE_DATA{$i}{'align'} = 'center';		  
			$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
		}

	$TABLE_DATA{11}{'align'} = 'center';
	#$TABLE_DATA{11}{'ENTRY'} = "<img src='../lib/DataTables/examples/resources/details_open.png'>";	
                if($site_selected ne "bangalore")
                {
                 #   delete $TABLE_DATA{2}{'ENTRY'};
	           # delete $TABLE_DATA{2}{'align'} ;			
                }
		&AddTableRow1(\%TABLE_DATA);		
	}
	print "];\n";
	print "\n table(\"placeholder28\",data,{title:\"<BR><font size=20><b><center>RS User Status</center></b></font><BR>\",colTitles:header})\n";
	print "  var otable = \$('#placeholder28-table').DataTable({ \n";
	print " retrieve: true, \n";
	print "    }); \n";
	print "\$(\'#placeholder28-table tbody tr\').on(\'click\', \'td:nth-child(10)\', function (f) { \n";
	print "     var tr = \$(this).closest(\'tr\');\n";
	print " var row = otable.row(tr); \n";
	print "\n var js_hash = { ";
	foreach $user (keys %pend_reason_hash) {
		$counter=0;
		$value="<b>Reasons</b>:<br>"; 
		$value .="$pend_reason_hash{$user}";                      
		print "\"$user\":\"$value\",";
		$value="";
	}
	print "}; \n";
	print "var  queue_name=\$( this ).parent().children(\"td:nth-child(1)\").text();\n";
	print "if(f.handled !== true) \n";
	print " { \n";
	print "  f.handled = true; \n";
	print "}\n";
	print "var cell=otable.cell( this ); \n";
	print  "   if (row.child.isShown()) { \n";
	#print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_open.png'>\").draw(); \n";
	print"row.child.remove();\n";	
	print "     row.child.hide();\n";
	print "    tr.removeClass(\'shown\'); \n";
	print "    } else { \n";
	#print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_close.png'>\").draw(); \n";
	print"row.child.remove();\n";		
	print "    row.child(js_hash[queue_name]).show(); \n";
       	print"row.child(js_hash[queue_name]).dialog(); \n";
	print "        tr.addClass(\'shown\'); \n";
	print "     } \n";
	print "  }); \n";
	print "});";
	print "</script>";

}

sub ShowBload {
 	 my $str = shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");
	#my $stmt = "select * from machines where time=$sql_time and site=\"$site_selected\";";
	my $stmt="select distinct * from machines order by time desc ;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not in9sert_machines data";
	print "<script language=\"javascript\" type=\"text/javascript\"> \n"; 
	print "\$(document).ready(function(){ \n";
	#print "var header = [\"Name\",\"Status\",\"Slots Used\",\"Slots Max\",\"Cpu Util\",\"Paging\",\"Disk\",\"Tmp Space\",\"Num Procs\",\"Speed\",\"Avl Mem\",\"Cpu Steal\",\"Interactive\",\"Reserved Users\",\"Allowed Grps\"];\n";
		print "var header = [\"Name\",\"Status\",\"Slots Used\",\"Slots Max\",\"Cpu Util\",\"Paging\",\"Disk\",\"Tmp Space(Gb)\",\"Num Procs\",\"Speed(GHz)\",\"Avl Mem(Gb)\",\"Cpu Steal\",\"Interactive\",\"Reserved Users\",\"Allowed Grps\"];\n";	
 	if($site_selected ne "Bangalore")
	{
	print "var header = [\"Name\",\"Status\",\"Slots Used\",\"Slots Max\",\"Cpu Util\",\"Paging\",\"Disk\",\"Tmp Space(Gb)\",\"Num Procs\",\"Speed(GHz)\",\"Avl Mem(Gb)\",\"Cpu Steal\",\"Interactive\",\"Reserved Users\",\"Allowed Grps\"];\n";	
	}
	print "var data = [ ";
	%TABLE_DATA =();        
	while (my @columns = $sth->fetchrow_array() ) {
		my %TABLE_DATA =();        
		for(my $i=0;$i<scalar(@columns);$i++) {
			next if($i==16); 
				 if($site_selected ne "Bangalore")
                                 { }
						
			if($i==0)
			{

				#$TABLE_DATA{0}{'align'} = 'center';
				#$TABLE_DATA{0}{'ENTRY'} = "<img src='../lib/DataTables/examples/resources/details_open.png'>";
				next;

			}
			
			if($i==10||$i==11 || $i==8 ||$i==6)
			{
				if($columns[$i] !=0)
				{

					$columns[$i]=sprintf("%.2f",$columns[$i]/1024);

				}

			}
			if($i==5)
			{ 
				$columns[$i]="$columns[$i] %";

			} 
			if($i==16)
			{
				$counter=0; 
				$value="";
				@temp_array=split /\+/, $columns[$i];
				$counter=0;
				foreach $access_grp (@temp_array)
				{

					$value .= "$access_grp ";
				}
				$columns[$i]=$value;
				$reserved_user{$columns[1]}=$value;
				next;
			}
				$TABLE_DATA{$i}{'align'} = 'center';		  
				$TABLE_DATA{$i}{'ENTRY'} = "$columns[$i]";		
			}
				 if($site_selected eq "bangalore")
				{	
				$TABLE_DATA{15}{'align'} = 'center';		  
				$TABLE_DATA{15}{'ENTRY'} = "$columns[15]";
               			}            
               			 $TABLE_DATA{16}{'align'} = 'center';
				$TABLE_DATA{16}{'ENTRY'} = $TABLE_DATA{16}{'ENTRY'};		    
				#$TABLE_DATA{15}{'ENTRY'} = "<img src='../lib/DataTables/examples/resources/details_open.png'>";		    
				&AddTableRow1(\%TABLE_DATA);		
			}
	print "];\n";
	print "\n table(\"placeholder26\",data,{title:\"<BR><font size=20><b><center>RS Machine Status</center></b></font><BR>\",colTitles:header})\n";
	print "  var otable = \$('#placeholder26-table').DataTable({ \n";
	print " retrieve: true, \n";
	print "    }); \n";
	print "\$(\'#placeholder26-table tbody tr\').on(\'click\', \'td:nth-child(15)\', function (f) { \n";
	print "     var tr = \$(this).closest(\'tr\');\n";
	print " var row = otable.row(tr); \n";
	print "\n var js_hash = { ";
	foreach $machine (keys %reserved_user) {
		$counter=0;
		$value="<b>Users</b>:"; 
		foreach $users(split(" ",$reserved_user{$machine})) {
			$value .="$users";
			$value .=",";   
			if($counter==20)
			{
				$value .="<BR>";
				$counter=0; 
			}
			$counter++;

		}
		print "\"$machine\":\"$value\",";
		$value="";
	}
	print "}; \n";
	print "var  queue_name=\$( this ).parent().children(\"td:nth-child(1)\").text();\n";
	print "if(f.handled !== true) \n";
	print " { \n";
	print "  f.handled = true; \n";
	print "}\n";
	print "var cell=otable.cell( this ); \n";
	print  "   if (row.child.isShown()) { \n";
	#print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_open.png'>\").draw(); \n";
  	#print "     row.child.hide();\n";
	print "    tr.removeClass(\'shown\'); \n";
	print "    } else { \n";
	#print "cell.data(\"<img src='../lib/DataTables/examples/resources/details_close.png'>\").draw(); \n";
	print "    row.child(js_hash[queue_name]).show();\n";
	print "        tr.addClass(\'shown\'); \n";
	print "     } \n";
	print "  }); \n";
	print "});";
	print "</script>";
}

####distribution of the pending and running jobs across features########
=d
sub pending_running_partition
{


  	my $str = shift;
	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");

	my $stmt="select distinct * from queues;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not insert data_rp";
	while (my @columns = $sth->fetchrow_array() ) {
		if($columns[2] =~ /adice/i)
		{
					

			$pend_count{adice} +=$columns[4];
			$run_count{adice} +=$columns[5]; 

		}
		elsif($columns[2] =~ /calibre/i)
		{
							
			$pend_count{calibre} +=$columns[4];
			$run_count{calibre} +=$columns[5]; 

		}   
		elsif($columns[2] =~ /vcs/i)
		{
							
			$pend_count{vcs} +=$columns[4];
			$run_count{vcs} +=$columns[5]; 

		}     
		elsif($columns[2] =~ /spectre/i)
		{		
			$pend_count{spectre} +=$columns[4];  
			$run_count{spectre} +=$columns[5]; 
		}       
		elsif($columns[2] =~ /Incisive/i)
		{
						
			$pend_count{incisive} +=$columns[4];
			$run_count{incisive} +=$columns[5]; 
		}     

		else
		{
						
			$pend_count{others} +=$columns[4];
			$run_count{others} +=$columns[5]; 

		}
	}
}
=cut
=d
sub pending_running_partition
{

  	my $str = shift;
  	my @tests=qw/adice calibre vcs spectre Incisive/; 

	$DBH = &connect or die "Cannot connect to the sql server \n";
	$DBH->do("USE $str;");

	my $stmt="select distinct * from queues;";
	my $sth = $DBH->prepare( $stmt );
	$sth->execute() or print "Could not insert data_rp";
	while (my @columns = $sth->fetchrow_array() ) {
	my $found='others';
	for my $w(@tests)
	{
	if($columns[0]=~ /$w/i)
	{
	$found=$w;
	
	
	}
	}
	$pend_Count{$found} +=$columns[3];
	$run_count{$found}  +=$columns[4];
	}
	

}
=cut
sub pend_reasons_desc {
	$pend_desc{A}="Awaiting first dispatch cycle.";                                             
	$pend_desc{a}="Your account is not valid on one or more hosts.";
	$pend_desc{B}="No contact with a potential host.";
	$pend_desc{b}="The specified job begin-time (bsub -b) has not been reached yet.";
	$pend_desc{C}="A potential hosts resources appear desperately low.";
	$pend_desc{c}="A potential host may be dedicated to a single job. See the section";
	$pend_desc{D}="A potential host is reserved for its owner.";
	$pend_desc{d}="An MT host has too few processors available.";
	$pend_desc{E}="A potential host is closed to job placement.";
	$pend_desc{e}="A potential host has too many processing units available";
	$pend_desc{F}="A potential host has insufficient slots available.";
	$pend_desc{f}="The job has failed the bsub -expect test one or more times.";
	$pend_desc{G}="The job wants all slots bsub -x, but some are in use.";
	$pend_desc{g}="User has reached the placed-state job limit (bsub -plim).";
	$pend_desc{H}="The dependency expression for the job evaluated to FALSE.";
	$pend_desc{h}="A host was excluded because the job has been classified as a long-runner.";
	$pend_desc{I}="User has reached USER_JOB_LIMIT of queue.";
	$pend_desc{i}="The host RS daemon has not synchronized (after startup) with";
	$pend_desc{J}="The queue is inactive.";
	$pend_desc{K}="The queue is waiting out the DISPATCH_DELAY.";
	$pend_desc{L}="The job is on the lost&found queue (always inactive.)";
	$pend_desc{l}="The required license(s) are not available.";
	$pend_desc{M}="The jobs PRE_EXEC script returned 1 (No license ?)";
	$pend_desc{N}="The user was restricted (Verdasys) from running on a host.";
	$pend_desc{O}="The queue has reached its job slot limit.";
	$pend_desc{P}="A potential host failed the jobs resource expression (bsub -R.)";
	$pend_desc{Q}="A potential host was excluded by the system.";
	$pend_desc{R}="This letter is not in use at this time";
	$pend_desc{S}="A potential host was excluded because the user is not allowed";
	$pend_desc{T}="A potential host was excluded because it was classified";
	$pend_desc{t}="Job was migrated because the host was thrashing.";
	$pend_desc{U}="User has reached job run limit (bsub -jlim).";
	$pend_desc{V}="A potential host failed the queues resource expression.";
	$pend_desc{W}="The jobs POST_EXEC script returned 1 (No license ?).";
	$pend_desc{X}="A Linux/Intel(or AMD) host was excluded because you did not bsub -lintel";
	$pend_desc{Y}="A host was excluded by bsub -m and/or HOSTS on the queue.";
	$pend_desc{Z}="One or more hosts could not CD to the jobs working directory or one of";
	$pend_desc{z}=" Job failed to start. Perhaps a bad user command,";
}

