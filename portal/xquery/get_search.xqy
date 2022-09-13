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

(::::::::::::::::::::
  EXTERNAL VARIABLES
 ::::::::::::::::::::)

(: For a complete browse of of a certain facet type, match browse URIs
   beginning with this string, e.g., https://bmrc.lib.uchicago.edu/topics/
   In browse mode you can also pass sort and limit for browse results
   instead of search results. :)
declare variable $b as xs:string external;

(: A JSON array of collections currently active. (i.e. 'f' params.) 
   search results will be restricted to these collections only. :)
declare variable $collections_active_raw as json:array external;

(: A query string. :)
declare variable $q as xs:string external;

(: For paged search results, start a page of search results from this index. :)
declare variable $start as xs:integer external;

(: Number of links to return for each sidebar facet. :)
declare variable $sidebar-facet-limit as xs:integer external;

(: For paged search results, number of results for this result page. :)
declare variable $size as xs:integer external;

(: Sorting for searches and browses. :)
declare variable $sort as xs:string external;

(: Placeholder variable for estimated search results. :)
declare variable $lookahead-pages as xs:integer := 1;

(:::::::::::::
   FUNCTIONS 
 :::::::::::::)

declare function abstract($doc) {
    (: Get the abstract for a finding aid.

       Params
         $doc - e.g. fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's abstract.
    :)
    let $tokens := fn:tokenize(
        fn:normalize-space(
            fn:string-join(
                ($doc//ead:abstract | $doc//ead:bioghist | $doc//ead:scopecontent)[1]//text()[fn:not(parent::ead:head)]
            )   
        ),
        ' '
    )
    return fn:concat(
        fn:string-join(
            $tokens[1 to 60],
            ' '
        ),
        ''
    )
};

declare function archive($doc) {
    (: Get the archive for a finding aid.

       Params
         $doc - e.g. fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's archive.

    figure out what archive this document is a part of. 
    assuming this is a map below. 

    for $s in map:keys($starts-with-dict)
    return
        if (
            fn:starts-with(
                fn:document-uri($doc),
                $s
            )
        )
        then map:get($starts-with-dict, $s)
        else ()

    for $n in $starts-with-json/node()
    return 
        if (
            fn:starts-with(
                fn:document-uri($doc),
                local-name($n)
            )
        )
        then $n/text()

    :)
    for $c in xdmp:document-get-collections(fn:document-uri($doc))
    return
        if (
            fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/archives/')
            and fn:not(
                fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/archives/BMRC+Portal')
            )
        )
        then xdmp:url-decode(
            fn:replace($c, 'https://bmrc.lib.uchicago.edu/archives/', '')
        )
        else ()
};

declare function archive-uri($doc) {
    (: Get the archive uri for a finding aid.

       Params
         $doc - e.g. fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's archive.
    :)
    for $c in xdmp:document-get-collections(fn:document-uri($doc))
    return
        if (
            fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/archives/')
            and fn:not(
                fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/archives/BMRC+Portal')
            )
        )
        then $c
        else ()
};

declare function collection-counts($collections, $docs, $sort, $limit) {
    (: 
       Params

         $collections - sequence of collections to consider.
         $docs        - a pre-computed sequence of document URIs to consider, like
                        the result documents from a search.
         $sort        - sort for results.
         $limit       - limit for results.

       Returns

         a JSON array, e.g.:
           [
             [
               "https://bmrc.lib.uchicago.edu/topics/one",
               "one",
               100
             ],
             ...
           ]

       Notes
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
            let $d := fn:replace(
                $c,
                '^(The) ',
                ''
            )
            order by $d
            return $c
        else if ($sort eq 'alpha-dsc')
        then
            for $c in $collections
            let $d := fn:replace(
                $c,
                '^(The) ',
                ''
            )
            order by $d descending
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

declare function collection-counts-wrap($collections-seq, $collections-starts-with, $collections-skip, $collections-browse, $docs-seq, $sidebar-facet-sort, $browse-sort, $sidebar-facet-limit) {
    (: Wrapper function to get collection counts for either the sidebar or a complete facet browse.

       Params
 
          $collections-seq         - a sequence of collections for search
                                     results.
          $collections-starts-with - filter $collections-seq for URIs beginning
                                     with this string.
          $collections-skip        - a sequence of collection URIs to skip
                                     (e.g., currently active collections)
          $collections-browse      - if a browse was specified, return every
                                     result. otherwise, return a smaller amount
                                     of results for a sidebar facet.
          $docs-seq                - a sequence of documents from search results.
          $sidebar-facet-sort      - sort for when we're returning results for
                                     a sidebar facet.
          $browse-sort             - sort for when we're returning a complete
                                     browse list for a facet.
          $sidebar-facet-limit     - limit for sidebar facets.

       Returns
   
           See collection-counts()
    :)
    collection-counts(
        for $c in $collections-seq
        return
            if (fn:starts-with($c, $collections-starts-with) and fn:not($c = $collections-skip) and $c ne 'https://bmrc.lib.uchicago.edu/archives/BMRC+Portal')
            then $c 
            else (),
        $docs-seq,
        if ($collections-browse eq $collections-starts-with)
        then $browse-sort
        else $sidebar-facet-sort,
        if ($collections-browse eq $collections-starts-with)
        then 0
        else $sidebar-facet-limit
    )
};

declare function collection-counts-for-doc($doc, $starts-with, $limit) {
    (: Get a list of facet tags for each search results. 

       Params

         $doc         - document to retrieve facets for.
         $starts-with - retrieve facets beginning with this string, e.g.,
                        https://bmrc.lib.uchicago.edu/topics/
         $limit       - retrive this many results only.

       Returns
         a JSON array, e.g.:
           [
             [
               "https://bmrc.lib.uchicago.edu/topics/one",
               "one",
               100
             ],
             ...
           ]

       Notes

         Unlike with the collection-counts() function, this function
         assumes that clicking on one of these tags starts a new, "fresh"
         search- so the facets that are present and the counts for each facet
         reflect all documents in the system. Because of that this function
         does not include a sequence of documents to consider as a parameter.

         Results are hard-coded to sort by descending relevance.
    :)

    let $collections-filtered :=
        for $c in xdmp:document-get-collections(fn:document-uri($doc))
        return
            if (fn:starts-with($c, $starts-with))
            then $c
            else ()

    let $collections-sorted :=
        for $c in $collections-filtered
        order by fn:count(fn:collection($c)) descending
        return $c
 
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
                                fn:count(fn:collection($c))
                            }
                        </json:value>
                    </json:array>
            }
        </json:array>
};

declare function collections-for-results($results) {
    (: Get a unique sequence of collections for a set of results.

       Params
         $results - search results from cts:search()

       Returns
         a sequence of unique MarkLogic collection URIs. 

       Notes
         map:keys() returns a unique sequence faster than fn:distinct-values().
    :)

    map:keys(
        map:new(
            for $r in $results
            return 
                for $c in xdmp:document-get-collections(fn:document-uri($r))
                return map:entry($c, fn:true())
        )
    )
};

declare function date($doc) {
    (: Get the date for a finding aid.

       Params
         $doc - e.g. fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's date.
    :)
    ($doc//ead:unitdate)[1]/text()
};

declare function extent($doc) {
    (: Get the extent for a finding aid.

       Params
         $doc - e.g. fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's extent.

       Notes
         collect the <physdesc> instead of the <extent> because there are a
         substantial number of cases where extent isn't actually present.
    :)
    let $physdesc_string_list :=
        for $p in $doc/ead:ead/ead:archdesc[1]/ead:did[1]/ead:physdesc
        return
            fn:normalize-space(
                fn:string-join(
                    $p//text(),
                    ' '
                )
            )
    return fn:string-join(
        $physdesc_string_list,
        '; '
    )
};

declare function page-results(
    $results         as item()*,
    $start           as xs:integer,
    $size            as xs:integer,
    $sort            as xs:string,
    $lookahead-pages as xs:integer
) {
    (: Get a page of search results.

       Params
         $results         - a sequence of items returned from e.g. cts:search()
         $start           - begin with this index.
         $size            - size of result page.
         $sort            - sort for this result set.
         $lookahead-pages - placeholder variable.

       Returns
         a sequence of paged search results.
    :)

    let $ordered-results :=
        for $r in $results
        order by
            if ($sort eq 'alpha' or $sort eq 'alpha-dsc')
            then sort-title($r)
            else if ($sort eq 'shuffle')
            then xdmp:random()
            else ()
        return $r

    let $paged-results :=
        if ($sort eq 'alpha-dsc' or $sort eq 'relevance-dsc')
        then fn:reverse($ordered-results)
        else $ordered-results

    return $paged-results[$start + 1 to $start + $size]
};

declare function query($raw-query as xs:string, $collections) as cts:query? {
    (: Build a query from a raw query string and a sequence of collections. 

       Params
         $raw-query   - a string, the query itself.
         $collections - a sequnce of collections to restrict this query to.

       Returns
         a cts:and-query() which can be passed to cts:search()

       Notes
	 Exact queries are wrapped in double quotes. Otherwise all active
	 facets are ANDed together, to search for results within the
         intersection of all collections passed to this script.
    :)

    let $options := (
        'case-insensitive',
        'diacritic-insensitive',
        'punctuation-insensitive',
        'whitespace-insensitive'
    )

    return cts:and-query(
        (
            (
                if ($raw-query eq "")
                then ()
                else
                    if (fn:starts-with($raw-query, '"') and fn:ends-with($raw-query, '"'))
                    then 
                        cts:word-query(fn:replace($raw-query, '"', ''), fn:insert-before($options, 0, 'distance-weight=64'))
                    else
                        for $t in fn:tokenize($raw-query, '\s+')[. ne '']
                        return cts:word-query($t, $options)
            ),
            for $c in $collections
            return cts:collection-query($c)
        )
    )
};

declare function results-for-collection($results, $collection) {
    (: Get results for a given collection, from a larger set of results.

       Params
         $results - search results from cts:search()

       Returns
         a sequence of unique MarkLogic collection URIs. 

       Notes
         map:keys() returns a unique sequence faster than fn:distinct-values().
    :)

    map:keys(
        map:new(
            for $r in $results
            return 
                if ($collection = xdmp:document-get-collections(fn:document-uri($r)))
                then map:entry($r, fn:true())
                else ()
        )
    )
};

declare function sort-title($doc) {
    (: Get the title for a given document.

       Params
         $doc - a MarkLogic document object, e.g.
                fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's title.
     :)

     fn:replace(
         title($doc),
         '^(The) ',
         ''
     )
};

declare function title($doc) {
    (: Get the title for a given document.

       Params
         $doc - a MarkLogic document object, e.g.
                fn:doc('BMRC.DEFENDER.INDIVIDUALS.xml')

       Returns
         a string, the document's title.
     :)

     fn:normalize-space($doc/ead:ead[1]/ead:frontmatter[1]/ead:titlepage[1]/ead:titleproper[1])
};

(:::::::::::
  VARIABLES
 :::::::::::)

(: a sequence of collections that are confirmed to exist in the system. :)
let $collections-active :=
    for $c in json:array-values($collections_active_raw)
    return
        if (fn:exists(fn:collection($c)))
        then $c
        else ()

(: search results. :)
let $search-results := 
    cts:search(
        fn:doc(),
        query(
            $q,
            $collections-active
        )
    )

(: collections present in this set of search results. :)
let $search-results-collections := collections-for-results($search-results)

(: total number of search results :)
let $total := fn:count($search-results)

(: paging. :)
let $paged-search-results := page-results(
    $search-results,
    $start,
    $size,
    $sort,
    $lookahead-pages
)

(: get a sequence of document URIs for search results to pass to collection-counts(). :)
let $docs-seq := 
    if (fn:empty($search-results))
    then
        for $d in fn:doc()
        return fn:document-uri($d)
    else
        for $r in $search-results
        return fn:document-uri($r)

(: sort for sidebar facets. :)
let $sidebar-facet-sort := 'relevance-dsc'

(: active collections, broken up by type, so they can be included in the facet sidebar. :)
let $active-archives :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/archives/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

let $active-decades :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/decades/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

let $active-organizations :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/organizations/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

let $active-people :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/people/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

let $active-places :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/places/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

let $active-topics :=
    <json:array>
        {
            for $c in $collections-active
            return
                if (fn:starts-with($c, 'https://bmrc.lib.uchicago.edu/topics/'))
                then
                    <json:array>
                        <json:value>{ $c }</json:value>
                        <json:value>
                            { 
                                xdmp:url-decode(fn:tokenize($c, "/")[5]) 
                            }
                        </json:value>
                        <json:value xsi:type="xs:integer">{ fn:count(results-for-collection($search-results, $c)) }</json:value>
                    </json:array>
                else ()
        }
    </json:array>

(: facets for the sidebar or for complete browse lists. :)
let $more-archives := 
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/archives/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )
        
let $more-decades :=
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/decades/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )

