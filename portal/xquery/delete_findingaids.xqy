for $d in fn:doc()
return xdmp:document-delete(fn:document-uri($d))
