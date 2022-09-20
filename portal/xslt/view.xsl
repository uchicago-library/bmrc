<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
 xmlns:ead="urn:isbn:1-931666-22-9"
 xmlns:str="http://exslt.org/strings"
 xmlns:ucf="https://lib.uchicago.edu/functions/"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 exclude-result-prefixes="ead str ucf xlink">

<!-- NOTES

     Outputting block-level (div) or inline (span) wrapper elements

     to determine if elements should output inline or block level wrappers, I
     check to see if their parent element allows PCDATA or not. For elements
     like ead:p, I output spans, but for elements like ead:did, I output divs.
  -->

<xsl:output omit-xml-declaration="yes"/>

<!-- PARAMETER: EADID -->
<xsl:param name="eadid"/>

<!-- PARAMETER: Q -->
<xsl:param name="q"/>

<!-- @* -->
<xsl:template match="@*"/>

<!-- @AUDIENCE = 'internal' -->
<xsl:template match="*[@audience = 'internal']" priority="9.0"/>

<!-- @ID -->
<xsl:template match="@id">
  <xsl:copy/>
</xsl:template>

<!-- @LABEL -->
<xsl:template match="@label[not(ancestor::ead:dsc)]">
  <h3>
    <xsl:attribute name="class">
      <xsl:value-of select="concat('ead_', local-name(..))"/>
    </xsl:attribute>
    <xsl:attribute name="id">
      <xsl:call-template name="generate_readable_id"/>
    </xsl:attribute>
    <xsl:value-of select="."/>
  </h3>
</xsl:template>

<!-- ABBR -->
<xsl:template match="ead:abbr">
  <abbr class="ead_abbr">
    <xsl:apply-templates select="@*|node()"/>
  </abbr>
</xsl:template>

<xsl:template match="ead:abbr[@expan]">
  <abbr class="ead_abbr" title="{@expan}">
    <xsl:apply-templates select="@*[name() != 'expan']|node()"/>
  </abbr>
</xsl:template>

<!-- ABSTRACT -->
<xsl:template match="ead:abstract">
  <xsl:apply-templates select="@label"/>
  <p class="ead_abstract">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </p>
</xsl:template>

<!-- top of archival description or inventory -->
<xsl:template match="ead:archdesc/ead:did/ead:abstract |
                     ead:dsc//ead:did/ead:abstract" priority="1.1">
  <dt class="ead_abstract">
    <xsl:apply-templates select="@*[name() != 'label']"/>
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_abstract">
    <xsl:apply-templates select="node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:abstract" priority="1.2">
  <div class="ead_abstract">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ACCESSRESTRICT -->
<xsl:template match="ead:accessrestrict">
  <div class="ead_accessrestrict">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ACCRUALS -->
<xsl:template match="ead:accruals">
  <div class="ead_accruals">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ACQINFO -->
<xsl:template match="ead:acqinfo">
  <div class="ead_acqinfo">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ADDRESS -->
<xsl:template match="ead:address">
  <address class="ead_address">
    <xsl:apply-templates select="@*|node()"/>
  </address>
</xsl:template>

<!-- ADDRESSLINE -->
<xsl:template match="ead:addressline">
  <div class="ead_addressline">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ALTFORMAVAIL -->
<xsl:template match="ead:altformavail">
  <div class="ead_altformavail">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- APPRAISAL -->
<xsl:template match="ead:appraisal">
  <div class="ead_appraisal">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ARC -->
<xsl:template match="ead:arc"/>

<!-- ARCHDESC -->
<xsl:template match="ead:archdesc">
  <div class="ead_archdesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ARCHDESCGRP -->
<xsl:template match="ead:archdescgrp">
  <div class="ead_archdescgrp">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ARCHREF -->
<xsl:template match="ead:archref">
  <div class="ead_archref">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ARRANGEMENT -->
<xsl:template match="ead:arrangement">
  <div class="ead_arrangement">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- AUTHOR -->
<xsl:template match="ead:author">
  <div class="ead_author">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- BIBLIOGRAPHY -->
<xsl:template match="ead:bibliography">
  <div class="ead_bibliography">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- BIBREF
     usually outputs an inline element, unless it is a child of bibliography,
     etc. -->
<xsl:template match="ead:bibref">
  <span class="ead_bibref">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="*[   self::ead:bibliography
                       or self::ead:otherfindingaid
                       or self::ead:relatedmaterial
                       or self::ead:separatedmaterial]/ead:bibref">
  <div class="ead_bibref">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- BIBSERIES
     usually outputs an inline element, unless it is a child of titlepage. -->
<xsl:template match="ead:bibseries">
  <span class="ead_bibseries">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:titlepage/ead:bibseries">
  <div class="ead_bibseries">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- BIOGHIST -->
<xsl:template match="ead:bioghist">
  <div class="ead_bioghist">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- BLOCKQUOTE
     note that html:blockquote is allowed to contain PCDATA, but ead:blockquote
     isn't. ead:blockquote always contains elements like <ead:p>, so rather than
     outputting an html:blockquote here we output a div. -->
<xsl:template match="ead:blockquote">
  <div class="ead_blockquote">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- C -->
<xsl:template match="ead:c">
  <xsl:variable name="c_count" select="count(ancestor-or-self::ead:c)"/>
  <xsl:variable name="c_class">
    <xsl:choose>
      <xsl:when test="$c_count &lt; 10">
        <xsl:value-of select="concat('ead_c0', $c_count)"/>
      </xsl:when> 
      <xsl:otherwise>
        <xsl:value-of select="concat('ead_c', $c_count)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="c_level">
    <xsl:choose>
      <xsl:when test="@level">
        <xsl:value-of select="concat('ead_c_', @level)"/>
      </xsl:when> 
      <xsl:otherwise>
        <xsl:value-of select="''"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <div class="{concat('ead_c ', $c_class, ' ', $c_level)}">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- CHANGE -->
