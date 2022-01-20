<?xml version="1.0"?>

<xsl:stylesheet 
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output omit-xml-declaration="yes"/>

<xsl:template match="/">
  <ul>
    <xsl:apply-templates select="//h2"/>
  </ul>
</xsl:template>

<xsl:template match="h2">
  <li>
    <a href="{concat('#', @id)}">
      <xsl:value-of select="."/>
    </a>
    <xsl:if test="following::h3[preceding::h2[1] = current()]">
      <ul>
        <xsl:apply-templates select="following::h3[preceding::h2[1] = current()]"/>
      </ul>
    </xsl:if>
  </li>
</xsl:template>

<xsl:template match="h3">
  <li>
    <a href="{concat('#', @id)}">
      <xsl:value-of select="."/>
    </a>
    <xsl:if test="following::h4[preceding::h3[1] = current()]">
      <ul>
        <xsl:apply-templates select="following::h4[preceding::h3[1] = current()]"/>
      </ul>
    </xsl:if>
  </li>
</xsl:template>

<xsl:template match="h4">
  <li>
    <a href="{concat('#', @id)}">
      <xsl:value-of select="."/>
    </a>
    <xsl:if test="following::h5[preceding::h4[1] = current()]">
      <ul>
        <xsl:apply-templates select="following::h5[preceding::h4[1] = current()]"/>
      </ul>
    </xsl:if>
  </li>
</xsl:template>

<xsl:template match="h5">
  <li>
    <a href="{concat('#', @id)}">
      <xsl:value-of select="."/>
    </a>
    <xsl:if test="following::h6[preceding::h5[1] = current()]">
      <ul>
        <xsl:apply-templates select="following::h6[preceding::h5[1] = current()]"/>
      </ul>
    </xsl:if>
  </li>
</xsl:template>

<xsl:template match="h6">
  <li>
    <a href="{concat('#', @id)}">
      <xsl:value-of select="."/>
    </a>
  </li>
</xsl:template>

</xsl:stylesheet>
