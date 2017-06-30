<?php
#echo stripslashes($_POST["data"]);
$my_file = 'file.txt';
$handle = fopen($my_file, 'w') or die('Cannot open file:  '.$my_file);
$data = $_POST["data"];
fwrite($handle, $data);
#$python=`python compiler.py test/test.2.5.ml outhtml.asm`;
#echo $python;
#echo exec('python compiler.py test/test.2.5.ml outhtml.asm');
system('python compiler.py file.txt outhtml.asm', $retValue);
#echo stripslashes($retValue);
$homepage = file_get_contents('./outhtml.asm');
echo $hompage;
?>
