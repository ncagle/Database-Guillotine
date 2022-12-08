<div id="top"></div>
<!--
comment block
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ncagle/Database-Guillotine">
    <img src="images/guillotine_small.png" alt="Logo" width="150" height="176">
  </a>

  <h1 align="center">
    Database Guillotine
    <br/>
    <sub>by Nat Cagle</sub>
  </h1>

  <p align="center">
    An ArcGIS python script tool that extracts, splits, or dataloads a dataset<br>
    based on custom queries, AOI polygons, or specific feature classes.
    <br />
    <a href="https://github.com/github_username/repo_name/issues">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#installation">Installation</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li>
      <a href="#roadmap">Roadmap</a>
      <ul>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li>
      <a href="#contact">Contact</a>
      <ul>
        <li><a href="#license">License</a></li>
        <li><a href="#acknowledgments">Acknowledgments</a></li>
      </ul>
    </li>
  </ol>
</details>

____________________________________________________________

<!-- ABOUT THE PROJECT -->
## About The Project

The Database Guillotine is used to extract, split, or dataload TDS datasets. You can split a local dataset or a connected SDE dataset. The tool can create a new GDB and clone the source schema, or dataload the source into a GDB that already has data or an empty GDB. The schemas must match to do this. The data can be extracted based on the full extent of the dataset or with a user created AOI. The AOI must be merged into one polygon (multiparts are allowed). By default, the Extract Scale option has a drop-down list of CTUU values to choose from. The tool will extract all data with a CTUU greater than or equal to the chosen value. All options can be used in combination with each other.

In the Advanced Options section, a custom query can be used to extract data. Choosing this option will cancel out the Extract Scale option above. The Custom Query field has a button to access the Query Builder interface for constructing your query. In order to view field names in the Query Builder, you must first choose a feature class from the Field Name Reference drop-down. The Query Builder references the chosen feature class to make the list of field names shown in the interface. Different feature classes have different fields, but many of them overlap. You can use any feature class to find the CTUU field, but only TransportationGroundCrvs will have the RIN_ROI field. TransportationGroundCrvs is a good option for the most common field names.

The next advanced option is to Extract Specific Feature Classes. Once the dataset input is added, the Feature Class List for this option will populate with all the available feature classes. They are all checked by default. You can uncheck specific feature classes you do not want extracted, such as StructurePnt/StructureSrf. Or you can unselect all of them at once and then check only a few feature classes. Be aware that the output database will still have all the feature classes in the dataset, but if they were not extracted, there won't be any features in them.

<br/>

![Toolbox Screen Shot][tool-screenshot]

<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

### Built With

[![Python 2.7][Python]][Python-url]



### Prerequisites

* ArcMap Desktop 10.5+
* Python 2.7



### Installation

1. Download the `Database Guillotine vX.tbx` ArcGIS Toolbox
2. In ArcMap or ArcCatalog, open the toolbox and double click "Database Guillotine"

<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

<!-- ROADMAP -->
## Roadmap

- [ ] Clone source dataset schema
    - [ ] Output GDB name & destination folder
- [ ] Dataload source into existing data or blank GDB
- [ ] Split with AOI polygon
    - [ ] Use full extent of data instead of AOI
    - [ ] Provide a merged AOI polygon
- [ ] Extract by SQL query
    - [ ] Extract Cartographic Scale
    - [ ] Extract data using custom query
    - [ ] Choose feature class to reference for field names
- [ ] Extract specific feature classes
    - [ ] Feature class checklist to include or exclude
- [ ] Mystery Parameter

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

**Create new GDB and clone source schema**
> This will create a new GDB in the chosen folder and clone the schema from the source dataset. This ensures that all the features being extracted match the source they are coming from.

<br/>

**Name for Split GDB**
> Give your new pet database a cute name!
> 
> The name cannot contain spaces and you don't need to add ".gdb" to the end. If you do add .gdb or have spaces in the name, the tool will automatically correct it. Feel free to try all you like; your efforts will be in vain.

<br/>

**Destination folder for split GDB**
> Choose the folder location where the new GDB will be created.

<br/>

**Dataload into existing data or empty GDB**
> Instead of creating a new GDB, source features can be dataloaded into a provided GDB with a matching schema. This can replace the ArcCatalog Data Loader tool and its various Cross-Reference databases.
> 
> If the provided GDB is empty, only the extracted source features will appear in the GDB when the tool is finished.
> 
> If the provided GDB already has existing features, then the extracted source features will be dataloaded together with existing features.


