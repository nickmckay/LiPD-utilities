**v1.0**

* Began use of Bagit for LiPD archives

* `paleoData`
  * Supports multiple entries

* `chronData`
  * Supports multiple entries

**v1.1**

* Root
  * Added `lipdVersion` key

* `paleoData`
  * No changes

* `chronData`
  * Support for nested tables within each entry
    * `chronMeasurementTable`
       * Supports one entry
       * Equivalent to the tables found in v1.0
    * `chronModel`
         * Supports multiple entries
	        * `method`
	           * Supports one entry
	           * How the model was created
	        * `chronModelTable`
	           * Supports one entry
	        * `ensembleTable`
	           * Supports one entry
	        * `calibratedAges`
	           * Supports multiple entries
	  

**v1.2**

* Root
  * Added `WDCPaleoUrl` key
* Resolution and Inferred data
   * Added `hasMean` key
   * Added `hasMedian` key
   * Added `hasMax` key
   * Added `hasMin` key
   * Added `hasResolution` key
*  `paleoData`
	* Redesigned to match the structure of `chronData` from v1.1
	* Support for nested tables within each entry
	* `paleoMeasurementTable`
		* Supports multiple entries
		* Equivalent to tables found in v1.0 & v1.1
	* `paleoModel`
		* Supports multiple entries
	        * `method`
	            * Supports one entry
	            * How the model was created
	        * `summaryTable`
	            * Supports one entry 
	        * `ensembleTable`
	            * Supports one entry
	        * `distributionTable`
	            * Supports multiple entries

* `chronData`
	* `calibratedAges` is now named `distributionTable`
	* `chronModelTable` is now named `summaryTable`

**v1.3**

* Changes to LiPD archive
	* `.jsonld` file is now generically named `metadata.jsonld` (Previously used:  `<datasetname>.jsonld` )
	* Top-level folder inside LiPD archive is named `bag`. (Previoudly used: `<datasetname>`)
* Root
	* Added `createdBy` key
* `paleoData` & `chronData`
	* `paleo` and `chron` prefixes are removed from metadata keys
		* `paleoMeasurementTable` & `chronMeasurementTable` become `measurementTable`
		* `paleoModel` & `chronModel` become `model`
	* All table name keys are removed in favor of `tableName`
		* Added `tableName` key
		* Removed `paleoDataTableName` & `chronDataTableName`
		* Removed `paleoMeasurementTableName` & `chronMeasurementTableName`
		* < There quite a few variations, so I will not list them all >
	* `interpretation`
		* Supports multiple entries
		*  interpretation key replaces `isotopeInterpretation` and `climateInterpretation` keys.  Data is merged.
	* `model`
		* `summaryTable`
			* Supports multiple entries
		* `ensembleTable`
			* Supports multiple entries