<!-- don't output anything extra for this element, since nothing is allowed
     between a <dl> and <dt>, <dd> pairs. -->
<xsl:template match="ead:change">
  <xsl:apply-templates select="node()"/>
</xsl:template>

<!-- CHRONITEM -->
<xsl:template match="ead:chronitem">
  <dd class="ead_chronitem">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<!-- CHRONLIST -->
<xsl:template match="ead:chronlist">
  <dl class="ead_chronlist">
    <xsl:apply-templates select="@*|node()"/>
  </dl>
</xsl:template>

<!-- COLSPEC -->
<xsl:template match="ead:colspec"/>

<!-- CONTAINER
     Note:

     The vast majority of <container> elements use one of the following forms:
     <container type="Folder">3</container>
     <container type="othertype">drawer 4</container>

     Because of this, append the @type to the text output for all containers,
     except when a container has been specifically marked as "othertype". 
-->
<xsl:template match="ead:container">
  <div class="ead_container">
    <xsl:apply-templates select="@*"/>
    <xsl:value-of select="concat(@type, ' ')"/> <xsl:apply-templates select="node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:container[@type = 'Othertype']" priority="1.1">
  <div class="ead_container">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- CORPNAME
     When ead:corpname is a child of ead:controlaccess or ead:inventory,
     output a <div>. Output an <li> when it is a child of ead:namegrp.
     For all other parents, output a <span>. -->
<xsl:template match="ead:corpname">
  <span class="ead_corpname">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:corpname" priority="1.1">
  <li class="ead_corpname">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:controlaccess
                       or self::ead:indexentry   ]/ead:corpname" priority="1.1">
  <div class="ead_corpname">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- CREATION -->
<xsl:template match="ead:creation">
  <div class="ead_creation">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DAO -->
<xsl:template match="ead:dao">
  <a class="ead_dao" href="{@href}">
    <xsl:apply-templates select="@*[name() != 'href']|node()"/>
  </a>
</xsl:template>

<!-- DAODESC
     output a div, unless this element is a child of ead:namegrp- then output
     an li.-->
<xsl:template match="ead:daodesc">
  <div class="ead_daodesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:daogrp/ead:daodesc" priority="1.1">
  <li class="ead_daodesc">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- DAOGRP -->
<xsl:template match="ead:daogrp">
  <ul class="ead_daogrp">
    <xsl:apply-templates select="@*|node()"/>
  </ul>
</xsl:template>

<!-- DAOLOC 
     output a link, unless the parent is daogrp- then output an li and a link.
     -->
<xsl:template match="ead:daoloc">
  <a class="ead_daoloc" href="{@href}">
    <xsl:apply-templates select="@*[name() != 'href']|node()"/>
  </a>
</xsl:template>

<xsl:template match="ead:daogrp/ead:daoloc" priority="1.1">
  <li class="ead_daoloc">
    <a href="{@href}">
      <xsl:apply-templates select="@*[name() != 'href']|node()"/>
    </a>
  </li>
</xsl:template>

<!-- DATE -->
<!-- output a div when this the parent is publicationstmt or titlepage.
     output a dt when the parent is change or chronlist.
     otherwise output a span. -->
<xsl:template match="ead:date">
  <span class="ead_date">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="*[   self::ead:change 
                       or self::ead:chronlist]/ead:date" priority="1.1">
  <dt class="ead_date">
    <xsl:apply-templates select="@*|node()"/>
  </dt>
</xsl:template>

<xsl:template match="*[   self::ead:publicationstmt
                       or self::ead:titlepage      ]/ead:date" priority="1.1">
  <div class="ead_date">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DEFITEM -->
<xsl:template match="ead:defitem">
  <dl class="ead_defitem">
    <xsl:apply-templates select="@*|node()"/>
  </dl>
</xsl:template>

<!-- DESCGRP -->
<xsl:template match="ead:descgrp">
  <div class="ead_descgrp">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DESCRULES -->
<xsl:template match="ead:descrules">
  <div class="ead_descrules">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DID -->
<xsl:template match="ead:archdesc/ead:did">
  <xsl:apply-templates select="ead:head"/>
  <dl class="ead_did">
    <xsl:apply-templates select="@*|*[not(self::ead:head)]|text()"/>
  </dl>
</xsl:template>

<!--
     A <did> may contain: 
       0 or more <unitid> elements
       0 or more containers
       0 or more other elements

     Get a count of these elements:
       Count (1) if unitid is present
       Count (1) for each de-duped container
       Count (1) if any other element is present

     Output each row separately, as a flexbox, and give each a class name that
     includes the number of columns. If there is a <unitid>, output it. Then, for
     each <container>, output the type, followed by the contents of the node.
     Finally, put every other element in the right-most column along with a label
     for each element type.
-->

