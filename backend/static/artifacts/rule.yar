rule Angler : Exploit_Kit
{
  strings:
    $s1 = /60\*60\*24\*7\*1000/
    $s2 = /PHP_SESSION_PHP/
  condition:
    $s1 and $s2
}

