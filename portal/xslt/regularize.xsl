<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
 xmlns:ead="urn:isbn:1-931666-22-9"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output omit-xml-declaration="yes"/>

<!-- * -->
<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- ABSTRACT -->
<xsl:template match="ead:abstract[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Abstract</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- ACCESSRESTRICT -->
<xsl:template match="ead:accessrestrict[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Conditions for Access</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- ACCRUALS -->
<xsl:template match="ead:accruals[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Accruals</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- ACQINFO -->
<xsl:template match="ead:acqinfo[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Acquisition Information</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- ALTFORMAVAIL -->
<xsl:template match="ead:altformavail[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Alternate Format Available</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- APPRAISAL -->
<xsl:template match="ead:appraisal[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Appraisal</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- ARRANGEMENT -->
<xsl:template match="ead:arrangement[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Arrangement</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- BIBLIOGRAPHY -->
<xsl:template match="ead:bibliography[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Bibliography</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="ead:bibliography/ead:bibref">
  <xsl:if test="not(preceding-sibling::ead:bibref)">
    <ead:list>
      <xsl:apply-templates select="." mode="item"/>
      <xsl:for-each select="following-sibling::ead:bibref">
        <xsl:apply-templates select="." mode="item"/>
      </xsl:for-each>
    </ead:list>
  </xsl:if>
</xsl:template>

<xsl:template match="ead:bibref" mode="item">
  <ead:item>
    <xsl:copy-of select="."/>
  </ead:item>
</xsl:template>

<!-- BIOGHIST -->
<xsl:template match="ead:bioghist[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Biography or History</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- C## -->
<xsl:template match="ead:c01 | ead:c02 | ead:c03 | ead:c04 | ead:c05 | 
                     ead:c06 | ead:c07 | ead:c08 | ead:c09 | ead:c10 | 
                     ead:c11 | ead:c12"> 
  <ead:c>
    <xsl:apply-templates select="@*|node()"/>
  </ead:c>
</xsl:template>

<!-- CONTAINER -->
<xsl:template match="ead:container[@type]">
  <xsl:copy>
    <xsl:attribute name="type">
      <xsl:value-of select="
          concat(
            substring(
                translate(
                    @type,
                    'abcdefghijklmnopqrstuvwxyz',
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                ),  
                1,  
                1   
            ),
            substring(@type, 2)
          )
      "/>
    </xsl:attribute>
    <xsl:apply-templates select="@*[name()!='type']|node()"/>
  </xsl:copy>
</xsl:template>

<!-- CONTROLACCESS -->
<xsl:template match="ead:controlaccess[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Indexed Terms</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="ead:controlaccess/ead:corpname |
                     ead:controlaccess/ead:famname |
                     ead:controlaccess/ead:function |
                     ead:controlaccess/ead:genreform |
                     ead:controlaccess/ead:geogname |
                     ead:controlaccess/ead:name |
                     ead:controlaccess/ead:occupation |
                     ead:controlaccess/ead:persname |
                     ead:controlaccess/ead:subarea |
                     ead:controlaccess/ead:subject |
                     ead:controlaccess/ead:title">
  <xsl:if test="not(preceding-sibling::ead:corpname) and
                not(preceding-sibling::ead:famname) and
                not(preceding-sibling::ead:function) and
                not(preceding-sibling::ead:genreform) and
                not(preceding-sibling::ead:geogname) and
                not(preceding-sibling::ead:name) and
                not(preceding-sibling::ead:occupation) and
                not(preceding-sibling::ead:persname) and
                not(preceding-sibling::ead:subarea) and
                not(preceding-sibling::ead:subject) and
                not(preceding-sibling::ead:title)">
    <ead:list>
      <xsl:apply-templates select="." mode="item"/>
      <xsl:for-each select="following-sibling::ead:corpname | following-sibling::ead:famname | following-sibling::ead:function | following-sibling::ead:genreform | following-sibling::ead:geogname | following-sibling::ead:name | following-sibling::ead:occupation | following-sibling::ead:persname | following-sibling::ead:subarea | following-sibling::ead:subject">
        <xsl:apply-templates select="." mode="item"/>
      </xsl:for-each>
    </ead:list>
  </xsl:if>
</xsl:template>

<xsl:template match="ead:corpname | ead:famname | ead:function | ead:genreform | ead:geogname | ead:name | ead:occupation | ead:persname | ead:subarea | ead:subject" mode="item">
  <ead:item>
    <xsl:copy-of select="."/>
  </ead:item>
</xsl:template>

<!-- CUSTODHIST -->
<xsl:template match="ead:custodhist[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Custodial History</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- DID -->
<xsl:template match="ead:archdesc/ead:did[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Descriptive Summary</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- DID/* -->
<xsl:template match="ead:archdesc/ead:did/*[@label]">
  <xsl:copy>
    <xsl:attribute name="label">
      <xsl:value-of select="
        concat(
          substring(
              translate(
                  @label,
                  'abcdefghijklmnopqrstuvwxyz',
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              ),  
              1,  
              1   
          ),
          substring(@label, 2)
        )
    "/>
    </xsl:attribute>
    <xsl:apply-templates select="@*[name()!='label']|node()"/>
  </xsl:copy>