<!-- inventory -->
<xsl:template match="ead:dsc//ead:did">
  <xsl:variable name="column_count" select="number(
                                              boolean(
                                                count(
                                                  ead:unitid
                                                )
                                              )
                                            ) +
                                            count(ead:container) +
                                            number(
                                              boolean(
                                                count(
                                                  ead:abstract |
                                                  ead:container |
                                                  ead:dao |
                                                  ead:daogrp |
                                                  ead:head |
                                                  ead:langmaterial |
                                                  ead:materialspec |
                                                  ead:note |
                                                  ead:origination |
                                                  ead:physdesc |
                                                  ead:physloc |
                                                  ead:repository |
                                                  ead:unitdate |
                                                  ead:unittitle
                                                )
                                              )
                                            )"/>
  <div class="{concat('ead_did ead_did_', string($column_count))}">
    <xsl:apply-templates select="ead:unitid|ead:container"/>
    <div class="ead_did">
      <dl class="ead_did">
        <xsl:apply-templates select="@*|*[not(self::ead:unitid) and not(self::ead:container)]|text()"/>
      </dl>
    </div>
  </div>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]" priority="1.1">
  <div class="ead_did">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DIMENSIONS -->
<xsl:template match="ead:dimensions">
  <div class="ead_dimensions">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DIV -->
<xsl:template match="ead:div">
  <div class="ead_div">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DSC -->
<xsl:template match="ead:dsc">
  <div class="ead_dsc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- DSCGRP -->
<xsl:template match="ead:dscgrp">
  <div class="ead_dscgrp">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- EAD -->
<xsl:template match="ead:ead">
  <div class="ead_ead">
    <h1 class="ead_titleproper">
      <xsl:call-template name="trim_trailing_commas">
        <xsl:with-param name="text" select="/ead:ead[1]/ead:archdesc[1]/ead:did[1]/ead:unittitle[1]"/>
      </xsl:call-template>
    </h1>
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- EADGRP -->
<xsl:template match="ead:eadgrp">
  <div class="ead_eadgrp">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- EADHEADER -->
<xsl:template match="ead:eadheader"/>

<!-- EADID -->
<xsl:template match="ead:eadid"/>

<!-- EDITION -->
<!-- can be inline or block-level. -->
<xsl:template match="ead:edition">
  <span class="ead_edition">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="*[   self::ead:editionstmt 
                       or self::ead:titlepage  ]/ead:edition" priority="1.1">
  <div class="ead_edition">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- EDITIONSTMT -->
<xsl:template match="ead:editionstmt">
  <div class="ead_editionstmt">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- EMPH -->
<xsl:template match="ead:emph">
  <em class="ead_emph">
    <xsl:apply-templates select="@*|node()"/>
  </em>
</xsl:template>

<xsl:template match="ead:emph[@render = 'bold']" priority="1.1">
  <strong class="ead_emph ead_emph_bold">
    <xsl:apply-templates select="@*|node()"/>
  </strong>
</xsl:template>

<xsl:template match="ead:emph[@render = 'bolddoublequote']" priority="1.1">
  <strong class="ead_emph ead_emph_bolddoublequote">
    <xsl:apply-templates select="@*"/>
    “<xsl:apply-templates select="node()"/>”
  </strong>
</xsl:template>

<xsl:template match="ead:emph[@render = 'bolditalic']" priority="1.1">
  <strong class="ead_emph ead_emph_bolditalic">
    <em class="ead_emph ead_emph_bolditalic">
      <xsl:apply-templates select="@*|node()"/>
    </em>
  </strong>
</xsl:template>

<xsl:template match="ead:emph[@render = 'boldsinglequote']" priority="1.1">
  <strong class="ead_emph ead_emph_boldsinglequote">
    <xsl:apply-templates select="@*"/>
    ‘<xsl:apply-templates select="node()"/>’
  </strong>
</xsl:template>

<xsl:template match="ead:emph[@render = 'boldunderline']" priority="1.1">
  <strong class="ead_emph ead_emph_boldunderline">
    <u class="ead_emph ead_emph_boldunderline">
      <xsl:apply-templates select="@*|node()"/>
    </u>
  </strong>
</xsl:template>

<xsl:template match="ead:emph[@render = 'doublequote']" priority="1.1">
  <span class="ead_emph ead_emph_doublequote">
    <xsl:apply-templates select="@*"/>
    “<xsl:apply-templates select="node()"/>”
  </span>
</xsl:template>

<xsl:template match="ead:emph[@render = 'italic']" priority="1.1">
  <em class="ead_emph ead_emph_italic">
    <xsl:apply-templates select="@*|node()"/>
  </em>
</xsl:template>

<xsl:template match="ead:emph[@render = 'singlequote']" priority="1.1">
  <span class="ead_emph ead_emph_singlequote">
    <xsl:apply-templates select="@*"/>
    ‘<xsl:apply-templates select="node()"/>’
  </span>
</xsl:template>

<xsl:template match="ead:emph[@render = 'sub']" priority="1.1">
  <sub class="ead_emph ead_emph_sub">
    <xsl:apply-templates select="@*|node()"/>
  </sub>
</xsl:template>

<xsl:template match="ead:emph[@render = 'super']" priority="1.1">
  <sup class="ead_emph ead_emph_super">
    <xsl:apply-templates select="@*|node()"/>
  </sup>
</xsl:template>

<xsl:template match="ead:emph[@render = 'underline']" priority="1.1">
  <u class="ead_emph ead_emph_underline">
    <xsl:apply-templates select="@*|node()"/>
  </u>
</xsl:template>

<!-- ENTRY -->
<xsl:template match="ead:entry">
  <td class="ead_entry">
    <xsl:apply-templates select="@*|node()"/>
  </td>
</xsl:template>

<!-- EVENT -->
<xsl:template match="ead:event">
  <dd class="ead_event">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<!-- EVENTGRP -->
<xsl:template match="ead:eventgrp">
  <xsl:apply-templates select="@*|node()"/>
</xsl:template>

