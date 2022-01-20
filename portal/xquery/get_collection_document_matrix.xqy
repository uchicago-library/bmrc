(: in this form it takes 26 minutes to pre-compute the matrix. :)

let $collections :=
  for $c in cts:collections()
  order by $c
  return $c
  
let $documents :=
  for $d in fn:doc()
  order by fn:document-uri($d)
  return fn:document-uri($d)

return json:object(
  <json:object>
    <json:entry>
      <json:key>collections</json:key>
      <json:value>
        <json:array>
          {
            for $c in $collections
            return <json:value>{ $c }</json:value>
          }
        </json:array>
      </json:value>
    </json:entry>
    <json:entry>
      <json:key>documents</json:key>
      <json:value>
        <json:array>
          {
            for $d in $documents
            return <json:value>{ $d }</json:value>
          }
        </json:array>
      </json:value>
    </json:entry>
    <json:entry>
      <json:key>collection_document_matrix</json:key>
      <json:value>
        <json:array>
          {
            for $c in $collections
            return
              <json:array>
                {
                  for $d in $documents
                  return
                    <json:value xsi:type="xs:boolean">{ fn:exists(fn:collection($c)/fn:doc($d)) }</json:value>
                }
              </json:array>
          }
        </json:array>
      </json:value>
    </json:entry>
  </json:object>
)
