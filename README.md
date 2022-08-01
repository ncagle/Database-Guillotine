# Database Guillotine

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
    <img src="images/guillotine_small.jpg" alt="Logo" width="100" height="100">
  </a>

<h1 align="center">Database Guillotine</h1>

  <p align="center">
    An ArcPy tool that splits a dataset based on an 
    custom queries, AOI polygons, specific feature classes, and more.
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

The Database Guillotine is used to extract or split TDS datasets. You can split a local dataset or a connected SDE dataset. The tool can either create a new GDB and clone the source schema, or use an existing blank GDB with a schema that matches the source. The data can be extracted based on the full extent of the dataset or with a user created AOI. The AOI must be merged into one polygon (multiparts are allowed). By default, the Extract Scale option has a drop-down list of CTUU values to choose from. The tool will extract all data with a CTUU greater than or equal to the chosen value. All options can be used in combination with each other.

In the Advanced Options section, a custom query can be used to extract data. Choosing this option will cancel out the Extract Scale option above. The Custom Query field has a button to access the Query Builder interface for constructing your query. In order to view field names in the Query Builder, you must first choose a feature class from the Field Name Reference drop-down. The Query Builder references the chosen feature class to make the list of field names shown in the interface. Different feature classes have different fields, but many of them overlap. You can use any feature class to find the CTUU field, but only TransportationGroundCrvs will have the RIN_ROI field. TransportationGroundCrvs is a good option for the most common field names.

The next advanced option is to Extract Specific Feature Classes. Once the dataset input is added, the Feature Class List for this option will populate with all the available feature classes. They are all checked by default. You can uncheck specific feature classes you do not want extracted, such as StructurePnt/StructureSrf. Or you can unselect all of them at once and then check only a few feature classes. Be aware that the output database will still have all the feature classes in the dataset, but if they were not extracted, there won't be any features in them.

[![Toolbox Screen Shot][tool-screenshot]


<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

### Built With

[![Python 2.7][Python]][Python-url]

[![made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

<p align="right">(<a href="#top">back to top</a>)</p>



### Prerequisites

* ArcMap Desktop 10.5+
* Python 2.7



### Installation

1. Download the ArcGIS Toolbox (.tbx)
2. In ArcMap or ArcCatalog, open the toolbox and double click "Database Guillotine"

<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

<p align="right">(<a href="#top">back to top</a>)</p>

____________________________________________________________

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/ncagle/Database-Guillotine](github.com/ncagle/Database-Guillotine)

[![LinkedIn][linkedin-shield]][linkedin-url]

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* J. Jackson [https://github.com/adab5urdum](github.com/adab5urdum)

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
[license-url]: https://github.com/ncagle/Database-Guillotine/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/ncagle/
[tool-screenshot]: images/toolbox_v1_6.png
[tool-logo]: images/guillotine_small.jpg
[Python]: https://img.shields.io/badge/python-2.7-blue?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/ 