<!-- EXPAN -->
<xsl:template match="ead:expan">
  <span class="ead_expan">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:expan[@abbr]" priority="1.1">
  <abbr class="ead_expan" title="{@expan}">
    <xsl:apply-templates select="@*[name() != 'abbr']|node()"/>
  </abbr>
</xsl:template>

<!-- EXTENT -->
<xsl:template match="ead:extent">
  <span class="ead_extent">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- EXTPTR -->
<xsl:template match="ead:extptr[@href]">
  <a class="ead_extptr" href="{@href}">
    <xsl:choose>
      <xsl:when test="@title">
        <xsl:value-of select="@title"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@href"/>
      </xsl:otherwise>
    </xsl:choose>
  </a>
</xsl:template>

<!-- EXTPTRLOC -->
<xsl:template match="ead:extptrloc">
  <li class="ead_extptrloc">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- EXTREF -->
<xsl:template match="ead:extref[@href]">
  <a class="ead_extref" href="{@href}">
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<xsl:template match="ead:extref[@xlink:href]" priority="1.1">
  <a class="ead_extref" href="{@xlink:href}">
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- EXTREFLOC -->
<xsl:template match="ead:extrefloc[@href]">
  <a class="ead_extref" href="{@href}">
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<xsl:template match="ead:daogrp/ead:extrefloc[@href] | 
                     ead:linkgrp/ead:extrefloc[@href]" priority="1.1">
  <li class="ead_extref">
    <a class="ead_extref" href="{@href}">
      <xsl:apply-templates select="@*|node()"/>
    </a>
  </li>
</xsl:template>

<!-- FAMNAME -->
<xsl:template match="ead:famname">
  <span class="ead_famname">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:famname" priority="1.1">
  <li class="ead_famname">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- FILEDESC -->
<xsl:template match="ead:filedesc">
  <div class="ead_filedesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- FILEPLAN -->
<xsl:template match="ead:fileplan">
  <div class="ead_fileplan">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- FRONTMATTER -->
<xsl:template match="ead:frontmatter">
  <div class="ead_frontmatter">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- FUNCTION -->
<!-- usually outputs an inline element, unless parent is controlaccess, etc. -->
<xsl:template match="ead:function">
  <span class="ead_function"> 
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="*[   self::ead:controlaccess
                       or self::ead:indexentry   ]/ead:function" priority="1.1">
  <div class="ead_function"> 
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:namegrp/ead:function" priority="1.1">
  <li class="ead_function">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- GENREFORM -->
<!-- usually outputs an inline element, unless it is a child of namegrp, in
     which case it outputs an <li>, or controlaccess or indexentry, in which
     case it outputs a div. -->
<xsl:template match="ead:genreform">
  <span class="ead_genreform">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:genreform" priority="1.1">
  <li class="ead_genreform">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:controlaccess
                       or self::ead:indexentry   ]/ead:genreform" priority="1.1">
  <div class="ead_genreform">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- GEOGNAME
     outputs a span, unless the parent is ead:indexentry or ead:namegrp. -->
<xsl:template match="ead:geogname">
  <span class="ead_geogname">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:indexentry/ead:geogname" priority="1.1">
  <dt class="ead_geogname">
    <xsl:apply-templates select="@*|node()"/>
  </dt>
</xsl:template>

<xsl:template match="ead:namegrp/ead:geogname" priority="1.1">
  <li class="ead_geogname">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- HEAD -->
<xsl:template match="ead:head">
  <xsl:variable name="count">
    <xsl:value-of select="
      count(
        ancestor::ead:accessrestrict |
        ancestor::ead:accruals |
        ancestor::ead:acqinfo |
        ancestor::ead:altformavail |
        ancestor::ead:appraisal |
        ancestor::ead:arrangement |
        ancestor::ead:bibliography |
        ancestor::ead:bioghist |
        ancestor::ead:controlaccess |
        ancestor::ead:custodhist |
        ancestor::ead:descgrp |
        ancestor::ead:did |
        ancestor::ead:dsc |
        ancestor::ead:fileplan |
        ancestor::ead:index |
        ancestor::ead:note |
        ancestor::ead:odd |
        ancestor::ead:originalsloc |
        ancestor::ead:otherfindaid |
        ancestor::ead:phystech |
        ancestor::ead:prefercite |
        ancestor::ead:processinfo |
        ancestor::ead:relatedmaterial |
        ancestor::ead:scopecontent |
        ancestor::ead:separatedmaterial |
        ancestor::ead:userestrict
      )"/>
    </xsl:variable>
  <xsl:if test="$count &gt; 5">
     <xsl:message terminate="yes">ERROR: Elements are too deeply nested under archdesc.</xsl:message>
  </xsl:if>
  
  <xsl:element name="{concat('h', 1 + $count)}">
    <xsl:attribute name="class">ead_head</xsl:attribute>
    <xsl:attribute name="id">
      <xsl:call-template name="generate_readable_id"/>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:element>
</xsl:template>

<xsl:template match="ead:head[ancestor::ead:dsc and not(parent::ead:dsc)]">
  <div class="ead_head">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- HIGHLIGHT -->
<xsl:template match="ead:highlight">
  <span class="ead_highlight">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- IMPRINT -->
<xsl:template match="ead:imprint">
  <div class="ead_imprint">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ITEM -->
<xsl:template match="*[   self::ead:change
                       or self::ead:defitem]/ead:item">
  <dd class="ead_item">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<xsl:template match="ead:list/ead:item">
  <li class="ead_item">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- INDEX -->
<xsl:template match="ead:index">
  <div class="ead_index">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- INDEXENTRY -->
