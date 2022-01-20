<?xml version="1.0"?>
<xsl:stylesheet 
  version="1.0" 
  xmlns:search="http://marklogic.com/appservices/search"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="xml"/>

<xsl:template match="search:response">
  <p>
    Result 
    <xsl:value-of select="@start"/> 
    to
    <xsl:value-of select="@start + @page-length - 1"/> 
    of
    <xsl:value-of select="@total"/>.
    <xsl:if test="@start &gt; 1">
      <a>
        <xsl:attribute name="href">
          <xsl:value-of select="concat(
            '/search/?q=',
            '',
            '&amp;start=',
            @start - @page-length)"/>
        </xsl:attribute>
        Previous
      </a>
      &#160;
    </xsl:if>
    <xsl:if test="@start + @page-length - 1 &lt; @total">
      <a>
        <xsl:attribute name="href">
          <xsl:value-of select="concat(
            '/search/?q=',
            '',
            '&amp;start=',
            @start + @page-length)"/>
        </xsl:attribute>
        Next
      </a>
    </xsl:if>
  </p>
  <ol>
    <xsl:attribute name="start">
      <xsl:value-of select="@start"/>
    </xsl:attribute>
    <xsl:apply-templates/>
  </ol>
</xsl:template>

<xsl:template match="search:result">
  <li>
    <xsl:value-of select="@uri"/><br/>
    INSTITUTION<br/>
    TITLE<br/>
    DATES<br/>
    ABSTRACT<br/>
    SUBJECTS<br/>
    NAMES<br/>
    TOPICS<br/>
    PLACES<br/>
    LOGO
  </li>
</xsl:template>

</xsl:stylesheet>
