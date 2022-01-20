import module namespace json =
  "http://marklogic.com/xdmp/json"
  at "/MarkLogic/json/json.xqy";

import module namespace search =
  "http://marklogic.com/appservices/search"
  at "/MarkLogic/appservices/search/search.xqy";

declare namespace cts = "http://marklogic.com/cts";
declare namespace ead = "urn:isbn:1-931666-22-9";
declare namespace xs  = "http://www.w3.org/2001/XMLSchema";
declare namespace xsi = "http://www.w3.org/2001/XMLSchema-instance";

declare default function namespace "https://bmrc.lib.uchicago.edu";

(: Get collections for the sidebar :)

(::::::::::::::::::::
  EXTERNAL VARIABLES
 ::::::::::::::::::::)

(: a browse, match facet URIs beginning with this string. :)
declare variable $b as xs:string external;

(: documents to consider- i.e., documents in an existing set of search results. :)
declare variable $docs as json:array external;

(: limit to this number of results. :)
declare variable $limit as xs:integer external;

(: sort results in this way. :)
declare variable $sort as xs:string external;

(:::::::::::
  FUNCTIONS 
 :::::::::::)

declare function get-collection-counts($docs, $collections, $sort, $limit) {
    (: 
       Params
         $docs               - accepting a list of documents is a way for this 
                               function to restrict collection counts to a specific
                               set of search results, without having to execute that
                               search. alternatively, pass in the empty sequence to
                               retrive counts for all documents. (i.e., passing in a
                               sequence of documents to refine an existing
                               search. pass in the empty sequence to start a new search.)
         $collections        - sequence of all collections to consider. the function
                               will only return collections from this sequence.
         $sort               - sort in this way.
         $limit              - limit to this many results.

       Returns
         a JSON array, e.g.:
           [
             [
               "https://bmrc.lib.uchicago.edu/topics/one",
               "one",
               100
             ],
             [
               "https://bmrc.lib.uchicago.edu/topics/two",
               "two",
               50
             ],
             [
               "https://bmrc.lib.uchicago.edu/topics/three",
               "three",
               66
             ]
           ]
       Note
         We can pre-compute collections-map and save it to the database- then
         you can retrieve it like this:

         let $collections-map := map:map(fn:doc('collections-map')/map:map)
       
         This shaves off about .2 seconds. As the database gets bigger is
         precomputing this value more and more important? 
    :)

    let $docs-map := map:new(
        if (fn:empty($docs))
        then
            for $d in fn:doc()
            return map:entry(fn:document-uri($d), fn:true())
        else
            for $d in $docs
            return map:entry($d, fn:true())
    )

    let $collections-map := map:new(
        for $c in $collections
        return map:entry(
            $c,
            map:new(
                for $d in fn:collection($c)
                return map:entry(fn:document-uri($d), fn:true())
            )
        )
    )

    let $collections-sorted :=
        if ($sort eq 'alpha')
        then
            for $c in $collections
            order by $c
            return $c
        else if ($sort eq 'alpha-dsc')
        then
            for $c in $collections
            order by $c descending
            return $c
        else if ($sort eq 'relevance')
        then
            for $c in $collections
            order by map:count($docs-map * map:get($collections-map, $c))
            return $c
        else if ($sort eq 'relevance-dsc')
        then
            for $c in $collections
            order by map:count($docs-map * map:get($collections-map, $c)) * -1
            return $c
        else if ($sort eq 'shuffle')
        then
            for $c in $collections
            order by xdmp:random()
            return $c
        else
            ()

    let $collections-limited :=
        if ($limit gt 0)
        then fn:subsequence($collections-sorted, 1, $limit)
        else $collections-sorted

    return
        <json:array>
            {
                for $c in $collections-limited
                return
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">
                            { 
                                map:count($docs-map * map:get($collections-map, $c))
                            }
                        </json:value>
                    </json:array>
            }
        </json:array>
};

declare function get-collections-for-results($results) {
    (: Get a unique sequence of collections for a set of results.

       Params
         $results - search results from cts:search()

       Returns
         a sequence of unique strings, MarkLogic collection URIs. 
    :)

    map:keys(
        map:new(
            for $r in $results
            return 
                for $c in xdmp:document-get-collections($r)
                return map:entry($c, fn:true())
        )
    )
};

(::::::
  MAIN
 ::::::)

let $collections-starts-with :=
    for $c in get-collections-for-results(json:array-values($docs))
    return
        if (fn:starts-with($c, $b))
        then $c
        else ()

return json:object(
    <json:object>
        <json:entry>
            <json:key>b</json:key>
            <json:value>{ $b }</json:value>
        </json:entry>
        <json:entry>
            <json:key>results</json:key>
            <json:value>
                {
                    get-collection-counts(
                        json:array-values($docs),
                        $collections-starts-with,
                        $sort,
                        $limit
                    )
                }
            </json:value>
        </json:entry>
        <json:entry>
            <json:key>sort</json:key>
            <json:value>{ $sort }</json:value>
        </json:entry>
        <json:entry>
            <json:key>sort</json:key>
            <json:value>{ $sort }</json:value>
        </json:entry>
    </json:object>
)