<xsl:template match="ead:indexentry">
  <xsl:apply-templates select="@*|node()"/>
</xsl:template>

<!-- LABEL -->
<xsl:template match="ead:label">
  <dt class="ead_label">
    <xsl:apply-templates select="@*|node()"/>
  </dt>
</xsl:template>

<!-- LANGMATERIAL -->
<xsl:template match="ead:langmaterial">
  <div class="ead_langmaterial">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- top of archival description or inventory -->
<xsl:template match="ead:archdesc/ead:did/ead:langmaterial |
                     ead:dsc//ead:did/ead:langmaterial" priority="1.1">
  
  <dt class="ead_langmaterial">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_langmaterial">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:langmaterial" priority="1.2">
  <div class="ead_langmaterial">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- LANGUAGE -->
<xsl:template match="ead:language">
  <span class="ead_language">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- LANGUSAGE -->
<xsl:template match="ead:langusage">
  <div class="ead_langusage">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- LB -->
<xsl:template match="ead:lb">
  <br class="ead_lb"/>
</xsl:template>

<!-- LEGALSTATUS -->
<xsl:template match="ead:legalstatus">
  <div class="ead_legalstatus">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- LINKGRP -->
<xsl:template match="ead:linkgrp">
  <ul class="ead_linkgrp">
    <xsl:apply-templates select="@*|node()"/>
  </ul>
</xsl:template>

<!-- LIST -->
<xsl:template match="ead:list">
  <xsl:apply-templates select="ead:head"/>
  <ul class="ead_list">
    <xsl:apply-templates select="@*|*[not(self::ead:head)]|text()"/>
  </ul>
</xsl:template>

<!-- LISTHEAD -->
<xsl:template match="ead:listhead">
  <div class="ead_listhead">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- MATERIALSPEC -->
<xsl:template match="ead:materialspec">
  <div class="ead_materialspec">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- inventory -->
<xsl:template match="ead:dsc//ead:did/ead:materialspec">
  <dt class="ead_materialspec">Material Specific Details</dt>
  <dd class="ead_materialspec">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:materialspec">
  <div class="ead_materialspec">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- NAME
     usually outputs a span, except when namegrp is the parent. -->
<xsl:template match="ead:name">
  <span class="ead_name">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:name">
  <li class="ead_name">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- NAMEGRP -->
<xsl:template match="ead:namegrp">
  <ul class="ead_namegrp">
    <xsl:apply-templates select="@*|node()"/>
  </ul>
</xsl:template>

<!-- NOTE -->
<!-- this element usually outputs a block level element, unless it is a child
     of namegrp, in which case it outputs an li, or archref, etc., in which
     case it outputs a span. -->
<xsl:template match="ead:note">
  <div class="ead_note">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:namegrp/ead:note" priority="1.1">
  <li class="ead_note">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:archref 
                       or self::ead:entry 
                       or self::ead:event
                       or self::ead:extrefloc
                       or self::ead:item
                       or self::ead:p
                       or self::ead:ref
                       or self::ead:refloc   ]/ead:note" priority="1.1">
  <span class="ead_note">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:note" priority="1.1">
  <div class="ead_note">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- inventory with container -->
<xsl:template match="ead:dsc//ead:did[ead:container]/ead:note" priority="1.1">
  <dt class="ead_note">Note</dt>
  <dd class="ead_note">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<!-- NOTESTMT -->
<xsl:template match="ead:notestmt">
  <div class="ead_notestmt">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- NUM -->
<xsl:template match="ead:num">
  <span class="ead_num">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- OCCUPATION 
     usually outputs a block-level element, unless the parent is a namegrp in
     which case it outputs an li. -->
<xsl:template match="ead:occupation">
  <span class="ead_occupation">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:occupation" priority="1.1">
  <li class="ead_occupation">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- ODD -->
<xsl:template match="ead:odd">
  <div class="ead_odd">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ORIGINALSLOC -->
<xsl:template match="ead:originalsloc">
  <div class="ead_originalsloc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ORIGINATION -->
<!-- usually outputs an inline element, unless it is a child of did. 
     special handling when this element occurs at the top of the archival
     description or in an inventory did with a container. -->
<xsl:template match="ead:origination">
  <span class="ead_origination">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:did/ead:origination" priority="1.1">
  <div class="ead_origination">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- top of archival description or inventory, w/ container -->
<xsl:template match="ead:archdesc/ead:did/ead:origination |
                     ead:dsc//ead:did[ead:container]/ead:origination" priority="1.2">
  <dt class="ead_origination">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_origination">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- OTHERFINDINGAID -->
<xsl:template match="ead:otherfindingaid">
  <div class="ead_otherfindingaid">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- P -->
<xsl:template match="ead:p">
  <p class="ead_p">
    <xsl:apply-templates select="@*|node()"/>
  </p>
</xsl:template>

<!-- PERSNAME
     usually outputs an inline element, except when namegrp is the parent. -->
<xsl:template match="ead:persname">
  <span class="ead_persname">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:persname" priority="1.1">
  <li class="ead_persname">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- PHYSDESC -->
<xsl:template match="ead:physdesc">
  <div class="ead_physdesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- top of archival description or inventory. note that in the top of the
     archival description, this element usually, but not always, contains an
     extent, although the label attribute is always on the physdesc. -->
<xsl:template match="ead:archdesc/ead:did/ead:physdesc |
                     ead:dsc//ead:did[ead:container]/ead:physdesc" priority="1.2">
  <dt class="ead_physdesc">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_physdesc">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:physdesc" priority="1.2">
  <div class="ead_physdesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PHYSFACET -->