</xsl:template>

<!-- DSC -->
<xsl:template match="ead:dsc[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Inventory</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="ead:dsc[not(*)]"/>

<!-- EADHEADER, FRONTMATTER -->
<xsl:template match="ead:eadheader">
  <xsl:copy-of select="."/>
  <xsl:if test="not(//ead:frontmatter)">
    <ead:frontmatter>
      <ead:titlepage>
        <ead:titleproper>
          <!-- omit <num> elements embedded inside <titleproper> -->
          <xsl:value-of select="//ead:titleproper[1]/text()"/>
        </ead:titleproper>
        <xsl:copy-of select="//ead:author[1]"/>
      </ead:titlepage>
    </ead:frontmatter>
  </xsl:if>
</xsl:template>

<!-- FILEPLAN -->
<xsl:template match="ead:fileplan[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Filing System</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- INDEX -->
<xsl:template match="ead:index[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Index</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- LANGMATERIAL -->
<xsl:template match="ead:archdesc/ead:did/ead:langmaterial[not(@label)] |
                     ead:dsc//ead:langmaterial[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Language</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- LANGUAGE -->
<xsl:template match="ead:language[not(text())]">
  <xsl:choose>
    <xsl:when test="@langcode='aar'">Afar</xsl:when>
    <xsl:when test="@langcode='eng'">English</xsl:when>
    <xsl:when test="@langcode='fre'">French</xsl:when>
    <xsl:when test="@langcode='ger'">German</xsl:when>
    <xsl:otherwise/>
  </xsl:choose>
</xsl:template>

<!-- ODD -->
<xsl:template match="ead:odd[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Other Descriptive Data</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- ORIGINATION -->
<xsl:template match="ead:archdesc/ead:did/ead:origination[not(@label)] |
                     ead:dsc//ead:origination[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Creator</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- OTHERFINDINGAID -->
<xsl:template match="ead:otherfindingaid[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Other Finding Aid</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- PHYSDESC -->
<xsl:template match="ead:physdesc[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Size</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- PHYSLOC -->
<xsl:template match="ead:physloc[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Storage Location</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- PHYSTECH -->
<xsl:template match="ead:phystech[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Physical Characteristics and Technical Requirements</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- PREFERCITE -->
<xsl:template match="ead:prefercite[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Preferred Citation</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- PROCESSINFO -->
<xsl:template match="ead:processinfo[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Processing Information</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- RELATED MATERIAL -->
<xsl:template match="ead:relatedmaterial[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Related Material</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="ead:relatedmaterial/ead:archref">
  <xsl:if test="not(preceding-sibling::ead:archref)">
    <ead:list>
      <xsl:apply-templates select="." mode="item"/>
      <xsl:for-each select="following-sibling::ead:archref">
        <xsl:apply-templates select="." mode="item"/>
      </xsl:for-each>
    </ead:list>
  </xsl:if>
</xsl:template>

<xsl:template match="ead:archref" mode="item">
  <ead:item>
    <xsl:copy-of select="."/>
  </ead:item>
</xsl:template>

<!-- REPOSITORY -->
<xsl:template match="ead:archdesc/ead:did/ead:repository[not(@label)] |
                     ead:dsc//ead:repository[not(@label)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <xsl:attribute name="label">Repository</xsl:attribute>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- SCOPECONTENT -->
<xsl:template match="ead:scopecontent[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Scope and Content</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- SEPARATEDMATERIAL -->
<xsl:template match="ead:separatedmaterial[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Separated Material</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<!-- UNITDATE -->
<xsl:template match="ead:archdesc/ead:did/ead:unitdate[not(@label)] |
                     ead:dsc//ead:unitdate[not(@label)]">
  <xsl:variable name="label">
    <xsl:choose>
      <xsl:when test="@type='bulk'">
        <xsl:value-of select="'Predominant Dates'"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="'Dates'"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:copy>
    <xsl:attribute name="label"><xsl:value-of select="$label"/></xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- UNITID -->
<xsl:template match="ead:archdesc/ead:did/ead:unitid[not(@label)] |
                     ead:dsc//ead:unitid[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Identifier</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- UNITTITLE -->
<xsl:template match="ead:archdesc/ead:did/ead:unittitle[not(@label)] |
                     ead:dsc//ead:unittitle[not(@label)]">
  <xsl:copy>
    <xsl:attribute name="label">Title</xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- USERESTRICT -->
<xsl:template match="ead:userestrict[not(ead:head)]">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Conditions Governing Use</ead:head>
    <xsl:apply-templates select="node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="ead:archdesc/ead:did//ead:userestrict">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- ****************************** -->
<!-- * PROJECT-SPECIFIC OVERRIDES * -->
<!-- ****************************** -->

<!-- CONTROLACCESS
     For the portal, <controlaccess> elements should always be given the
     heading "Indexed Terms", even if a different heading was used in the
     finding aid itself. This is because other headings, (e.g. "Control
     Access") are jargon-y and off-putting to users. As per LLM, 
     10/26/2021. -->

<xsl:template match="ead:controlaccess" priority="2.0">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <ead:head>Indexed Terms</ead:head>
    <xsl:apply-templates select="*[not(self::ead:head)]|text()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>
