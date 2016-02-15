<?php

	require_once('./preheader.php'); // <-- this include file MUST go first before any HTML/output
	include ('./ajaxCRUD.class.php'); // <-- this include file MUST go first before any HTML/output
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	</head>
<?php
    //"primary_ip","idrac_ip","os_version","status","id","application","contact","hostname","groups","comments"
    $tbl_inv = new ajaxCRUD("inventory", "servers", "id", "./");
    $tbl_inv->omitPrimaryKey();
    $tbl_inv->displayAs("hostname", "Hostname");
    $tbl_inv->displayAs("primary_ip", "Primary IP");
    $tbl_inv->displayAs("os_version", "OS Version");
    $tbl_inv->displayAs("location", "Location");
    $tbl_inv->displayAs("application", "Application");
    $tbl_inv->displayAs("status", "Status");
    $tbl_inv->displayAs("contact", "Contact");
    $tbl_inv->displayAs("comments", "comments");    
    $tbl_inv->displayAs("idrac_ip", "IDRAC/ILO IP");    
    //Order the fields will be displayed in...
    $tbl_inv->orderFields("hostname","primary_ip","location");
    #$tbl_inv->setTextareaHeight('fldLongField', 100);
    

    $allowableValues = array("Available", "Connected with Errors", "Unreachable");
    $tbl_inv->defineAllowableValues("status", $allowableValues);
    $tbl_inv->defineAllowableValues("location", array("Johns Creek","Lorain") );

    //set field fldCheckbox to be a checkbox
    #$tbl_inv->defineCheckbox("fldCheckbox", "1", "0");

    $tbl_inv->setLimit(50);
    //Filters
    //$tbl_inv->addAjaxFilterBox('hostname');
    //$tbl_inv->addAjaxFilterBox('application');
    //$tbl_inv->addAjaxFilterBox('location');
    $tbl_inv->addAjaxFilterBoxAllFields();
    //CSV Export enabled
    $tbl_inv->showCSVExportOption();
    #Cool formating if you want it
    #$tbl_inv->formatFieldWithFunction('hostname', 'makeBlue');
    echo "<h2>MST IFS Linux Inventory</h2>\n";
    $tbl_inv->showTable();

    echo "<br /><hr ><br />\n";

    function makeBold($val){
	return "<b>$val</b>";
    } 

    function makeBlue($val){
	return "<span style='color: blue;'>$val</span>";
    }

?>
