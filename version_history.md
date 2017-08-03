**v1.0**

* Began use of Bagit for LiPD archives

* `paleoData`
  * Support for multiple entries

* `chronData`
  * Support for multiple entries

**v1.1**

* Root
  * Added `lipdVersion` key

* `paleoData`
  * No changes

* `chronData`
  * Support for nested tables within each entry
   * `chronMeasurementTable`
      * Equivalent to the tables found in v1.0
   * `chronModel`
         * Support for multiple entries
	     * `method`
	           * Single entry
	           * How the model was created
	     * `chronModelTable`
	           * Single entry 
	     * `ensembleTable`
	           * Single entry
	     * `calibratedAges`
	           *  Multiple entries
	  

**v1.2**

* Root
  * Added `WDCPaleoUrl` key
*  `paleoData`
	* Redesigned to match the structure of `chronData` from v1.1
	* Support for nested tables within each entry
	* `paleoMeasurementTable`
		* Equivalent to tables found in v1.0 & v1.1
	* `paleoModel`
		* Support for multiple entries
	     * `method`
	           * Single entry
	           * How the model was created
	     * `paleoModelTable`
	           * Single entry 
	     * `ensembleTable`
	           * Single entry
	     * `distributionTable`
	           *  Multiple entries

* `chronData`
	* `calibratedAges` is now named `distributionTable`

**v1.3**

* Changes to LiPD archive
	* `.jsonld` file is now generically named `metadata.jsonld` (Previously used:  `<datasetname>.jsonld` )
	* Top-level folder inside LiPD archive is named `bag`. (Previoudly used: `<datasetname>`)
* Root
	* Added `createdBy` key
* `paleoData` & `chronData`
	* `paleo` and `chron` prefixes are removed from metadata keys (i.e. `paleoMeasurementTable` and `chronMeasurementTable` each become `measurementTable`)
	* `interpretation`
		*  interpretation key replaces `isotopeInterpretation` and `climateInterpretation` keys.  Data is merged.
	* `model`
		* `summaryTable`
			* Support for multiple entries
		* `ensembleTable`
			* Support for multiple entries