<xsl:template match="ead:physfacet">
  <div class="ead_physfacet">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PHYSLOC -->
<xsl:template match="ead:physloc">
  <div class="ead_physloc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- top of archival description -->
<xsl:template match="ead:archdesc/ead:did/ead:physloc" priority="1.1">
  <dt class="ead_physloc">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_physloc">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory with container -->
<xsl:template match="ead:dsc//ead:did[ead:container]/ead:physloc" priority="1.2">
  <dt class="ead_physloc">Physical Location</dt>
  <dd class="ead_physloc">
    <xsl:apply-templates select="@*|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:physloc" priority="1.2">
  <div class="ead_physloc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PHYSTECH -->
<xsl:template match="ead:phystech">
  <div class="ead_phystech">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PREFERCITE -->
<xsl:template match="ead:prefercite">
  <div class="ead_prefercite">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PROCESSINFO -->
<xsl:template match="ead:processinfo">
  <div class="ead_processinfo">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PROFILEDESC -->
<xsl:template match="ead:profiledesc">
  <div class="ead_profiledesc">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PUBLICATIONSTMT -->
<xsl:template match="ead:publicationstmt">
  <div class="ead_publicationstmt">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PUBLISHER -->
<xsl:template match="ead:publisher">
  <div class="ead_publisher">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- PTR
     outputs an inline element, except when the child of ptrgrp. -->
<xsl:template match="ead:ptr">
  <span class="ead_ptr">
    <xsl:call-template name="ptr"/>
  </span>
</xsl:template>

<xsl:template match="ead:ptrgrp/ead:ptr" priority="1.1">
  <li class="ead_ptr">
    <xsl:call-template name="ptr"/>
  </li>
</xsl:template>

<xsl:template name="ptr">
  <a class="ead_ptr" href="{concat('#', @target)}">
    <xsl:apply-templates select="@*"/>
    <xsl:value-of select="@title"/>
  </a>
</xsl:template>

<!-- PTRGRP -->
<xsl:template match="ead:ptrgrp">
  <ul class="ead_ptrgrp">
    <xsl:apply-templates select="@*|node()"/>
  </ul>
</xsl:template>

<!-- PTRLOC -->
<xsl:template match="ead:ptrloc">
  <div class="ead_ptrloc" id="{@id}"/>
</xsl:template>

<!-- RELATEDMATERIAL -->
<xsl:template match="ead:relatedmaterial">
  <div class="ead_relatedmaterial">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- REPOSITORY -->
<!-- usually outputs an inline element, except when the child of a did. -->
<xsl:template match="ead:repository">
  <span class="ead_repository">j
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- top of archival description or in inventory, with container. -->
<xsl:template match="ead:archdesc/ead:did/ead:repository |
                     ead:dsc//ead:did[ead:container]/ead:repository" priority="1.1">
  <dt class="ead_repository">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_repository">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:repository" priority="1.2">
  <div class="ead_repository">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- REF -->
<xsl:template match="ead:ptrgrp/ead:ref">
  <li class="ead_ref">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- REFLOC -->
<xsl:template match="ead:refloc">
  <li class="ead_refloc">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- RESOURCE -->
<xsl:template match="ead:resource">
  <li class="ead_resource">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- REVISIONDESC -->
<xsl:template match="ead:revisiondesc">
  <dl class="ead_revisiondesc">
    <xsl:apply-templates select="@*|node()"/>
  </dl>
</xsl:template>

<!-- ROW -->
<xsl:template match="ead:row">
  <tr class="ead_row">
    <xsl:apply-templates select="@*|node()"/>
  </tr>
</xsl:template>

<!-- RUNNER -->
<xsl:template match="ead:runner"/>

<!-- SCOPECONTENT -->
<xsl:template match="ead:scopecontent">
  <div class="ead_scopecontent">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- SEPARATEDMATERIAL -->
<xsl:template match="ead:separatedmaterial">
  <div class="ead_separatedmaterial">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- SERIESSTMT -->
<xsl:template match="ead:seriesstmt">
  <div class="ead_seriesstmt">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- SPONSOR -->
<xsl:template match="ead:sponsor">
  <div class="ead_sponsor">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- SUBAREA -->
<xsl:template match="ead:subarea">
  <span class="ead_subarea">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- SUBJECT
     usually outputs an inline element, except when the child of ead:entry or
     ead:namegrp. -->
<xsl:template match="ead:subject">
  <span class="ead_subject">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:entry/ead:subject">
  <div class="ead_subject">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:namegrp/ead:subject">
  <li class="ead_subject">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<!-- SUBTITLE -->
<xsl:template match="ead:subtitle">
  <div class="ead_subtitle">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- TABLE -->
<xsl:template match="ead:table">
  <table class="ead_table">
    <xsl:apply-templates select="@*|node()"/>
  </table>
</xsl:template>

<!-- TBODY -->
<xsl:template match="ead:tbody">
  <tbody class="ead_table">
    <xsl:apply-templates select="@*|node()"/>
  </tbody>
</xsl:template>

<!-- TGROUP -->
<xsl:template match="ead:tgroup">
  <xsl:apply-templates select="@*|node()"/>
</xsl:template>

<!-- THEAD -->
<xsl:template match="ead:thead">
  <thead class="ead_thead">
    <xsl:apply-templates select="@*|node()"/>
  </thead>
</xsl:template>

<!-- TITLE
     usually outputs an inline element, unless the parent is bibliography, etc. -->