<br/>

**Use Full Extent**
> This option forgoes using an AOI polygon and just pulls all the data (still following the queries below).
> 
> This can be used if you want to pull an entire SDE dataset local for final finishing and delivery.

<br/>

**AOI**
> This is the AOI that will be used to split the data when extracting. The polygon provided must be merged into one feature. If the AOI you are extracting is not contiguous, still merge the polygons into one multipart feature.
> 
> All features that cross this AOI boundary will be split at the edge, retaining their attribution. Any multipart features created as a result of this process are exploded as part of the tool.

<br/>

**Extract Scale**
> Choose a scale value from the drop-down. The tool will extract data that has a CTUU value greater than or equal to the chosen value.
>
> If you wish to only extract data equal to one specific CTUU value or data that is less than a certain CTUU value, use the Custom Query in Advanced Options.

<br/>

**Extract data using custom query**
> _Advanced Option_
> 
> This will search the source dataset for any features with attributes that match the provided query. All features that meet the criteria will be extracted.

<br/>

**Field Name Reference**
> _Advanced Option_
> 
> In order to view field names in the Query Builder, you must first choose a feature class from the Field Name Reference drop-down. The Query Builder references the chosen feature class to make the list of field names shown in the interface.
> 
> Different feature classes have different fields, but many of them overlap. You can use any feature class to find the CTUU field, but only TransportationGroundCrv will have the RIN_ROI field. TransportationGroundCrv is a good option for the most common field names. If you want to find the HGT field in the Query Builder, you can select any feature class with that field as a reference, such as UtilityInfrastructurePnt.

<br/>

**Custom Query**
> _Advanced Option_
> 
> Here you can write a custom SQL query that be used to filter the data being extracted from the source. Choosing this option will cancel out the Extract Scale option above. The Custom Query field has a button to access the Query Builder interface for constructing your query. In order to view the fields in the Query Builder, you must first choose a feature class from the Field Name Reference drop-down. The Query Builder references the chosen feature class to make the list of fields shown in the interface.

<br/>

**Extract Specific Feature Classes**
> _Advanced Option_
> 
> This allows you to specify any feature classes you would like to include or exclude when extracting data from the source.

<br/>

**Feature Class List**
> _Advanced Option_
> 
> Once the dataset input is added, this list will populate with all the available feature classes. They are all checked by default.
> 
> You can uncheck specific feature classes you do not want extracted, such as StructurePnt/StructureSrf. Or you can unselect all of them at once and then check only a few feature classes.
> 
> Note: The output database will still have all the feature classes in the dataset, but the feature classes selected in this list are the only ones that will have data extracted. If a feature class was unchecked from this list, the feature class in the output will be empty.

<br/>

**What is it for? Nobody knows**
> _Super Secret Parameter_
> 
> How mysterious!
> 
> What does it mean?
> 
> Why are ArcMap's internal workings so mischievously convoluted?!

<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.



<!-- CONTACT -->
## Contact

Project Link - <a href="https://github.com/ncagle/Database-Guillotine">Database Guillotine</a>

Nat Cagle - <a href="https://github.com/ncagle">github.com/ncagle</a>

[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* John Jackson - <a href="https://github.com/adab5urdum">github.com/adab5urdum</a>
* Guillotine Logo Image by <a href="https://www.vectorportal.com">Vectorportal.com</a>,  <a class="external text" href="https://creativecommons.org/licenses/by/4.0/" >CC BY</a>

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ncagle/Database-Guillotine.svg?style=for-the-badge
[contributors-url]: https://github.com/ncagle/Database-Guillotine/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ncagle/Database-Guillotine.svg?style=for-the-badge
[forks-url]: https://github.com/ncagle/Database-Guillotine/network/members
[stars-shield]: https://img.shields.io/github/stars/ncagle/Database-Guillotine.svg?style=for-the-badge
[stars-url]: https://github.com/ncagle/Database-Guillotine/stargazers
[issues-shield]: https://img.shields.io/github/issues/ncagle/Database-Guillotine.svg?style=for-the-badge
[issues-url]: https://github.com/ncagle/Database-Guillotine/issues
[license-shield]: https://img.shields.io/github/license/ncagle/Database-Guillotine.svg?style=for-the-badge
[license-url]: https://github.com/ncagle/Database-Guillotine/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/ncagle/
[tool-screenshot]: images/toolbox_v1_7.png
[tool-logo]: images/guillotine_small.jpg
[Python]: https://img.shields.io/badge/python-2.7-blue?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/ 
