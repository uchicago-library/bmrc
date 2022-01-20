import module namespace json = "http://marklogic.com/xdmp/json" at "/MarkLogic/json/json.xqy";
declare namespace xs = "http://www.w3.org/2001/XMLSchema";
declare namespace xsi = "http://www.w3.org/2001/XMLSchema-instance";

declare variable $browse as xs:string external;

(: Get a complete list of collections. :)

let $collections := json:object()
let $_ := for $c in cts:collections()
    return 
        if (fn:starts-with($c, $browse) and $c ne "https://bmrc.lib.uchicago.edu/institutions/BMRC+Portal") 
        then (
            map:put(
                $collections,
                $c,            
                json:array(
                    <json:array>
                        {   
                            for $x in fn:collection($c)
                            return json:array(
                                <json:array> 
                                    <json:value xsi:type="xs:string">{fn:document-uri($x)}</json:value>
                                    <json:value xsi:type="xs:string">{fn:normalize-space(fn:string-join(($x//*:titleproper)[1]/text()))}</json:value>
                                </json:array>
                            )   
                        }   
                    </json:array>
                )   
            )   
        )
        else ()
return $collections