<xsl:template match="ead:title">
  <span class="ead_title">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:title" priority="1.1">
  <li class="ead_title">
    <xsl:apply-templates select="@*|node()"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:bibliography
                       or self::ead:controlaccess
                       or self::ead:indexentry
                       or self::ead:otherfindaid
                       or self::ead:relatedmaterial
                       or self::ead:separatedmaterial]/ead:title" priority="1.1">
  <div class="ead_title">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- TITLEPAGE -->
<xsl:template match="ead:titlepage">
  <div class="ead_titlepage">
    <xsl:apply-templates select="ead:titleproper"/>
  </div>
</xsl:template>

<!-- TITLEPROPER -->
<xsl:template match="ead:titleproper"/>

<!-- TITLESTMT -->
<xsl:template match="ead:titlestmt">
  <div class="ead_titlestmt">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- UNITDATE
     usually outputs an inline element, unless the parent is a did. -->
<xsl:template match="ead:unitdate">
  <span class="ead_unitdate">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- omit the label when unitdate is a child of unittitle. -->
<xsl:template match="ead:unittitle/ead:unitdate">
  <span class="ead_unitdate">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </span>
</xsl:template>

<!-- top of archival description, or inventory with container -->
<xsl:template match="ead:archdesc/ead:did/ead:unitdate |
                     ead:dsc//ead:did[ead:container]/ead:unitdate" priority="1.1">
  <dt class="ead_unitdate">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_unitdate">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:unitdate" priority="1.1">
  <div class="ead_unitdate">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- UNITID
     usually outputs an inline element, unless it is at the top of the archival
     description or in the inventory. -->
<xsl:template match="ead:unitid">
  <span class="ead_unitid">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- top of archival description -->
<xsl:template match="ead:archdesc/ead:did/ead:unitid |
                     ead:archdesc/ead:did[ead:container]/ead:unitid" priority="1.1">
  <dt class="ead_unitid">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_unitid">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory, or inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:unitid" priority="1.2">
  <div class="ead_unitid">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- UNITTITLE
     usually outputs an inline element, unless the parent is a did. -->
<xsl:template match="ead:unittitle">
  <span class="ead_unittitle">
    <xsl:apply-templates select="@*|node()"/>
  </span>
</xsl:template>

<!-- top of archival description or inventory, with container -->
<xsl:template match="ead:archdesc/ead:did/ead:unittitle |
                     ead:dsc//ead:did[ead:container]/ead:unittitle" priority="1.1">
  <dt class="ead_unittitle">
    <xsl:value-of select="@label"/>
  </dt>
  <dd class="ead_unittitle">
    <xsl:apply-templates select="@*[name() != 'label']|node()"/>
  </dd>
</xsl:template>

<!-- inventory without container -->
<xsl:template match="ead:dsc//ead:did[not(ead:container)]/ead:unittitle" priority="1.2">
  <div class="ead_unittitle">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- USERESTRICT -->
<xsl:template match="ead:userestrict">
  <div class="ead_userestrict">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- ****************************** -->
<!-- * PROJECT-SPECIFIC OVERRIDES * -->
<!-- ****************************** -->

<!-- CONTAINER
     Note:

     The vast majority of <container> elements use one of the following forms:
     <container type="Folder">3</container>
     <container type="othertype">drawer 4</container>

     Because of this, append the @type to the text output for all containers,
     except when a container has been specifically marked as "othertype". 
-->
<xsl:template match="ead:container" priority="2.0">
  <div class="ead_container">
    <xsl:apply-templates select="@*"/>
    <xsl:value-of select="concat(@type, ' ')"/> <xsl:apply-templates select="node()"/>
  </div>
</xsl:template>

<xsl:template match="ead:container[@type = 'Othertype']" priority="2.1">
  <div class="ead_container">
    <xsl:apply-templates select="@*|node()"/>
  </div>
</xsl:template>

<!-- CORPNAME
     When ead:corpname is a child of ead:controlaccess or ead:inventory,
     output a <div>. Output an <li> when it is a child of ead:namegrp.
     For all other parents, output a <span>. When this element is a
     child of publisher or repository output plain text, otherwise output
     a link back to the search interface. -->
<xsl:template match="ead:corpname" priority="2.0">
  <span class="ead_corpname">
    <xsl:choose>
      <xsl:when test="ancestor::ead:publisher or ancestor::ead:repository">
        <xsl:apply-templates select="@*|node()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="corpname"/>
      </xsl:otherwise>
    </xsl:choose>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:corpname" priority="2.1">
  <li class="ead_corpname">
    <xsl:choose>
      <xsl:when test="ancestor::ead:publisher or ancestor::ead:repository">
        <xsl:apply-templates select="@*|node()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates name="corpname"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:call-template name="corpname"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:controlaccess
                       or self::ead:indexentry   ]/ead:corpname" priority="2.1">
  <div class="ead_corpname">
    <xsl:choose>
      <xsl:when test="ancestor::ead:publisher or ancestor::ead:repository">
        <xsl:apply-templates select="@*|node()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates name="corpname"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:call-template name="corpname"/>
  </div>
</xsl:template>

<xsl:template name="corpname">
  <a class="ead_corpname">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/organizations/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- FAMNAME -->
<xsl:template match="ead:famname" priority="2.0">
  <span class="ead_famname">
    <xsl:call-template name="famname"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:famname" priority="2.1">
  <li class="ead_famname">
    <xsl:call-template name="famname"/>
  </li>
</xsl:template>

<xsl:template name="famname">
  <a class="ead_famname">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/people/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- GENREFORM -->