let $more-organizations :=
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/organizations/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )

let $more-people :=
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/people/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )

let $more-places :=
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/places/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )

let $more-topics :=
    collection-counts-wrap(
        $search-results-collections, 
        'https://bmrc.lib.uchicago.edu/topics/',
        $collections-active,
        $b,
        $docs-seq,
        $sidebar-facet-sort,
        $sort,
        $sidebar-facet-limit + 1
    )

return json:object(
    <json:object>
        <json:entry>
            <json:key>active_archives</json:key>
            <json:value>{ $active-archives }</json:value>
        </json:entry>
        <json:entry>
            <json:key>active_decades</json:key>
            <json:value>{ $active-decades }</json:value>
        </json:entry>
        <json:entry>
            <json:key>active_organizations</json:key>
            <json:value>{ $active-organizations }</json:value>
        </json:entry>
        <json:entry>
            <json:key>active_people</json:key>
            <json:value>{ $active-people }</json:value>
        </json:entry>
        <json:entry>
            <json:key>active_places</json:key>
            <json:value>{ $active-places }</json:value>
        </json:entry>
        <json:entry>
            <json:key>active_topics</json:key>
            <json:value>{ $active-topics }</json:value>
        </json:entry>
        <json:entry>
            <json:key>b</json:key>
            <json:value>{ $b }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_archives</json:key>
            <json:value>{ $more-archives }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_decades</json:key>
            <json:value>{ $more-decades }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_organizations</json:key>
            <json:value>{ $more-organizations }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_people</json:key>
            <json:value>{ $more-people }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_places</json:key>
            <json:value>{ $more-places }</json:value>
        </json:entry>
        <json:entry>
            <json:key>more_topics</json:key>
            <json:value>{ $more-topics }</json:value>
        </json:entry>
        <json:entry>
            <json:key>q</json:key>
            <json:value>{ $q }</json:value>
        </json:entry>
        <json:entry>
            <json:key>sort</json:key>
            <json:value>{ $sort }</json:value>
        </json:entry>
        <json:entry>
            <json:key>size</json:key>
            <json:value xsi:type="xs:integer">{ $size }</json:value>
        </json:entry>
        <json:entry>
            <json:key>start</json:key>
            <json:value xsi:type="xs:integer">{ $start }</json:value>
        </json:entry>
        <json:entry>
            <json:key>stop</json:key>
            <json:value xsi:type="xs:integer">{ fn:min(($start + $size - 1, $total)) }</json:value>
        </json:entry>
        <json:entry>
            <json:key>total</json:key>
            <json:value xsi:type="xs:integer">{ $total }</json:value>
        </json:entry>
        <json:entry>
            <json:key>collections-active</json:key>
            <json:value>
                <json:array>
                    { 
                        for $c in $collections-active
                        return
                            <json:array>
                                <json:value>{ $c }</json:value>
                                <json:value>{ xdmp:url-decode(fn:tokenize($c, "/")[5]) }</json:value>
                                <json:value xsi:type="xs:integer">{ fn:count(cts:search(fn:doc(for $x in $search-results return fn:document-uri($x)), cts:collection-query($c))) }</json:value>
                            </json:array>
                    }
                </json:array>
            </json:value>
        </json:entry>
        <json:entry>
            <json:key>results</json:key>
            <json:value>
                <json:array>
                    {
                        for $r at $i in $paged-search-results
                        (: need date, extent, and archives for each of these. :)
                        return
                            <json:value>
                                <json:object>
                                    <json:entry>
                                        <json:key>abstract</json:key>
                                        <json:value>{ abstract($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>archive</json:key>
                                        <json:value>{ archive($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>archive_uri</json:key>
                                        <json:value>{ archive-uri($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>date</json:key>
                                        <json:value>{ date($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>extent</json:key>
                                        <json:value>{ extent($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>index</json:key>
                                        <json:value xsi:type="xs:integer">{ $start - 1 + $i }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>title</json:key>
                                        <json:value>{ title($r) }</json:value>
                                    </json:entry>
                                    <json:entry>
                                        <json:key>uri</json:key>
                                        <json:value>{ fn:document-uri($r) }</json:value>
                                    </json:entry>
                                </json:object>
                            </json:value>
                    }
                </json:array>
            </json:value>
        </json:entry>
    </json:object>
)