<!-- usually outputs an inline element, unless it is a child of namegrp, in
     which case it outputs an <li>, or controlaccess or indexentry, in which
     case it outputs a div. -->
<xsl:template match="ead:genreform" priority="2.0">
  <span class="ead_genreform">
    <xsl:call-template name="genreform"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:genreform" priority="2.1">
  <li class="ead_genreform">
    <xsl:call-template name="genreform"/>
  </li>
</xsl:template>

<xsl:template match="*[   self::ead:controlaccess
                       or self::ead:indexentry   ]/ead:genreform" priority="2.1">
  <div class="ead_genreform">
    <xsl:call-template name="genreform"/>
  </div>
</xsl:template>

<xsl:template name="genreform">
  <a class="ead_genreform">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/topics/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- GEOGNAME
     outputs a span, unless the parent is ead:indexentry or ead:namegrp. -->
<xsl:template match="ead:geogname" priority="2.0">
  <span class="ead_geogname">
    <xsl:call-template name="geogname"/>
  </span>
</xsl:template>

<xsl:template match="ead:indexentry/ead:geogname" priority="2.1">
  <dt class="ead_geogname">
    <xsl:call-template name="geogname"/>
  </dt>
</xsl:template>

<xsl:template match="ead:namegrp/ead:geogname" priority="2.1">
  <li class="ead_geogname">
    <xsl:call-template name="geogname"/>
  </li>
</xsl:template>

<xsl:template name="geogname">
  <a class="ead_geogname">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/places/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- NAME
     usually outputs a span, except when namegrp is the parent. -->
<xsl:template match="ead:name" priority="2.0">
  <span class="ead_name">
    <xsl:call-template name="name"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:name" priority="2.1">
  <li class="ead_name">
    <xsl:call-template name="name"/>
  </li>
</xsl:template>

<xsl:template name="name">
  <a class="ead_name">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/people/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- OCCUPATION 
     usually outputs a block-level element, unless the parent is a namegrp in
     which case it outputs an li. -->
<xsl:template match="ead:occupation" priority="2.0">
  <span class="ead_occupation">
    <xsl:call-template name="occupation"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:occupation" priority="2.1">
  <li class="ead_occupation">
    <xsl:call-template name="occupation"/>
  </li>
</xsl:template>

<xsl:template name="occupation">
  <a class="ead_occupation">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/topics/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- PERSNAME
     usually outputs an inline element, except when namegrp is the parent. -->
<xsl:template match="ead:persname" priority="2.0">
  <span class="ead_persname">
    <xsl:call-template name="persname"/>
  </span>
</xsl:template>

<xsl:template match="ead:namegrp/ead:persname" priority="2.1">
  <li class="ead_persname">
    <xsl:call-template name="persname"/>
  </li>
</xsl:template>

<xsl:template name="persname">
  <a class="ead_persname">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/people/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- SUBJECT
     usually outputs an inline element, except when the child of ead:entry or
     ead:namegrp. -->
<xsl:template match="ead:subject" priority="2.0">
  <span class="ead_subject">
    <xsl:call-template name="subject"/>
  </span>
</xsl:template>

<xsl:template match="ead:entry/ead:subject" priority="2.1">
  <div class="ead_subject">
    <xsl:call-template name="subject"/>
  </div>
</xsl:template>

<xsl:template match="ead:namegrp/ead:subject" priority="2.1">
  <li class="ead_subject">
    <xsl:call-template name="subject"/>
  </li>
</xsl:template>

<xsl:template name="subject">
  <a class="ead_subject">
    <xsl:attribute name="href">
      <xsl:call-template name="build_search_link">
        <xsl:with-param name="ns" select="'https://bmrc.lib.uchicago.edu/topics/'"/>
        <xsl:with-param name="s" select="string(.)"/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="@*|node()"/>
  </a>
</xsl:template>

<!-- BUILD SEARCH LINKS -->
<xsl:template name="build_search_link">
  <xsl:param name="ns"/>
  <xsl:param name="s"/>
  <xsl:value-of select="ucf:bmrc_search_url(
    $ns,
    normalize-space($s)
  )"/>
</xsl:template>

<!-- GENERATE READABLE IDS -->
<xsl:template name="generate_readable_id">
  <!-- this template can be called from either an @label attribute, or a <head>
       element. In either case, we want to use the parent element to name the
       anchor. Either the direct parent of the attribute, or the parent of the
       <head>. -->
  <xsl:variable name="name">
    <xsl:value-of select="local-name(..)"/>
  </xsl:variable>

  <!-- same for counting preceding elements. If the current context is an element 
       (a <head>) count backwards from the parent, but also count backwards from 
       the parent if the current context is an @label attribute. -->
  <xsl:variable name="count">
    <xsl:value-of select="count(../preceding::*[local-name() = $name])"/>
  </xsl:variable>

  <!-- produce IDs like "scopecontent", "scopecontent-2", etc. -->
  <xsl:variable name="id">
    <xsl:choose>
      <xsl:when test="$count &gt; 0">
        <xsl:value-of select="concat($name, '-', $count + 1)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$name"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:value-of select="$id"/>
</xsl:template>

<!-- TRIM TRAILING COMMAS -->
<xsl:template name="trim_trailing_commas">
  <xsl:param name="text"/>
  <xsl:variable name="s" select="normalize-space($text)"/>
  <xsl:choose>
    <xsl:when test="substring($s, string-length($s)) = ','">
        <xsl:value-of select="substring($s, 1, string-length($s) - 1)"/>
    </xsl:when>
    <xsl:otherwise>
        <xsl:value-of select="$s"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
